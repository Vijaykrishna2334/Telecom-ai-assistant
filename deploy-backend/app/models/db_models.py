"""
SQLAlchemy ORM models for Telecom AI Assistant.
Defines database tables for users, sessions, messages, plans, and billing.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, 
    String, Text, JSON, Index
)
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions: Mapped[List["ChatSession"]] = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    billing_records: Mapped[List["Billing"]] = relationship("Billing", back_populates="user", cascade="all, delete-orphan")
    subscriptions: Mapped[List["UserPlan"]] = relationship("UserPlan", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"


class ChatSession(Base):
    """Chat session model for conversation tracking."""
    __tablename__ = "chat_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    is_voice_session: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="sessions")
    messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    # Index for faster session lookups
    __table_args__ = (
        Index("idx_session_user_active", "user_id", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, token='{self.session_token[:8]}...')>"


class ChatMessage(Base):
    """Individual chat message model."""
    __tablename__ = "chat_messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rag_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # RAG context used
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Response latency
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
    
    # Index for faster message retrieval
    __table_args__ = (
        Index("idx_message_session_created", "session_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, role='{self.role}')>"


class Plan(Base):
    """Telecom plan model."""
    __tablename__ = "plans"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plan_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # 'prepaid', 'postpaid', 'fiber', 'airfiber'
    price: Mapped[float] = mapped_column(Float, nullable=False)
    validity_days: Mapped[int] = mapped_column(Integer, default=30)
    data_gb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Data in GB
    data_description: Mapped[str] = mapped_column(String(100), nullable=False)  # "2GB/day", "Unlimited"
    calls: Mapped[str] = mapped_column(String(100), nullable=False)  # "Unlimited", "1000 mins"
    sms: Mapped[str] = mapped_column(String(100), default="100 SMS/day")
    features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Additional features as JSON
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions: Mapped[List["UserPlan"]] = relationship("UserPlan", back_populates="plan")
    
    def __repr__(self) -> str:
        return f"<Plan(id={self.id}, name='{self.name}', price={self.price})>"


class UserPlan(Base):
    """User plan subscription model."""
    __tablename__ = "user_plans"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("plans.id"), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
    plan: Mapped["Plan"] = relationship("Plan", back_populates="subscriptions")
    
    # Index for active subscriptions
    __table_args__ = (
        Index("idx_userplan_user_active", "user_id", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<UserPlan(user_id={self.user_id}, plan_id={self.plan_id})>"


class Billing(Base):
    """Billing and payment records."""
    __tablename__ = "billing"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    status: Mapped[str] = mapped_column(String(20), default="pending")  # 'pending', 'paid', 'failed', 'refunded'
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'upi', 'card', 'netbanking'
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="billing_records")
    
    # Index for billing queries
    __table_args__ = (
        Index("idx_billing_user_status", "user_id", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<Billing(id={self.id}, amount={self.amount}, status='{self.status}')>"


class RAGQueryLog(Base):
    """Log of RAG queries for analytics and caching."""
    __tablename__ = "rag_query_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    expanded_query: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    documents_retrieved: Mapped[int] = mapped_column(Integer, default=0)
    relevant_documents: Mapped[int] = mapped_column(Integer, default=0)
    crag_action: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'correct', 'ambiguous', 'incorrect'
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Index for analytics
    __table_args__ = (
        Index("idx_rag_created", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<RAGQueryLog(id={self.id}, query='{self.query[:30]}...')>"
