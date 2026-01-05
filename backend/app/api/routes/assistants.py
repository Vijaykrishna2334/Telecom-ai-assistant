"""
Assistant management endpoints.
"""
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class Assistant(BaseModel):
    """Assistant model."""
    
    id: int
    name: str
    type: str
    description: str
    is_active: bool
    created_at: datetime


@router.get(
    "/assistants",
    response_model=List[Assistant],
    status_code=status.HTTP_200_OK,
    tags=["Assistants"],
)
async def list_assistants() -> List[Assistant]:
    """
    List available AI assistants.

    Returns:
        List of assistants
    """
    # Mock assistants
    return [
        Assistant(
            id=1,
            name="General Support",
            type="text",
            description="General customer support assistant",
            is_active=True,
            created_at=datetime.now(timezone.utc),
        ),
        Assistant(
            id=2,
            name="Voice Assistant",
            type="voice",
            description="Voice-enabled customer support assistant",
            is_active=True,
            created_at=datetime.now(timezone.utc),
        ),
    ]


@router.post(
    "/assistants",
    response_model=Assistant,
    status_code=status.HTTP_201_CREATED,
    tags=["Assistants"],
)
async def create_assistant(assistant: Assistant) -> Assistant:
    """
    Create a new assistant.

    Args:
        assistant: Assistant details

    Returns:
        Created assistant
    """
    # Mock creation
    return assistant
