"""
Text-to-Speech service using Kokoro-82M TTS.
Kokoro is a lightweight 82M parameter TTS model with high quality output.
Apache licensed, runs locally without cloud dependencies.
"""
import io
import wave
import numpy as np
from typing import Optional, AsyncGenerator

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_device():
    """Detect best available device for TTS."""
    try:
        import torch
        if torch.cuda.is_available():
            logger.info("CUDA GPU detected for Kokoro TTS")
            return "cuda"
    except ImportError:
        pass
    return "cpu"


class KokoroTTSService:
    """Text-to-Speech service using Kokoro-82M TTS (local)."""

    def __init__(
        self,
        voice: Optional[str] = None,
        lang_code: Optional[str] = None,
    ):
        """
        Initialize Kokoro TTS service.

        Args:
            voice: Voice to use (default: af_heart - American female)
            lang_code: Language code (default: 'a' for American English)
        """
        self.voice = voice or getattr(settings, 'kokoro_voice', 'af_heart')
        self.lang_code = lang_code or getattr(settings, 'kokoro_lang_code', 'a')
        self.sample_rate = 24000  # Kokoro outputs at 24kHz
        self.pipeline = None
        self.model_loaded = False
        self.device = get_device()
        logger.info("Initializing Kokoro TTS service", voice=self.voice, lang_code=self.lang_code, device=self.device)

    async def load_model(self) -> None:
        """Load the Kokoro TTS model."""
        try:
            from kokoro import KPipeline
            
            # KPipeline automatically uses GPU if available
            self.pipeline = KPipeline(lang_code=self.lang_code)
            self.model_loaded = True
            logger.info("Kokoro TTS model loaded successfully", voice=self.voice, device=self.device)
                
        except ImportError as e:
            logger.error("kokoro not installed - run: pip install 'kokoro>=0.9.2' soundfile")
            raise ImportError("kokoro package required. Install with: pip install 'kokoro>=0.9.2' soundfile") from e
        except Exception as e:
            logger.error("Failed to load Kokoro TTS", error=str(e))
            raise

    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize

        Returns:
            WAV audio data as bytes
        """
        if not self.model_loaded:
            await self.load_model()

        logger.info("Synthesizing speech with Kokoro", text_length=len(text))

        try:
            # Generate audio using Kokoro pipeline
            generator = self.pipeline(text, voice=self.voice)
            
            # Collect all audio chunks
            audio_chunks = []
            for i, (gs, ps, audio) in enumerate(generator):
                audio_chunks.append(audio)
            
            # Concatenate all chunks
            if audio_chunks:
                full_audio = np.concatenate(audio_chunks)
            else:
                logger.warning("No audio generated")
                return b""

            # Convert to WAV bytes
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                
                # Convert float32 to int16
                audio_int16 = (full_audio * 32767).astype(np.int16)
                wav_file.writeframes(audio_int16.tobytes())

            wav_bytes = wav_buffer.getvalue()
            logger.info("Kokoro TTS generated audio", bytes=len(wav_bytes))
            return wav_bytes

        except Exception as e:
            logger.error("Kokoro TTS synthesis failed", error=str(e))
            raise

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Stream synthesize speech from text (yields audio chunks).

        Args:
            text: Text to synthesize

        Yields:
            WAV audio data chunks as bytes
        """
        if not self.model_loaded:
            await self.load_model()

        logger.info("Streaming synthesis with Kokoro", text_length=len(text))

        try:
            generator = self.pipeline(text, voice=self.voice)
            
            for i, (gs, ps, audio) in enumerate(generator):
                # Convert each chunk to WAV bytes
                wav_buffer = io.BytesIO()
                with wave.open(wav_buffer, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(self.sample_rate)
                    audio_int16 = (audio * 32767).astype(np.int16)
                    wav_file.writeframes(audio_int16.tobytes())
                
                yield wav_buffer.getvalue()

        except Exception as e:
            logger.error("Kokoro TTS streaming failed", error=str(e))
            raise
