"""
WebSocket handler for real-time voice streaming.
"""
import json
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.logging import get_logger
from app.services.llm import create_voice_prompt, ollama_client
from app.services.voice import voice_pipeline

logger = get_logger(__name__)
router = APIRouter()


class VoiceConnectionManager:
    """Manages voice WebSocket connections."""

    def __init__(self) -> None:
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """Connect a new WebSocket client."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info("Voice WebSocket connected", session_id=session_id)

    def disconnect(self, session_id: str) -> None:
        """Disconnect a WebSocket client."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info("Voice WebSocket disconnected", session_id=session_id)

    async def send_json(self, data: dict, session_id: str) -> None:
        """Send JSON data to a specific client."""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(data)

    async def send_bytes(self, data: bytes, session_id: str) -> None:
        """Send binary data to a specific client."""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_bytes(data)


voice_manager = VoiceConnectionManager()


@router.websocket("/ws/voice/{session_id}")
async def voice_websocket(websocket: WebSocket, session_id: str) -> None:
    """
    WebSocket endpoint for real-time voice streaming.

    Args:
        websocket: WebSocket connection
        session_id: Session identifier
    """
    await voice_manager.connect(websocket, session_id)

    try:
        while True:
            # Receive audio data from client
            message = await websocket.receive()

            if "bytes" in message:
                # Process audio input
                audio_data = message["bytes"]
                logger.info(
                    "Received audio",
                    session_id=session_id,
                    size=len(audio_data),
                )

                # Transcribe audio
                transcription = await voice_pipeline.process_audio_input(audio_data)

                if transcription:
                    # Send transcription to client
                    await voice_manager.send_json(
                        {
                            "type": "transcription",
                            "text": transcription,
                        },
                        session_id,
                    )

                    # Generate LLM response
                    messages = create_voice_prompt(transcription)
                    response = await ollama_client.chat(messages=messages)
                    response_text = response.get("message", {}).get("content", "")

                    # Send text response
                    await voice_manager.send_json(
                        {
                            "type": "text_response",
                            "text": response_text,
                        },
                        session_id,
                    )

                    # Synthesize speech
                    audio_response = await voice_pipeline.process_text_output(
                        response_text
                    )

                    # Send audio response
                    await voice_manager.send_bytes(audio_response, session_id)

            elif "text" in message:
                # Handle control messages
                data = json.loads(message["text"])
                logger.info("Received control message", session_id=session_id, data=data)

                if data.get("type") == "ping":
                    await voice_manager.send_json({"type": "pong"}, session_id)

    except WebSocketDisconnect:
        voice_manager.disconnect(session_id)
        logger.info("Voice client disconnected", session_id=session_id)
    except Exception as e:
        logger.error("Voice WebSocket error", session_id=session_id, error=str(e))
        voice_manager.disconnect(session_id)
        # Send error message
        try:
            await voice_manager.send_json(
                {"type": "error", "message": str(e)}, session_id
            )
        except:
            pass
