"""
CRUD (Create, Read, Update, Delete) operations for database models.
Provides async database operations for all entities.
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.models.db_models import (
    User, ChatSession, ChatMessage, Plan, UserPlan, Billing, RAGQueryLog
)

logger = get_logger(__name__)


# ============================================================================
# User CRUD Operations
# ============================================================================

async def create_user(
    session: AsyncSession,
    email: str,
    name: str,
    password: str,
    phone: Optional[str] = None
) -> User:
    """Create a new user with hashed password."""
    # Simple password hashing (use passlib in production)
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    user = User(
        email=email,
        name=name,
        hashed_password=hashed,
        phone=phone
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    logger.info("Created user", user_id=user.id, email=email)
    return user


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """Get user by email."""
    result = await session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_phone(session: AsyncSession, phone: str) -> Optional[User]:
    """Get user by phone number."""
    result = await session.execute(
        select(User).where(User.phone == phone)
    )
    return result.scalar_one_or_none()


async def update_user(
    session: AsyncSession,
    user_id: int,
    **kwargs
) -> Optional[User]:
    """Update user fields."""
    await session.execute(
        update(User).where(User.id == user_id).values(**kwargs)
    )
    return await get_user_by_id(session, user_id)


# ============================================================================
# Chat Session CRUD Operations
# ============================================================================

def generate_session_token() -> str:
    """Generate a unique session token."""
    return secrets.token_hex(32)


async def create_chat_session(
    session: AsyncSession,
    user_id: Optional[int] = None,
    is_voice: bool = False,
    session_token: Optional[str] = None
) -> ChatSession:
    """Create a new chat session."""
    token = session_token or generate_session_token()
    
    chat_session = ChatSession(
        session_token=token,
        user_id=user_id,
        is_voice_session=is_voice
    )
    session.add(chat_session)
    await session.flush()
    await session.refresh(chat_session)
    logger.info("Created chat session", session_id=chat_session.id, token=token[:8])
    return chat_session


async def get_session_by_token(
    session: AsyncSession,
    token: str
) -> Optional[ChatSession]:
    """Get chat session by token."""
    result = await session.execute(
        select(ChatSession)
        .where(ChatSession.session_token == token)
        .options(selectinload(ChatSession.messages))
    )
    return result.scalar_one_or_none()


async def get_session_by_id(
    session: AsyncSession,
    session_id: int
) -> Optional[ChatSession]:
    """Get chat session by ID."""
    result = await session.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id)
        .options(selectinload(ChatSession.messages))
    )
    return result.scalar_one_or_none()


async def get_or_create_session(
    session: AsyncSession,
    session_token: Optional[str] = None,
    user_id: Optional[int] = None,
    is_voice: bool = False
) -> ChatSession:
    """Get existing session by token or create a new one."""
    if session_token:
        existing = await get_session_by_token(session, session_token)
        if existing and existing.is_active:
            return existing
    
    return await create_chat_session(session, user_id, is_voice, session_token)


async def end_chat_session(session: AsyncSession, token: str) -> bool:
    """End a chat session."""
    result = await session.execute(
        update(ChatSession)
        .where(ChatSession.session_token == token)
        .values(is_active=False, ended_at=datetime.utcnow())
    )
    return result.rowcount > 0


async def get_user_sessions(
    session: AsyncSession,
    user_id: int,
    limit: int = 10
) -> List[ChatSession]:
    """Get recent sessions for a user."""
    result = await session.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


# ============================================================================
# Chat Message CRUD Operations
# ============================================================================

async def add_message(
    session: AsyncSession,
    session_id: int,
    role: str,
    content: str,
    rag_context: Optional[str] = None,
    response_time_ms: Optional[int] = None
) -> ChatMessage:
    """Add a message to a chat session."""
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        rag_context=rag_context,
        response_time_ms=response_time_ms
    )
    session.add(message)
    await session.flush()
    await session.refresh(message)
    return message


async def get_session_messages(
    session: AsyncSession,
    session_id: int,
    limit: int = 50
) -> List[ChatMessage]:
    """Get messages for a session, ordered by creation time."""
    result = await session.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_chat_history(
    session: AsyncSession,
    session_token: str,
    limit: int = 20
) -> List[Dict[str, str]]:
    """Get chat history formatted for LLM context."""
    chat_session = await get_session_by_token(session, session_token)
    if not chat_session:
        return []
    
    messages = await get_session_messages(session, chat_session.id, limit)
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]


# ============================================================================
# Plan CRUD Operations
# ============================================================================

async def get_all_plans(
    session: AsyncSession,
    category: Optional[str] = None,
    active_only: bool = True
) -> List[Plan]:
    """Get all plans, optionally filtered by category."""
    query = select(Plan)
    
    if active_only:
        query = query.where(Plan.is_active == True)
    
    if category:
        query = query.where(Plan.category == category)
    
    query = query.order_by(Plan.price.asc())
    
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_plan_by_id(session: AsyncSession, plan_id: int) -> Optional[Plan]:
    """Get plan by ID."""
    result = await session.execute(
        select(Plan).where(Plan.id == plan_id)
    )
    return result.scalar_one_or_none()


async def get_plan_by_plan_id(session: AsyncSession, plan_id: str) -> Optional[Plan]:
    """Get plan by plan_id string."""
    result = await session.execute(
        select(Plan).where(Plan.plan_id == plan_id)
    )
    return result.scalar_one_or_none()


async def create_plan(
    session: AsyncSession,
    plan_id: str,
    name: str,
    category: str,
    price: float,
    data_description: str,
    calls: str,
    **kwargs
) -> Plan:
    """Create a new plan."""
    plan = Plan(
        plan_id=plan_id,
        name=name,
        category=category,
        price=price,
        data_description=data_description,
        calls=calls,
        **kwargs
    )
    session.add(plan)
    await session.flush()
    await session.refresh(plan)
    logger.info("Created plan", plan_id=plan.plan_id, name=name)
    return plan


async def search_plans(
    session: AsyncSession,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    category: Optional[str] = None
) -> List[Plan]:
    """Search plans by criteria."""
    query = select(Plan).where(Plan.is_active == True)
    
    if min_price is not None:
        query = query.where(Plan.price >= min_price)
    if max_price is not None:
        query = query.where(Plan.price <= max_price)
    if category:
        query = query.where(Plan.category == category)
    
    query = query.order_by(Plan.price.asc())
    
    result = await session.execute(query)
    return list(result.scalars().all())


# ============================================================================
# Billing CRUD Operations
# ============================================================================

async def create_billing_record(
    session: AsyncSession,
    user_id: int,
    amount: float,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None
) -> Billing:
    """Create a billing record."""
    billing = Billing(
        user_id=user_id,
        amount=amount,
        description=description,
        due_date=due_date or (datetime.utcnow() + timedelta(days=30))
    )
    session.add(billing)
    await session.flush()
    await session.refresh(billing)
    return billing


async def get_user_billing(
    session: AsyncSession,
    user_id: int,
    status: Optional[str] = None
) -> List[Billing]:
    """Get billing records for a user."""
    query = select(Billing).where(Billing.user_id == user_id)
    
    if status:
        query = query.where(Billing.status == status)
    
    query = query.order_by(Billing.created_at.desc())
    
    result = await session.execute(query)
    return list(result.scalars().all())


async def update_billing_status(
    session: AsyncSession,
    billing_id: int,
    status: str,
    transaction_id: Optional[str] = None,
    payment_method: Optional[str] = None
) -> Optional[Billing]:
    """Update billing status after payment."""
    values = {"status": status}
    
    if status == "paid":
        values["paid_at"] = datetime.utcnow()
    if transaction_id:
        values["transaction_id"] = transaction_id
    if payment_method:
        values["payment_method"] = payment_method
    
    await session.execute(
        update(Billing).where(Billing.id == billing_id).values(**values)
    )
    
    result = await session.execute(
        select(Billing).where(Billing.id == billing_id)
    )
    return result.scalar_one_or_none()


# ============================================================================
# RAG Query Log Operations
# ============================================================================

async def log_rag_query(
    session: AsyncSession,
    query: str,
    response_time_ms: int,
    documents_retrieved: int = 0,
    relevant_documents: int = 0,
    crag_action: Optional[str] = None,
    expanded_query: Optional[str] = None,
    cache_hit: bool = False
) -> RAGQueryLog:
    """Log a RAG query for analytics."""
    log_entry = RAGQueryLog(
        query=query,
        expanded_query=expanded_query,
        documents_retrieved=documents_retrieved,
        relevant_documents=relevant_documents,
        crag_action=crag_action,
        response_time_ms=response_time_ms,
        cache_hit=cache_hit
    )
    session.add(log_entry)
    await session.flush()
    return log_entry


async def get_rag_stats(
    session: AsyncSession,
    hours: int = 24
) -> Dict[str, Any]:
    """Get RAG query statistics for the last N hours."""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    result = await session.execute(
        select(
            func.count(RAGQueryLog.id).label("total_queries"),
            func.avg(RAGQueryLog.response_time_ms).label("avg_response_time"),
            func.sum(func.cast(RAGQueryLog.cache_hit, Integer)).label("cache_hits"),
        ).where(RAGQueryLog.created_at >= since)
    )
    
    row = result.one()
    return {
        "total_queries": row.total_queries or 0,
        "avg_response_time_ms": round(row.avg_response_time or 0, 2),
        "cache_hits": row.cache_hits or 0,
        "cache_hit_rate": round((row.cache_hits or 0) / max(row.total_queries or 1, 1) * 100, 2)
    }
