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
        try:
            from piper import PiperVoice
            
            # Look for model file
            model_path = os.path.join(
                os.path.dirname(__file__), 
                "models", 
                f"{self.voice}.onnx"
            )
            
            if not os.path.exists(model_path):
                error_msg = f"Piper model not found at {model_path}. Please download it first."
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            self.model = PiperVoice.load(model_path)
            self.model_loaded = True
            logger.info("Piper TTS model loaded successfully", voice=self.voice, path=model_path)
                
        except ImportError as e:
            logger.error("piper-tts not installed - run: pip install piper-tts")
            raise ImportError("piper-tts package required. Install with: pip install piper-tts") from e
        except Exception as e:
            logger.error("Failed to load Piper TTS", error=str(e))
            raise
    
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
        """Synthesize using Piper TTS via command line."""
        import subprocess
        import json
        
        # Use Piper CLI - the officially documented method
        try:
            model_path = os.path.join(
                os.path.dirname(__file__), 
                "models", 
                f"{self.voice}.onnx"
            )
            
            # Create temp file for output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_path = temp_wav.name
            
            try:
                # Call Piper CLI: echo "text" | piper --model model.onnx --output_file output.wav
                cmd = [
                    'piper',
                    '--model', model_path,
                    '--output_file', temp_path
                ]
                
                # Run Piper with text as stdin
                result = subprocess.run(
                    cmd,
                    input=text.encode('utf-8'),
                    capture_output=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    logger.error(f"Piper CLI failed: {result.stderr.decode()}")
                    return b""
                
                # Read the generated WAV file
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                
                logger.info(f"Piper TTS generated {len(audio_data)} bytes via CLI")
                return audio_data
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except FileNotFoundError:
            logger.error("Piper CLI not found - install with: pip install piper-tts")
            return b""
        except Exception as e:
            logger.error("Piper CLI failed", error=str(e))
            return b""

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
