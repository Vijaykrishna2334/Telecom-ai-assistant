"""
Real-time voice gateway implementing the full voice conversation pipeline.

Architecture:
Browser ↔ WebSocket ↔ Gateway ↔ VAD/STT/LLM/TTS Pipeline

Features:
- Continuous audio streaming with VAD
- Real-time STT with partial transcripts
- LLM streaming with sentence splitting
- Parallel TTS jobs for low latency
- Barge-in detection to interrupt bot
"""
import asyncio
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from collections import deque
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.logging import get_logger
from app.services.llm import create_voice_prompt, ollama_client
from app.services.voice import voice_pipeline

logger = get_logger(__name__)
router = APIRouter()


class ConversationState(Enum):
    """State of the voice conversation."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    BOT_SPEAKING = "bot_speaking"


@dataclass
class VoiceSession:
    """Manages state for a voice session."""
    session_id: str
    websocket: WebSocket
    state: ConversationState = ConversationState.IDLE
    audio_buffer: bytes = b""
    is_speech_active: bool = False
    speech_start_time: float = 0
    silence_start_time: float = 0
    pending_tts_tasks: List[asyncio.Task] = field(default_factory=list)
    audio_queue: deque = field(default_factory=deque)
    current_transcript: str = ""
    barge_in_detected: bool = False
    history: List[Dict[str, str]] = field(default_factory=list)
    cancel_event: asyncio.Event = field(default_factory=asyncio.Event)
    
    def __post_init__(self):
        self.cancel_event = asyncio.Event()


class RealTimeVoiceGateway:
    """
    Real-time voice conversation gateway.
    
    Handles the full pipeline:
    1. Audio streaming from browser
    2. VAD for speech detection
    3. STT streaming with partial results
    4. LLM streaming with sentence splitting
    5. Parallel TTS processing
    6. Audio streaming back to browser
    7. Barge-in detection
    """
    
    # Configuration
    SILENCE_TIMEOUT_MS = 1500  # 1.5 seconds of silence before processing
    MIN_SPEECH_DURATION_MS = 250  # Minimum speech duration
    SAMPLE_RATE = 16000  # 16kHz audio
    CHUNK_SIZE = 512  # Audio chunk size in bytes
    
    def __init__(self):
        self.sessions: Dict[str, VoiceSession] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str) -> VoiceSession:
        """Connect a new voice client."""
        await websocket.accept()
        session = VoiceSession(session_id=session_id, websocket=websocket)
        self.sessions[session_id] = session
        
        logger.info("Voice session connected", session_id=session_id)
        
        # Send welcome message
        await self.send_event(session, "connected", {
            "message": "Voice session ready",
            "sample_rate": self.SAMPLE_RATE
        })
        
        # Proactive greeting: Bot starts the conversation
        await self._send_greeting(session)
        
        return session
    
    def disconnect(self, session_id: str):
        """Disconnect a voice client."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            # Cancel any pending tasks
            session.cancel_event.set()
            for task in session.pending_tts_tasks:
                task.cancel()
            del self.sessions[session_id]
            logger.info("Voice session disconnected", session_id=session_id)
    
    async def send_event(self, session: VoiceSession, event_type: str, data: dict = None):
        """Send a JSON event to the client."""
        message = {"type": event_type}
        if data:
            message.update(data)
        try:
            await session.websocket.send_json(message)
        except Exception as e:
            logger.error("Failed to send event", error=str(e))
    
    async def send_audio(self, session: VoiceSession, audio_data: bytes):
        """Send audio data to the client."""
        try:
            await session.websocket.send_bytes(audio_data)
        except Exception as e:
            logger.error("Failed to send audio", error=str(e))
    
    async def process_audio_chunk(self, session: VoiceSession, audio_chunk: bytes):
        """
        Process an incoming audio chunk.
        
        This implements the VAD logic:
        1. Detect speech start
        2. Accumulate audio during speech
        3. Detect silence timeout
        4. Trigger processing when speech ends
        """
        current_time = time.time() * 1000  # ms
        
        # Add to buffer
        session.audio_buffer += audio_chunk
        
        # Run VAD on the chunk
        is_speech = await self._detect_speech(audio_chunk)
        
        if is_speech:
            if not session.is_speech_active:
                # INFO: Log current state
                logger.info(
                    "🎙️ Speech detected in chunk",
                    session_id=session.session_id,
                    current_state=session.state.value,
                    is_bot_speaking=(session.state == ConversationState.BOT_SPEAKING)
                )
                
                # Check for barge-in BEFORE changing state
                if session.state == ConversationState.BOT_SPEAKING:
                    logger.warning("🚨 TRIGGERING BARGE-IN NOW 🚨", session_id=session.session_id)
                    await self._handle_barge_in(session)
                
                # Speech just started
                session.is_speech_active = True
                session.speech_start_time = current_time
                session.state = ConversationState.LISTENING
                
                await self.send_event(session, "speech_start")
                logger.info("Speech started", session_id=session.session_id)
            
            session.silence_start_time = 0
            
        else:
            if session.is_speech_active:
                if session.silence_start_time == 0:
                    session.silence_start_time = current_time
                
                silence_duration = current_time - session.silence_start_time
                
                if silence_duration >= self.SILENCE_TIMEOUT_MS:
                    # Silence timeout reached - process the speech
                    speech_duration = current_time - session.speech_start_time
                    
                    if speech_duration >= self.MIN_SPEECH_DURATION_MS:
                        await self.send_event(session, "speech_end")
                        logger.info("Speech ended", 
                                   session_id=session.session_id,
                                   duration_ms=speech_duration)
                        
                        # Process the accumulated audio
                        await self._process_speech(session)
                    
                    # Reset state
                    session.is_speech_active = False
                    session.audio_buffer = b""
                    session.silence_start_time = 0
    
    async def _detect_speech(self, audio_chunk: bytes) -> bool:
        """Detect speech using VAD."""
        try:
            # Use the voice pipeline's VAD
            return await voice_pipeline.detect_speech(audio_chunk)
        except Exception:
            # If VAD fails, assume speech
            return len(audio_chunk) > 0
    
    async def _handle_barge_in(self, session: VoiceSession):
        """Handle barge-in (user interrupts bot)."""
        logger.info("🔴 BARGE-IN DETECTED 🔴", session_id=session.session_id, current_state=session.state.value)
        session.barge_in_detected = True
        session.cancel_event.set()
        
        # Cancel all pending TTS tasks
        for task in session.pending_tts_tasks:
            task.cancel()
        session.pending_tts_tasks.clear()
        
        # Clear audio queue
        session.audio_queue.clear()
        
        # Notify client to stop audio playback
        await self.send_event(session, "stop_audio", {
            "reason": "barge_in"
        })
        
        # Reset state to LISTENING immediately
        session.state = ConversationState.LISTENING
        session.cancel_event.clear()
        
        logger.info("Barge-in handled, state reset to LISTENING", session_id=session.session_id)
    
    async def _process_speech(self, session: VoiceSession):
        """Process accumulated speech audio."""
        session.state = ConversationState.PROCESSING
        audio_data = session.audio_buffer
        
        try:
            # Step 1: Transcribe audio (STT)
            await self.send_event(session, "processing", {"stage": "transcribing"})
            transcript = await voice_pipeline.process_audio_input(audio_data)
            
            if not transcript:
                await self.send_event(session, "error", {"message": "Could not transcribe audio"})
                session.state = ConversationState.IDLE
                return
            
            session.current_transcript = transcript
            
            # Send transcription to client
            await self.send_event(session, "transcript", {
                "text": transcript,
                "is_final": True
            })
            
            logger.info("Transcription complete", 
                       session_id=session.session_id, 
                       text=transcript)
            
            # Step 2: Generate LLM response with streaming
            await self.send_event(session, "processing", {"stage": "thinking"})
            await self._generate_streamed_response(session, transcript)
            
        except Exception as e:
            logger.error("Speech processing error", 
                        session_id=session.session_id, 
                        error=str(e))
            await self.send_event(session, "error", {"message": str(e)})
            session.state = ConversationState.IDLE
    
    async def _generate_streamed_response(self, session: VoiceSession, transcript: str):
        """
        Generate LLM response with streaming and parallel TTS.
        
        Implements sentence splitting and parallel TTS jobs:
        1. Stream tokens from LLM
        2. Split into sentences
        3. Queue TTS jobs in parallel
        4. Play audio in order
        """
        session.state = ConversationState.BOT_SPEAKING
        logger.info("🤖 ENTERING BOT_SPEAKING STATE 🤖", session_id=session.session_id)
        session.barge_in_detected = False
        session.pending_tts_tasks.clear()
        
        # CRITICAL: Get RAG context to ground responses in knowledge base
        # This prevents hallucination of fake plans like "Jio Bronze"
        try:
            from app.services.rag import knowledge_base
            # Pass conversation history so RAG can understand context
            # (e.g., if user was asking about AirFiber, continue with AirFiber docs)
            context = await knowledge_base.get_context_for_query(
                transcript, 
                conversation_history=session.history
            )
            logger.info("RAG context retrieved", 
                       session_id=session.session_id,
                       context_length=len(context) if context else 0)
        except Exception as e:
            logger.warning("Failed to get RAG context, proceeding without", error=str(e))
            context = None
        
        # Create prompt WITH RAG context
        messages = create_voice_prompt(
            user_message=transcript,
            context=context,  # Now passing RAG context!
            conversation_history=session.history
        )
        
        try:
            # Accumulate response for sentence splitting
            full_response = ""
            sentence_buffer = ""
            sentences_processed = 0
            tts_queue = []  # Queue of (sentence_index, audio_future)
            
            # Get streaming response from LLM
            # chat() is async def, so we await it to get the async generator
            response_stream = await ollama_client.chat(
                messages=messages, 
                stream=True
            )
            
            # Iterate over the async generator
            async for token in response_stream:
                if session.barge_in_detected:
                    logger.info("Response generation cancelled due to barge-in")
                    break
                
                full_response += token
                sentence_buffer += token
                
                # Send token to client for real-time display
                await self.send_event(session, "token", {"text": token})
                
                # Check for complete sentences/phrases
                chunks = self._split_sentences(sentence_buffer)
                
                if len(chunks) > 1:
                    # Process all complete chunks (except the last incomplete one)
                    for chunk in chunks[:-1]:
                        if chunk.strip():
                            # Check barge-in BEFORE starting TTS
                            if session.barge_in_detected:
                                logger.info("Skipping TTS due to barge-in")
                                break
                            
                            sentences_processed += 1
                            
                            # Process TTS SEQUENTIALLY (await each one)
                            # This allows barge-in to stop remaining sentences
                            await self._synthesize_and_queue(
                                session, 
                                chunk, 
                                sentences_processed
                            )
                    
                    # Keep only the incomplete chunk
                    sentence_buffer = chunks[-1]
            
            # Process any remaining text
            if sentence_buffer.strip() and not session.barge_in_detected:
                sentences_processed += 1
                await self._synthesize_and_queue(
                    session, 
                    sentence_buffer, 
                    sentences_processed
                )
            
            
            # Send complete response
            await self.send_event(session, "response_complete", {
                "text": full_response,
                "sentences": sentences_processed
            })
            
            # Store in history
            session.history.append({"role": "user", "content": transcript})
            session.history.append({"role": "assistant", "content": full_response})
            
            # Keep history manageable (last 10 messages)
            if len(session.history) > 10:
                session.history = session.history[-10:]
            
        except asyncio.CancelledError:
            logger.info("Response generation cancelled")
            session.state = ConversationState.IDLE
        except Exception as e:
            logger.error("LLM streaming error", error=str(e))
            await self.send_event(session, "error", {"message": str(e)})
            session.state = ConversationState.IDLE
        # NOTE: Do NOT set state to IDLE here!
        # State should remain BOT_SPEAKING while audio plays
        # It will be changed to LISTENING when user starts talking (barge-in or natural turn)
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into speakable sentences.
        
        Only split on sentence-ending punctuation (. ! ?) 
        NOT on commas/semicolons - those create too many tiny chunks
        which slow down TTS processing.
        """
        # Split on sentence-ending punctuation ONLY
        # Pattern matches: period, exclamation, question mark
        pattern = r'(?<=[.!?])\s+'
        chunks = re.split(pattern, text)
        
        # Filter out empty strings
        return [chunk.strip() for chunk in chunks if chunk.strip()]
    
    async def _synthesize_and_queue(
        self, 
        session: VoiceSession, 
        text: str, 
        index: int
    ):
        """Synthesize speech and IMMEDIATELY send to client."""
        # Early exit if barge-in already detected
        if session.barge_in_detected:
            logger.info("TTS skipped - barge-in already detected", 
                       session_id=session.session_id, index=index)
            return
            
        try:
            logger.info("TTS job started", 
                       session_id=session.session_id, 
                       index=index, 
                       text=text[:50])
            
            audio_data = await voice_pipeline.process_text_output(text)
            
            if audio_data and not session.barge_in_detected:
                # IMMEDIATELY send audio instead of queuing
                await self.send_event(session, "audio_start", {"index": index})
                await self.send_audio(session, audio_data)
                await self.send_event(session, "audio_end", {"index": index})
                
                logger.info("TTS job complete and audio sent", 
                           session_id=session.session_id, 
                           index=index)
            
        except Exception as e:
            logger.error("TTS job failed", 
                        session_id=session.session_id, 
                        index=index, 
                        error=str(e))
    
    async def _play_audio_queue(self, session: VoiceSession):
        """Play audio from queue in order."""
        # Wait for all pending TTS tasks
        if session.pending_tts_tasks:
            await asyncio.gather(*session.pending_tts_tasks, return_exceptions=True)
        
        # Sort by index and play
        audio_items = sorted(session.audio_queue, key=lambda x: x[0])
        
        for index, audio_data in audio_items:
            if session.barge_in_detected:
                break
            
            await self.send_event(session, "audio_start", {"index": index})
            await self.send_audio(session, audio_data)
            await self.send_event(session, "audio_end", {"index": index})
        
        session.audio_queue.clear()
    
    async def handle_control_message(self, session: VoiceSession, data: dict):
        """Handle control messages from client."""
        msg_type = data.get("type")
        
        if msg_type == "ping":
            await self.send_event(session, "pong")
        
        elif msg_type == "stop" or msg_type == "disconnect":
            # User requested stop/disconnect
            await self._handle_barge_in(session)
            await self.send_event(session, "disconnecting", {"message": "Ending session"})
        
        elif msg_type == "config":
            # Update configuration
            if "silence_timeout" in data:
                self.SILENCE_TIMEOUT_MS = data["silence_timeout"]
            logger.info("Config updated", session_id=session.session_id, config=data)
    
    async def _send_greeting(self, session: VoiceSession):
        """Send initial greeting to user."""
        try:
            greeting_text = "Namaste! Welcome to JioCare. How may I help you today?"
            
            # Generate greeting audio
            from app.services.voice import voice_pipeline
            audio_data = await voice_pipeline.process_text_output(greeting_text)
            
            if audio_data:
                await self.send_event(session, "greeting_start")
                await self.send_audio(session, audio_data)
                await self.send_event(session, "greeting_end", {"text": greeting_text})
                
                # Store in history
                session.history.append({"role": "assistant", "content": greeting_text})
                
                logger.info("Greeting sent", session_id=session.session_id)
        except Exception as e:
            logger.error("Failed to send greeting", error=str(e))


# Global gateway instance
voice_gateway = RealTimeVoiceGateway()


@router.websocket("/ws/voice/realtime/{session_id}")
async def realtime_voice_websocket(websocket: WebSocket, session_id: str):
    """
    Real-time voice WebSocket endpoint.
    
    Implements the full voice conversation pipeline with:
    - Continuous audio streaming
    - VAD-based speech detection
    - STT with streaming
    - LLM with sentence splitting
    - Parallel TTS
    - Barge-in detection
    """
    session = await voice_gateway.connect(websocket, session_id)
    
    try:
        while True:
            message = await websocket.receive()
            
            if "bytes" in message:
                # Audio chunk
                await voice_gateway.process_audio_chunk(session, message["bytes"])
            
            elif "text" in message:
                # Control message
                try:
                    data = json.loads(message["text"])
                    await voice_gateway.handle_control_message(session, data)
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON message", 
                                  session_id=session_id,
                                  text=message["text"])
    
    except WebSocketDisconnect:
        voice_gateway.disconnect(session_id)
    except Exception as e:
        logger.error("Voice WebSocket error", 
                    session_id=session_id, 
                    error=str(e))
        voice_gateway.disconnect(session_id)
