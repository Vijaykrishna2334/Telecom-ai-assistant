"""
Health check and readiness endpoints.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, status
from app.core.config import settings
from app.models.schemas import HealthCheck, ReadinessCheck
from app.services.cache import cache_service
from app.services.llm import ollama_client

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheck,
    status_code=status.HTTP_200_OK,
    tags=["Health"],
)
async def health_check() -> HealthCheck:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return HealthCheck(
        status="healthy",
        version=settings.api_version,
        timestamp=datetime.now(timezone.utc),
    )


@router.get(
    "/ready",
    response_model=ReadinessCheck,
    status_code=status.HTTP_200_OK,
    tags=["Health"],
)
async def readiness_check() -> ReadinessCheck:
    """
    Readiness check endpoint that verifies dependent services.

    Returns:
        Readiness status with service availability
    """
    services = {
        "redis": await cache_service.check_health(),
        "ollama": await ollama_client.check_health(),
        "database": True,  # Would check DB connection in production
        "chromadb": True,  # Would check ChromaDB connection in production
    }

    all_ready = all(services.values())
    status_code = "ready" if all_ready else "not_ready"

    return ReadinessCheck(
        status=status_code,
        services=services,
        timestamp=datetime.now(timezone.utc),
    )
