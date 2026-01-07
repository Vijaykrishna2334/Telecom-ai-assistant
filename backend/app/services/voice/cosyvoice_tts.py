"""
Text-to-Speech service using CosyVoice 2/3 (Alibaba FunAudioLLM).
CosyVoice is a state-of-the-art TTS with:
- 150ms streaming latency
- Zero-shot voice cloning
- Emotional control
- Multi-lingual support

GitHub: https://github.com/FunAudioLLM/CosyVoice
"""
import io
import wave
import numpy as np
from typing import Optional, AsyncGenerator
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# CosyVoice model paths (will be downloaded on first use)
COSYVOICE_MODEL_DIR = Path(__file__).parent / "models" / "cosyvoice"


def get_device():
    """Detect best available device for TTS."""
    try:
        import torch
        if torch.cuda.is_available():
            logger.info("CUDA GPU detected for CosyVoice TTS")
            return "cuda"
    except ImportError:
        pass
    return "cpu"


class CosyVoiceTTSService:
    """
    Text-to-Speech service using CosyVoice 2/3.
    
    Features:
    - Ultra-low latency (~150ms streaming)
    - Zero-shot voice cloning from 3-10 sec reference
    - Emotional control via instruct mode
    - Streaming bi-directional synthesis
    """

    def __init__(
        self,
        model_name: str = "CosyVoice2-0.5B",
        voice: Optional[str] = None,
    ):
        """
        Initialize CosyVoice TTS service.

        Args:
            model_name: Model to use (CosyVoice2-0.5B or CosyVoice-300M)
            voice: Voice preset (optional, for zero-shot cloning)
        """
        self.model_name = model_name
        self.voice = voice
        self.sample_rate = 22050  # CosyVoice default sample rate
        self.model = None
        self.model_loaded = False
        self.device = get_device()
        logger.info(
            "Initializing CosyVoice TTS service", 
            model=model_name, 
            device=self.device
        )

    async def load_model(self) -> None:
        """Load the CosyVoice TTS model."""
        try:
            # Try to import CosyVoice
            try:
                from cosyvoice.cli.cosyvoice import CosyVoice2
                model_class = CosyVoice2
                logger.info("Using CosyVoice2 (latest)")
            except ImportError:
                try:
                    from cosyvoice.cli.cosyvoice import CosyVoice
                    model_class = CosyVoice
                    logger.info("Using CosyVoice (original)")
                except ImportError:
                    raise ImportError(
                        "CosyVoice not installed. Install with:\n"
                        "  git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git\n"
                        "  cd CosyVoice && pip install -r requirements.txt"
                    )

            # Load model from ModelScope or local path
            model_dir = str(COSYVOICE_MODEL_DIR / self.model_name)
            
            # Try loading from local path first, then ModelScope
            try:
                self.model = model_class(model_dir)
            except Exception:
                # Download from ModelScope
                logger.info("Downloading CosyVoice model from ModelScope...")
                model_id = f"iic/{self.model_name}"
                self.model = model_class(model_id, load_jit=False, load_trt=False)
            
            self.model_loaded = True
            logger.info("CosyVoice TTS model loaded successfully", model=self.model_name)
                
        except ImportError as e:
            logger.error("CosyVoice not installed", error=str(e))
            raise
        except Exception as e:
            logger.error("Failed to load CosyVoice TTS", error=str(e))
            raise

    async def synthesize(
        self, 
        text: str,
        instruct: Optional[str] = None,
        reference_audio: Optional[bytes] = None,
    ) -> bytes:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            instruct: Optional instruction for emotional control
                      e.g., "Speak with empathy and concern"
            reference_audio: Optional reference audio for voice cloning

        Returns:
            WAV audio data as bytes
        """
        if not self.model_loaded:
            await self.load_model()

        logger.info("Synthesizing speech with CosyVoice", text_length=len(text))

        try:
            # Choose synthesis mode
            if reference_audio:
                # Zero-shot voice cloning
                output = self.model.inference_zero_shot(
                    text, 
                    reference_audio,
                    stream=False
                )
            elif instruct:
                # Instruct mode with emotional control
                output = self.model.inference_instruct(
                    text,
                    self.voice or "default",
                    instruct,
                    stream=False
                )
            else:
                # Standard synthesis
                output = self.model.inference_sft(
                    text,
                    self.voice or "default",
                    stream=False
                )

            # Collect output
            audio_data = None
            for result in output:
                audio_data = result["tts_speech"]
                break  # Non-streaming, take first result

            if audio_data is None:
                logger.warning("No audio generated")
                return b""

            # Convert to WAV bytes
            wav_bytes = self._to_wav_bytes(audio_data)
            logger.info("CosyVoice TTS generated audio", bytes=len(wav_bytes))
            return wav_bytes

        except Exception as e:
            logger.error("CosyVoice TTS synthesis failed", error=str(e))
            raise

    async def synthesize_stream(
        self, 
        text: str,
        instruct: Optional[str] = None,
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream synthesize speech from text (yields audio chunks).
        
        CosyVoice 2 supports true bi-directional streaming with ~150ms latency.

        Args:
            text: Text to synthesize
            instruct: Optional instruction for emotional control

        Yields:
            WAV audio data chunks as bytes
        """
        if not self.model_loaded:
            await self.load_model()

        logger.info("Streaming synthesis with CosyVoice", text_length=len(text))

        try:
            # Use streaming mode
            if instruct:
                output = self.model.inference_instruct(
                    text,
                    self.voice or "default", 
                    instruct,
                    stream=True
                )
            else:
                output = self.model.inference_sft(
                    text,
                    self.voice or "default",
                    stream=True
                )

            for result in output:
                audio_chunk = result.get("tts_speech")
                if audio_chunk is not None:
                    yield self._to_wav_bytes(audio_chunk)

        except Exception as e:
            logger.error("CosyVoice TTS streaming failed", error=str(e))
            raise

    async def clone_voice(
        self,
        text: str,
        reference_audio_path: str,
        reference_text: Optional[str] = None,
    ) -> bytes:
        """
        Synthesize speech using zero-shot voice cloning.

        Args:
            text: Text to synthesize
            reference_audio_path: Path to reference audio (3-10 seconds)
            reference_text: Optional transcript of reference audio

        Returns:
            WAV audio data as bytes in cloned voice
        """
        if not self.model_loaded:
            await self.load_model()

        logger.info(
            "Cloning voice with CosyVoice", 
            text_length=len(text),
            reference=reference_audio_path
        )

        try:
            # Load reference audio
            import torchaudio
            reference_audio, sr = torchaudio.load(reference_audio_path)
            
            # Zero-shot cloning
            output = self.model.inference_zero_shot(
                text,
                reference_text or "",
                reference_audio,
                stream=False
            )

            audio_data = None
            for result in output:
                audio_data = result["tts_speech"]
                break

            if audio_data is None:
                return b""

            return self._to_wav_bytes(audio_data)

        except Exception as e:
            logger.error("CosyVoice voice cloning failed", error=str(e))
            raise

    def _to_wav_bytes(self, audio_tensor) -> bytes:
        """Convert audio tensor to WAV bytes."""
        import torch
        
        # Ensure we have numpy array
        if isinstance(audio_tensor, torch.Tensor):
            audio_np = audio_tensor.cpu().numpy()
        else:
            audio_np = np.array(audio_tensor)

        # Flatten if needed
        if len(audio_np.shape) > 1:
            audio_np = audio_np.flatten()

        # Convert to WAV
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            
            # Normalize and convert to int16
            audio_np = audio_np / max(abs(audio_np.max()), abs(audio_np.min()), 1e-8)
            audio_int16 = (audio_np * 32767).astype(np.int16)
            wav_file.writeframes(audio_int16.tobytes())

        return wav_buffer.getvalue()


# Create service instance when imported
cosyvoice_tts_service = CosyVoiceTTSService()
