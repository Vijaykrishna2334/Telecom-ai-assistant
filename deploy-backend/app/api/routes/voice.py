"""
Voice session API endpoints.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from app.core.logging import get_logger
from app.core.security import generate_session_id
from app.models.schemas import VoiceSessionCreate, VoiceSessionResponse

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/voice/sessions",
    response_model=VoiceSessionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Voice"],
)
async def create_voice_session(
    request: VoiceSessionCreate,
) -> VoiceSessionResponse:
    """
    Create a new voice session.

    Args:
        request: Voice session creation request

    Returns:
        Voice session details
    """
    try:
        session_id = generate_session_id()

        logger.info("Creating voice session", session_id=session_id, user_id=request.user_id)

        # Mock response - would create actual DB records in production
        return VoiceSessionResponse(
            id=1,
            conversation_id=1,
            session_id=session_id,
            audio_format=request.audio_format,
            sample_rate=request.sample_rate,
            duration_seconds=0.0,
            created_at=datetime.now(timezone.utc),
        )

    except Exception as e:
        logger.error("Failed to create voice session", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create voice session: {str(e)}",
        )


@router.get(
    "/voice/sessions/{session_id}",
    response_model=VoiceSessionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Voice"],
)
async def get_voice_session(session_id: str) -> VoiceSessionResponse:
    """
    Get voice session details.

    Args:
        session_id: Session ID

    Returns:
        Voice session details
    """
    logger.info("Getting voice session", session_id=session_id)

    # Mock response
    return VoiceSessionResponse(
        id=1,
        conversation_id=1,
        session_id=session_id,
        audio_format="wav",
        sample_rate=16000,
        duration_seconds=0.0,
        created_at=datetime.now(timezone.utc),
    )


@router.delete(
    "/voice/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Voice"],
)
async def delete_voice_session(session_id: str) -> None:
    """
    End a voice session.

    Args:
        session_id: Session ID
    """
    logger.info("Deleting voice session", session_id=session_id)
    # Would update DB record in production
    return None
