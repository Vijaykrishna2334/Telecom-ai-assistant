"""
Models package for Pydantic schemas and database models.
"""
from app.models.database import close_db, init_db, get_db, get_db_session, is_db_available, check_db_health
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    HealthCheck,
    PlanResponse,
    ReadinessCheck,
    VoiceSessionCreate,
    VoiceSessionResponse,
)
from app.models.db_models import (
    Base,
    User,
    ChatSession,
    ChatMessage,
    Plan,
    UserPlan,
    Billing,
    RAGQueryLog,
)
from app.models import crud

__all__ = [
    # Database
    "init_db",
    "close_db",
    "get_db",
    "get_db_session",
    "is_db_available",
    "check_db_health",
    # Pydantic Schemas
    "ChatRequest",
    "ChatResponse",
    "HealthCheck",
    "PlanResponse",
    "ReadinessCheck",
    "VoiceSessionCreate",
    "VoiceSessionResponse",
    # ORM Models
    "Base",
    "User",
    "ChatSession",
    "ChatMessage",
    "Plan",
    "UserPlan",
    "Billing",
    "RAGQueryLog",
    # CRUD
    "crud",
]
