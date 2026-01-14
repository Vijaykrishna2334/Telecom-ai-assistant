"""
API routes initialization.
"""
from app.api.routes import assistants, calls, chat, chat_stream, health, voice

__all__ = ["health", "chat", "chat_stream", "voice", "assistants", "calls"]
