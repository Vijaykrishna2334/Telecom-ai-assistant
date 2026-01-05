"""
API routes initialization.
"""
from app.api.routes import assistants, calls, chat, health, voice

__all__ = ["health", "chat", "voice", "assistants", "calls"]
