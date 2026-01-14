"""
Voice processing pipeline integrating STT, TTS, and VAD.
"""
from typing import AsyncGenerator, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.services.voice.stt import stt_service
from app.services.voice.vad import vad_service
from app.services.voice.tts import tts_service

logger = get_logger(__name__)


class VoicePipeline:
    """Voice processing pipeline."""

    def __init__(self):
        """Initialize voice pipeline."""
        self.stt = stt_service
        self.tts = tts_service
        self.vad = vad_service

    async def initialize(self) -> None:
        """Initialize all voice processing models."""
        logger.info("Initializing voice pipeline")
        await self.stt.load_model()
        await self.tts.load_model()
        await self.vad.load_model()
        logger.info("Voice pipeline initialized")

    async def detect_speech(self, audio_chunk: bytes) -> bool:
        """
        Detect if audio chunk contains speech.
        
        Args:
            audio_chunk: Audio bytes (16-bit PCM)
            
        Returns:
            True if speech detected, False otherwise
        """
        return await self.vad.detect_speech(audio_chunk)

    async def process_audio_input(
        self, audio_data: bytes, language: str = "en"
    ) -> Optional[str]:
        """
        Process audio input through VAD and STT.

        Args:
            audio_data: Audio bytes
            language: Language code

        Returns:
            Transcribed text or None if no speech detected
        """
        # Skip VAD check - we already detected speech in real-time chunks
        # The buffer was accumulated BECAUSE chunks contained speech
        # No need to re-validate the entire buffer with Silero-VAD
        
        # Transcribe audio directly
        result = await self.stt.transcribe(audio_data, language)
        return result.get("text")

    async def process_text_output(self, text: str) -> bytes:
        """
        Process text output through TTS.

        Args:
            text: Text to synthesize

        Returns:
            Audio bytes
        """
        audio_data = await self.tts.synthesize(text)
        return audio_data

    async def process_conversation_turn(
        self, audio_input: bytes, text_response: str, language: str = "en"
    ) -> dict[str, any]:
        """
        Process a full conversation turn.

        Args:
            audio_input: Input audio bytes
            text_response: Text response from LLM
            language: Language code

        Returns:
            Dict with transcription and audio response
        """
        logger.info("Processing conversation turn")

        # Process input
        transcription = await self.process_audio_input(audio_input, language)

        # Process output
        audio_response = await self.process_text_output(text_response)

        return {
            "transcription": transcription,
            "audio_response": audio_response,
            "text_response": text_response,
        }

    async def stream_audio_processing(
        self, audio_stream: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[dict[str, any], None]:
        """
        Process streaming audio.

        Args:
            audio_stream: Stream of audio chunks

        Yields:
            Processing results
        """
        logger.info("Starting streaming audio processing")

        async for audio_chunk in audio_stream:
            # Check for speech
            has_speech = await self.vad.detect_speech(audio_chunk)

            if has_speech:
                # Transcribe chunk
                result = await self.stt.transcribe(audio_chunk)
                yield result


# Global voice pipeline instance
voice_pipeline = VoicePipeline()
