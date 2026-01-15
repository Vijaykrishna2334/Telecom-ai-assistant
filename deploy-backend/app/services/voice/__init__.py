"""
Voice processing services for STT, TTS, VAD, and pipeline.
Uses Kokoro TTS for text-to-speech.
"""
from app.services.voice.pipeline import VoicePipeline, voice_pipeline
from app.services.voice.stt import STTService, stt_service
from app.services.voice.tts import tts_service
from app.services.voice.vad import VADService, vad_service
from app.services.voice.kokoro_tts import KokoroTTSService

__all__ = [
    "STTService",
    "stt_service",
    "tts_service",
    "VADService",
    "vad_service",
    "VoicePipeline",
    "voice_pipeline",
    "KokoroTTSService",
]

