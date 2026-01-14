"""
Voice Activity Detection (VAD) using Silero-VAD.
Silero-VAD is a pre-trained deep learning model for accurate speech detection.
"""
import torch
import struct
import numpy as np
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VADService:
    """Voice Activity Detection using Silero-VAD neural model."""

    def __init__(
        self,
        threshold: Optional[float] = None,
        sample_rate: int = 16000,
    ):
        """
        Initialize VAD service.

        Args:
            threshold: Speech probability threshold (0.0 to 1.0)
            sample_rate: Audio sample rate in Hz
        """
        self.threshold = threshold or settings.vad_threshold
        self.sample_rate = sample_rate
        self.model = None
        self.model_loaded = False
        self.use_energy_fallback = False
        self.energy_threshold = 500  # Fallback energy threshold
        
        logger.info(
            "Initializing VAD service",
            threshold=self.threshold,
            sample_rate=self.sample_rate,
        )

    async def load_model(self) -> None:
        """Load the Silero-VAD model."""
        try:
            # Load Silero-VAD model
            self.model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            
            self.model_loaded = True
            logger.info("Silero-VAD model loaded successfully")
            
        except Exception as e:
            logger.warning(
                "Failed to load Silero-VAD, using energy-based fallback",
                error=str(e)
            )
            self.use_energy_fallback = True
            self.model_loaded = True  # Still mark as loaded for fallback

    async def detect_speech(self, audio_data: bytes) -> bool:
        """
        Detect if audio contains speech using Silero-VAD.

        Args:
            audio_data: Raw audio bytes (16-bit PCM)

        Returns:
            True if speech detected, False otherwise
        """
        if not self.model_loaded:
            logger.warning("VAD model not loaded, assuming no speech")
            return False

        if len(audio_data) < 2:
            return False

        try:
            if self.use_energy_fallback:
                return await self._detect_speech_energy(audio_data)
            else:
                return await self._detect_speech_silero(audio_data)
                
        except Exception as e:
            logger.error("VAD detection error", error=str(e))
            # On error, assume speech to avoid dropping audio
            return True

    async def _detect_speech_silero(self, audio_data: bytes) -> bool:
        """Detect speech using Silero-VAD neural model."""
        try:
            # Convert bytes to numpy array
            num_samples = len(audio_data) // 2
            audio_int16 = struct.unpack(f'<{num_samples}h', audio_data[:num_samples * 2])
            audio_float32 = np.array(audio_int16, dtype=np.float32) / 32768.0
            
            # Silero-VAD requires EXACTLY 512 samples for 16kHz
            required_samples = 512
            
            if len(audio_float32) < required_samples:
                # Pad with zeros if too short
                audio_float32 = np.pad(audio_float32, (0, required_samples - len(audio_float32)))
            elif len(audio_float32) > required_samples:
                # Take only first 512 samples if too long
                audio_float32 = audio_float32[:required_samples]
            
            # Convert to torch tensor
            audio_tensor = torch.from_numpy(audio_float32)
            
            # Get speech probability from model
            speech_prob = self.model(audio_tensor, self.sample_rate).item()
            
            is_speech = speech_prob > self.threshold
            
            if is_speech:
                logger.debug(
                    "Speech detected (Silero)",
                    probability=speech_prob,
                    threshold=self.threshold,
                    samples=len(audio_float32)
                )
            
            return is_speech
            
        except Exception as e:
            logger.error("Silero-VAD error, falling back to energy", error=str(e))
            return await self._detect_speech_energy(audio_data)

    async def _detect_speech_energy(self, audio_data: bytes) -> bool:
        """Fallback: Energy-based speech detection."""
        try:
            num_samples = len(audio_data) // 2
            samples = struct.unpack(f'<{num_samples}h', audio_data[:num_samples * 2])
            
            # Calculate RMS energy
            sum_squares = sum(s * s for s in samples)
            rms = (sum_squares / num_samples) ** 0.5 if num_samples > 0 else 0
            
            is_speech = rms > self.energy_threshold
            
            if is_speech:
                logger.debug(
                    "Speech detected (Energy fallback)",
                    rms=rms,
                    threshold=self.energy_threshold
                )
            
            return is_speech
            
        except Exception as e:
            logger.error("Energy-based VAD error", error=str(e))
            return True


# Global VAD service instance
vad_service = VADService()
