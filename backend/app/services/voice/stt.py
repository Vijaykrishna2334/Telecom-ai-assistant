"""
Speech-to-Text service using Faster-Whisper.
Transcribes audio to text using Whisper models.
"""
import io
import wave
import tempfile
import os
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class STTService:
    """Speech-to-Text service using Faster-Whisper."""

    def __init__(
        self,
        model_size: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize STT service.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large-v3)
            device: Device to use (cpu, cuda)
        """
        self.model_size = model_size or settings.stt_model
        self.device = device or settings.stt_device
        self.model = None
        self.model_loaded = False
        logger.info("Initializing STT service", model=self.model_size, device=self.device)

    async def load_model(self) -> None:
        """Load the Whisper model."""
        try:
            from faster_whisper import WhisperModel
            
            logger.info("Loading Whisper model...", model=self.model_size, device=self.device)
            self.model = WhisperModel(
                self.model_size, 
                device=self.device,
                compute_type="int8" if self.device == "cpu" else "float16"
            )
            self.model_loaded = True
            logger.info("STT model loaded successfully", model=self.model_size)
        except ImportError:
            logger.warning("faster-whisper not installed, STT will use placeholder")
            self.model_loaded = False
        except Exception as e:
            logger.error("Failed to load STT model", error=str(e))
            self.model_loaded = False

    def _bytes_to_wav_file(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        """Convert raw audio bytes to a temporary WAV file."""
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        
        with wave.open(temp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data)
        
        return temp_file.name

    async def transcribe(
        self, audio_data: bytes, language: str = "en"
    ) -> dict[str, any]:
        """
        Transcribe audio to text.

        Args:
            audio_data: Audio bytes (16-bit PCM, mono, 16kHz)
            language: Language code

        Returns:
            Dict with transcription result
        """
        logger.info("Transcribing audio", language=language, audio_size=len(audio_data))

        if not self.model_loaded or self.model is None:
            logger.warning("STT model not loaded, returning placeholder")
            return {
                "text": "[STT model not loaded - please check faster-whisper installation]",
                "language": language,
                "confidence": 0.0,
            }

        try:
            # Convert bytes to temporary WAV file
            temp_wav = self._bytes_to_wav_file(audio_data)
            
            try:
                # Transcribe using faster-whisper
                segments, info = self.model.transcribe(
                    temp_wav,
                    language=language,
                    vad_filter=True,  # Use built-in VAD
                    beam_size=5
                )
                
                # Collect all segments
                text_parts = []
                confidence_sum = 0
                segment_count = 0
                
                for segment in segments:
                    text_parts.append(segment.text)
                    confidence_sum += segment.avg_logprob
                    segment_count += 1
                
                full_text = " ".join(text_parts).strip()
                avg_confidence = confidence_sum / segment_count if segment_count > 0 else 0
                
                logger.info("Transcription complete", 
                           text=full_text[:100] if full_text else "[empty]",
                           segments=segment_count)
                
                return {
                    "text": full_text if full_text else "[No speech detected]",
                    "language": info.language if info else language,
                    "confidence": avg_confidence,
                }
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_wav):
                    os.remove(temp_wav)
                    
        except Exception as e:
            logger.error("Transcription error", error=str(e))
            return {
                "text": f"[Transcription error: {str(e)}]",
                "language": language,
                "confidence": 0.0,
            }

    async def transcribe_stream(self, audio_stream):
        """
        Transcribe streaming audio.

        Args:
            audio_stream: Audio stream generator

        Yields:
            Transcription chunks
        """
        logger.info("Starting streaming transcription")
        
        # Accumulate audio chunks
        audio_buffer = b""
        
        async for chunk in audio_stream:
            audio_buffer += chunk
            
            # Process every ~1 second of audio (16000 samples * 2 bytes)
            if len(audio_buffer) >= 32000:
                result = await self.transcribe(audio_buffer)
                yield {"text": result["text"], "is_final": False}
                audio_buffer = b""
        
        # Process remaining audio
        if audio_buffer:
            result = await self.transcribe(audio_buffer)
            yield {"text": result["text"], "is_final": True}


# Global STT service instance
stt_service = STTService()

