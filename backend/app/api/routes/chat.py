"""
Chat API endpoints.
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from app.core.logging import get_logger
from app.core.security import generate_session_id
from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm import create_chat_prompt, ollama_client
from app.services.rag import knowledge_base

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    tags=["Chat"],
)
async def send_message(request: ChatRequest) -> ChatResponse:
    """
    Send a chat message and get AI response.

    Args:
        request: Chat request with message and optional session_id

    Returns:
        Chat response with assistant message
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or generate_session_id()

        logger.info(
            "Processing chat message",
            session_id=session_id,
            message_length=len(request.message),
        )

        # Get relevant context from knowledge base
        context = await knowledge_base.get_context_for_query(request.message)

        # Create prompt with context and history
        messages = create_chat_prompt(
            user_message=request.message,
            context=context if context else None,
            conversation_history=request.history,
        )

        # Generate response from LLM
        response = await ollama_client.chat(messages=messages)

        # Extract assistant message
        assistant_message = response.get("message", {}).get("content", "")

        logger.info(
            "Chat response generated",
            session_id=session_id,
            response_length=len(assistant_message),
        )

        return ChatResponse(
            message=assistant_message,
            session_id=session_id,
            conversation_id=1,  # Would be actual conversation ID from DB
            rag_context=context if context else None,  # Debug: Show RAG context
        )

    except Exception as e:
        logger.error("Chat request failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}",
        )
