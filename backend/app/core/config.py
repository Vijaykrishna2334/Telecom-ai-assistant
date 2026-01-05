"""
Core configuration management for Telecom AI Assistant.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Telecom AI Assistant"
    debug: bool = False
    secret_key: str = "change-me-in-production"
    api_version: str = "v1"
    host: str = "0.0.0.0"
    port: int = 8000

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
    ollama_num_predict: int = 512

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection: str = "telecom_knowledge"

    # Voice Processing
    stt_model: str = "base"
    stt_device: str = "cpu"
    tts_voice: str = "en_US-amy-medium"  # Natural female voice
    tts_sample_rate: int = 22050
    vad_threshold: float = 0.5
    vad_min_speech_duration: float = 0.25

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
