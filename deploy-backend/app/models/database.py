"""
Database initialization and connection management.
Async SQLAlchemy engine with PostgreSQL using asyncpg.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import get_logger
from app.models.db_models import Base

logger = get_logger(__name__)

# Global database engine and session factory
_engine = None
_async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_database_url() -> str:
    """
    Get the async database URL.
    Converts postgresql:// to postgresql+asyncpg:// for async support.
    """
    url = settings.database_url
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


async def init_db() -> None:
    """
    Initialize database connections and create tables.
    
    Creates async engine with connection pooling and creates all tables
    defined in the ORM models.
    """
    global _engine, _async_session_factory
    
    try:
        database_url = get_database_url()
        
        # Create async engine with connection pooling
        _engine = create_async_engine(
            database_url,
            echo=settings.debug,  # Log SQL in debug mode
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_pre_ping=True,  # Check connection health before use
            pool_recycle=3600,  # Recycle connections after 1 hour
        )
        
        # Create session factory
        _async_session_factory = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        # Create all tables
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully", url=database_url.split("@")[1] if "@" in database_url else database_url)
        
    except Exception as e:
        logger.warning(
            "Database initialization failed - running without PostgreSQL",
            error=str(e),
            hint="Start PostgreSQL with: docker-compose up -d db"
        )
        # App can still run without database (using mock data)
        _engine = None
        _async_session_factory = None


async def close_db() -> None:
    """
    Close database connections gracefully.
    
    Disposes the connection pool and closes all connections.
    """
    global _engine, _async_session_factory
    
    if _engine:
        await _engine.dispose()
        logger.info("Database connections closed")
    
    _engine = None
    _async_session_factory = None


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session.
    
    Usage:
        async with get_db_session() as session:
            result = await session.execute(query)
    
    Yields:
        AsyncSession: Database session with automatic commit/rollback
    
    Raises:
        RuntimeError: If database is not initialized
    """
    if _async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    session = _async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session injection.
    
    Usage in routes:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    
    Yields:
        AsyncSession: Database session
    """
    if _async_session_factory is None:
        # Return None to allow endpoints to work without database
        yield None
        return
    
    session = _async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


def is_db_available() -> bool:
    """Check if database is available."""
    return _engine is not None and _async_session_factory is not None


async def check_db_health() -> bool:
    """
    Check database health by executing a simple query.
    
    Returns:
        bool: True if database is healthy, False otherwise
    """
    if not is_db_available():
        return False
    
    try:
        async with get_db_session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return False
