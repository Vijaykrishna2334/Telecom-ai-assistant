"""
WebSocket handler for real-time text chat.
"""
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.logging import get_logger
from app.services.llm import create_chat_prompt, ollama_client
from app.services.rag import knowledge_base

logger = get_logger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self) -> None:
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """Connect a new WebSocket client."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info("WebSocket connected", session_id=session_id)

    def disconnect(self, session_id: str) -> None:
        """Disconnect a WebSocket client."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info("WebSocket disconnected", session_id=session_id)

    async def send_message(self, message: str, session_id: str) -> None:
        """Send a message to a specific client."""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/chat/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str) -> None:
    """
    WebSocket endpoint for real-time chat.

    Args:
        websocket: WebSocket connection
        session_id: Session identifier
    """
    await manager.connect(websocket, session_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            logger.info("Received message", session_id=session_id, length=len(data))

            # Get context from knowledge base
            context = await knowledge_base.get_context_for_query(data)

            # Create prompt with context
            messages = create_chat_prompt(
                user_message=data,
                context=context if context else None,
            )

            # Stream response from Ollama LLM
            response_text = ""
            chat_gen = await ollama_client.chat(messages=messages, stream=True)

            async for chunk in chat_gen:
                response_text += chunk
                await manager.send_message(chunk, session_id)

            logger.info(
                "Sent response",
                session_id=session_id,
                length=len(response_text),
            )

    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info("Client disconnected", session_id=session_id)
    except Exception as e:
        logger.error("WebSocket error", session_id=session_id, error=str(e))
        manager.disconnect(session_id)
