"""
Core configuration management for Telecom AI Assistant.
"""
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Find .env file - check both backend/ and project root
_backend_dir = Path(__file__).resolve().parent.parent.parent  # backend/
_project_root = _backend_dir.parent  # Telecom-ai-assistant/
_env_file = _project_root / ".env" if (_project_root / ".env").exists() else ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(_env_file),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Allow extra env vars like VITE_*
    )

    # Application
    app_name: str = "Telecom AI Assistant"
    debug: bool = False
    secret_key: str = "change-me-in-production"
    api_version: str = "v1"
    host: str = "0.0.0.0"
    port: int = 8080

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/telecom_ai"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 3600

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_timeout: int = 120
    ollama_num_predict: int = 150  # Reduced for faster responses (was 512)

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection: str = "telecom_knowledge"

    # CRAG (Corrective RAG) Settings
    # Embedding model: BGE is 2024 state-of-the-art for RAG
    embedding_model: str = "BAAI/bge-base-en-v1.5"
    # Relevance thresholds for CRAG grading
    crag_relevance_threshold: float = 0.6  # Score above = CORRECT
    crag_ambiguous_threshold: float = 0.3  # Score between = AMBIGUOUS, below = INCORRECT
    crag_top_k: int = 5  # Number of documents to retrieve

    # Voice Processing
    # base.en: Good balance of speed and accuracy (prevents hallucinations)
    # tiny.en was hallucinating, base.en is more reliable
    stt_model: str = "base.en"  
    stt_device: str = "cuda"  # GPU enabled for faster STT
    stt_compute_type: str = "float16"  # float16 for GPU (faster than int8)
    
    # TTS Configuration
    # Options: "piper" (stable), "kokoro" (fast), "cosyvoice" (best quality, 150ms latency)
    # NOTE: Kokoro has compatibility issues with Python 3.12 (spacy/pydantic)
    tts_provider: str = "kokoro"  # Using Kokoro for faster TTS
    
    # Piper TTS settings
    tts_voice: str = "en_US-ljspeech-high"  # High-quality natural female voice
    tts_sample_rate: int = 22050
    
    # Kokoro TTS settings (82M lightweight model)
    kokoro_voice: str = "af_heart"  # American female voice
    kokoro_lang_code: str = "a"  # 'a' = American English
    
    # CosyVoice TTS settings (Alibaba FunAudioLLM - 150ms latency)
    # Models: CosyVoice2-0.5B (latest), CosyVoice-300M
    cosyvoice_model: str = "CosyVoice2-0.5B"
    cosyvoice_voice: str = "default"  # Or path to reference audio for cloning
    
    # VAD settings
    vad_threshold: float = 0.5  # Higher threshold = less sensitive to noise (0.0-1.0)
    vad_min_speech_duration: float = 0.25  # Minimum speech duration in seconds

    # Security
    cors_origins: List[str] = ["*"]  # Allow all origins for local development
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    @property
    def api_prefix(self) -> str:
        """Get API prefix path."""
        return f"/api/{self.api_version}"


# Global settings instance
settings = Settings()
