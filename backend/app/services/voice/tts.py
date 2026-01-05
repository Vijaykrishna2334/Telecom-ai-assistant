"""
Text-to-Speech service using Piper TTS.
Runs fully locally without cloud dependencies.
Falls back to pyttsx3 (system TTS) on Windows if Piper is not available.
"""
import io
import wave
import tempfile
import os
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TTSService:
    """Text-to-Speech service using Piper TTS (local)."""

    def __init__(
        self,
        voice: Optional[str] = None,
        sample_rate: Optional[int] = None,
    ):
        """
        Initialize TTS service.

        Args:
            voice: Voice model to use
            sample_rate: Audio sample rate
        """
        self.voice = voice or settings.tts_voice
        self.sample_rate = sample_rate or settings.tts_sample_rate
        self.model = None
        self.model_loaded = False
        self.use_pyttsx3 = False
        self.engine = None
        logger.info("Initializing TTS service", voice=self.voice)

    async def load_model(self) -> None:
        """Load the Piper TTS model."""
        # First try Piper
        try:
            from piper import PiperVoice
            
            # Look for model file
            model_path = os.path.join(
                os.path.dirname(__file__), 
                "models", 
                f"{self.voice}.onnx"
            )
            
            if os.path.exists(model_path):
                self.model = PiperVoice.load(model_path)
                self.model_loaded = True
                logger.info("Piper TTS model loaded", voice=self.voice)
                return
            else:
                logger.warning("Piper model not found", path=model_path)
                
        except ImportError:
            logger.warning("piper-tts not installed")
        except Exception as e:
            logger.error("Piper failed", error=str(e))
        
        # Fallback to pyttsx3 (Windows system TTS)
        self._init_pyttsx3()
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3 as fallback TTS and try to find a female voice."""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            
            # Try to find a female voice
            voices = self.engine.getProperty('voices')
            female_voice = None
            for voice in voices:
                if "female" in voice.name.lower() or "zira" in voice.name.lower() or "hazel" in voice.name.lower():
                    female_voice = voice.id
                    break
            
            if female_voice:
                self.engine.setProperty('voice', female_voice)
                logger.info("Selected female system voice", name=next(v.name for v in voices if v.id == female_voice))
            
            self.engine.setProperty('rate', 160)
            self.engine.setProperty('volume', 0.9)
            self.use_pyttsx3 = True
            self.model_loaded = True
            logger.info("Using pyttsx3 system TTS (local)")
        except Exception as e:
            logger.error("pyttsx3 failed", error=str(e))
            self.model_loaded = False

    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize

        Returns:
            Audio bytes (WAV format)
        """
        if not text or not text.strip():
            return b""
            
        logger.info("Synthesizing speech", text_length=len(text))

        if not self.model_loaded:
            logger.warning("TTS not loaded")
            return b""

        try:
            if self.use_pyttsx3:
                return self._synthesize_pyttsx3(text)
            else:
                return self._synthesize_piper(text)
        except Exception as e:
            logger.error("TTS error", error=str(e))
            return b""

    def _synthesize_piper(self, text: str) -> bytes:
        """Synthesize using Piper TTS."""
        audio_buffer = io.BytesIO()
        
        with wave.open(audio_buffer, 'wb') as wav_file:
            wav_file.setframerate(self.sample_rate)
            wav_file.setsampwidth(2)
            wav_file.setnchannels(1)
            
            for audio_bytes in self.model.synthesize_stream_raw(text):
                wav_file.writeframes(audio_bytes)
        
        return audio_buffer.getvalue()

    def _synthesize_pyttsx3(self, text: str) -> bytes:
        """Synthesize using pyttsx3 system TTS."""
        temp_path = tempfile.mktemp(suffix=".wav")
        
        try:
            self.engine.save_to_file(text, temp_path)
            self.engine.runAndWait()
            
            if os.path.exists(temp_path):
                with open(temp_path, 'rb') as f:
                    return f.read()
            return b""
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    async def synthesize_stream(self, text: str):
        """
        Synthesize speech from text as a stream.

        Args:
            text: Text to synthesize

        Yields:
            Audio chunks
        """
        if not text or not text.strip():
            return
            
        if not self.model_loaded:
            return

        if self.use_pyttsx3:
            audio = self._synthesize_pyttsx3(text)
            if audio:
                yield audio
        else:
            try:
                for chunk in self.model.synthesize_stream_raw(text):
                    yield chunk
            except Exception as e:
                logger.error("TTS stream error", error=str(e))


# Global TTS service instance
tts_service = TTSService()
