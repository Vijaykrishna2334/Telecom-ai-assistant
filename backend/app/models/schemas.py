"""
Pydantic schemas for API request/response models.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Health Check Schemas
class HealthCheck(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Check timestamp")


class ReadinessCheck(BaseModel):
    """Readiness check response with service status."""
    status: str = Field(..., description="Readiness status")
    services: Dict[str, bool] = Field(..., description="Service availability")
    timestamp: datetime = Field(..., description="Check timestamp")


# Chat Schemas
class ChatRequest(BaseModel):
    """Chat message request."""
    message: str = Field(..., min_length=1, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    history: Optional[List[Dict[str, str]]] = Field(None, description="Conversation history for context")


class ChatResponse(BaseModel):
    """Chat message response."""
    message: str = Field(..., description="Assistant response message")
    session_id: str = Field(..., description="Session ID")
    conversation_id: int = Field(..., description="Conversation ID")
    rag_context: Optional[str] = Field(None, description="RAG context used for response (debug)")


# Plan Schemas
class PlanResponse(BaseModel):
    """Telecom plan response."""
    id: int = Field(..., description="Database ID")
    plan_id: str = Field(..., description="Plan identifier")
    name: str = Field(..., description="Plan name")
    price: float = Field(..., description="Plan price")
    data: str = Field(..., description="Data allowance")
    calls: str = Field(..., description="Calls allowance")
    sms: str = Field(..., description="SMS allowance")
    features: List[str] = Field(default_factory=list, description="Plan features")
    is_active: bool = Field(True, description="Whether plan is active")
    created_at: datetime = Field(..., description="Creation timestamp")


# Voice Session Schemas
class VoiceSessionCreate(BaseModel):
    """Voice session creation request."""
    user_id: Optional[str] = Field(None, description="User identifier")
    audio_format: str = Field("wav", description="Audio format")
    sample_rate: int = Field(16000, description="Sample rate in Hz")


class VoiceSessionResponse(BaseModel):
    """Voice session response."""
    id: int = Field(..., description="Session database ID")
    conversation_id: int = Field(..., description="Associated conversation ID")
    session_id: str = Field(..., description="Session identifier")
    audio_format: str = Field(..., description="Audio format")
    sample_rate: int = Field(..., description="Sample rate in Hz")
    duration_seconds: float = Field(0.0, description="Session duration")
    created_at: datetime = Field(..., description="Creation timestamp")
