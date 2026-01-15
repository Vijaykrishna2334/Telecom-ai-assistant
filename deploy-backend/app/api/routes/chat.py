"""
Chat API endpoints with database persistence and Redis caching.
"""
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from app.core import settings
from app.core.logging import get_logger
from app.core.security import generate_session_id
from app.models.schemas import ChatRequest, ChatResponse
from app.models.database import get_db_session, is_db_available
from app.models import crud
from app.services.llm import create_chat_prompt, ollama_client
from app.services.rag import knowledge_base
from app.services.cache import cache_service

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

    Features:
    - Stores messages in PostgreSQL for history
    - Caches RAG responses in Redis for faster repeated queries
    - Returns RAG context for debugging

    Args:
        request: Chat request with message and optional session_id

    Returns:
        Chat response with assistant message
    """
    start_time = time.time()
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or generate_session_id()
        db_session_id = None
        conversation_id = 1

        logger.info(
            "Processing chat message",
            session_id=session_id,
            message_length=len(request.message),
        )

        # Try to get or create database session
        if is_db_available():
            try:
                async with get_db_session() as db:
                    # Get or create chat session
                    chat_session = await crud.get_or_create_session(
                        db, session_token=session_id
                    )
                    db_session_id = chat_session.id
                    conversation_id = chat_session.id
                    
                    # Store user message
                    await crud.add_message(
                        db,
                        session_id=db_session_id,
                        role="user",
                        content=request.message
                    )
            except Exception as db_error:
                logger.warning("Database operation failed, continuing without persistence", error=str(db_error))

        # Check Redis cache for similar queries
        cached_response = await cache_service.get_rag_response(request.message)
        if cached_response:
            logger.info("Using cached RAG response", session_id=session_id)
            assistant_message = cached_response.get("response", "")
            context = cached_response.get("context")
            
            # Still store the response in DB even if cached
            if is_db_available() and db_session_id:
                try:
                    async with get_db_session() as db:
                        await crud.add_message(
                            db,
                            session_id=db_session_id,
                            role="assistant",
                            content=assistant_message,
                            rag_context=context,
                            response_time_ms=int((time.time() - start_time) * 1000)
                        )
                except Exception:
                    pass  # Non-critical, continue
            
            return ChatResponse(
                message=assistant_message,
                session_id=session_id,
                conversation_id=conversation_id,
                rag_context=context,
            )

        # Get relevant context from knowledge base (CRAG)
        context = await knowledge_base.get_context_for_query(
            request.message, 
            conversation_history=request.history
        )

        # Create prompt with context and history
        messages = create_chat_prompt(
            user_message=request.message,
            context=context if context else None,
            conversation_history=request.history,
        )

        # Generate response from Ollama LLM
        response = await ollama_client.chat(messages=messages)

        # Extract assistant message
        assistant_message = response.get("message", {}).get("content", "")
        response_time_ms = int((time.time() - start_time) * 1000)

        # Cache the response in Redis for future similar queries
        if context:  # Only cache if we had RAG context
            await cache_service.cache_rag_response(
                query=request.message,
                response=assistant_message,
                context=context
            )

        # Store assistant response in database
        if is_db_available() and db_session_id:
            try:
                async with get_db_session() as db:
                    await crud.add_message(
                        db,
                        session_id=db_session_id,
                        role="assistant",
                        content=assistant_message,
                        rag_context=context,
                        response_time_ms=response_time_ms
                    )
            except Exception as db_error:
                logger.warning("Failed to store response in DB", error=str(db_error))

        logger.info(
            "Chat response generated",
            session_id=session_id,
            response_length=len(assistant_message),
            response_time_ms=response_time_ms,
        )

        return ChatResponse(
            message=assistant_message,
            session_id=session_id,
            conversation_id=conversation_id,
            rag_context=context if context else None,
        )

    except Exception as e:
        logger.error("Chat request failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}",
        )


@router.get(
    "/chat/history/{session_id}",
    status_code=status.HTTP_200_OK,
    tags=["Chat"],
)
async def get_chat_history(session_id: str, limit: int = 50):
    """
    Get chat history for a session.

    Args:
        session_id: Session token
        limit: Maximum number of messages to return

    Returns:
        List of messages in the session
    """
    if not is_db_available():
        return {"messages": [], "error": "Database not available"}

    try:
        async with get_db_session() as db:
            history = await crud.get_chat_history(db, session_id, limit)
            return {"messages": history, "session_id": session_id}
    except Exception as e:
        logger.error("Failed to get chat history", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat history: {str(e)}",
        )
