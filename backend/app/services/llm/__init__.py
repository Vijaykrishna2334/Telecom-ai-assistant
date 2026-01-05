"""
LLM services for Telecom AI Assistant.
"""
from app.services.llm.function_router import FunctionRouter, function_router
from app.services.llm.ollama_client import OllamaClient, ollama_client
from app.services.llm.prompt_templates import (
    AVAILABLE_FUNCTIONS,
    TELECOM_SYSTEM_PROMPT,
    VOICE_SYSTEM_PROMPT,
    create_chat_prompt,
    create_voice_prompt,
    get_function_definitions,
)

__all__ = [
    "OllamaClient",
    "ollama_client",
    "FunctionRouter",
    "function_router",
    "TELECOM_SYSTEM_PROMPT",
    "VOICE_SYSTEM_PROMPT",
    "AVAILABLE_FUNCTIONS",
    "create_chat_prompt",
    "create_voice_prompt",
    "get_function_definitions",
]
