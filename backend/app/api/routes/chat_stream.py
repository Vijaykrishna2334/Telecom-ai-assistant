"""
Streaming Chat API endpoint.

Provides Server-Sent Events (SSE) streaming for real-time token-by-token responses.
"""
import json
from typing import AsyncGenerator

from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse
from app.core.logging import get_logger
from app.core.security import generate_session_id
from app.models.schemas import ChatRequest
from app.services.llm import create_chat_prompt, ollama_client
from app.services.rag import knowledge_base

logger = get_logger(__name__)
router = APIRouter()


async def generate_stream(
    messages: list,
    session_id: str,
    context: str | None = None,
) -> AsyncGenerator[str, None]:
    """
    Generate streaming response tokens.

    Args:
        messages: Chat messages for LLM
        session_id: Session identifier
        context: Optional RAG context

    Yields:
        SSE formatted data chunks
    """
    full_response = ""
    
    try:
        # Stream tokens from Ollama
        async for token in ollama_client.chat(messages=messages, stream=True):
            full_response += token
            # Format as SSE data
            data = json.dumps({"token": token, "session_id": session_id})
            yield f"data: {data}\n\n"
        
        # Send completion signal with full response and context
        done_data = json.dumps({
            "done": True,
            "message": full_response,
            "session_id": session_id,
            "rag_context": context,
        })
        yield f"data: {done_data}\n\n"
        
    except Exception as e:
        logger.error("Streaming error", error=str(e))
        error_data = json.dumps({"error": str(e)})
        yield f"data: {error_data}\n\n"


@router.post(
    "/chat/stream",
    status_code=status.HTTP_200_OK,
    tags=["Chat"],
    summary="Stream chat response",
    description="Stream AI response token-by-token using Server-Sent Events (SSE).",
)
async def stream_chat(request: ChatRequest) -> StreamingResponse:
    """
    Stream chat response token by token.

    This endpoint uses Server-Sent Events (SSE) to stream the AI response
    word-by-word as it's being generated, providing a ChatGPT-like experience.

    Args:
        request: Chat request with message and optional session_id

    Returns:
        StreamingResponse with SSE formatted data
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or generate_session_id()

        logger.info(
            "Starting streaming chat",
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

        # Return streaming response
        return StreamingResponse(
            generate_stream(messages, session_id, context),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            },
        )

    except Exception as e:
        logger.error("Stream chat request failed", error=str(e))
        # Return error as SSE
        async def error_stream():
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
