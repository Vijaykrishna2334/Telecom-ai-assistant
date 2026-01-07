"""
Voice processing services for STT, TTS, VAD, and pipeline.
Supports multiple TTS providers: Piper, Kokoro, CosyVoice
"""
from app.services.voice.pipeline import VoicePipeline, voice_pipeline
from app.services.voice.stt import STTService, stt_service
from app.services.voice.tts import TTSService, tts_service
from app.services.voice.vad import VADService, vad_service
from app.services.voice.kokoro_tts import KokoroTTSService
from app.services.voice.cosyvoice_tts import CosyVoiceTTSService

__all__ = [
    "STTService",
    "stt_service",
    "TTSService",
    "tts_service",
    "VADService",
    "vad_service",
    "VoicePipeline",
    "voice_pipeline",
    "KokoroTTSService",
    "CosyVoiceTTSService",
]

