"""
Main FastAPI application entry point for Telecom AI Assistant.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import assistants, calls, chat, health, voice, knowledge
from app.api.websockets import chat_ws, voice_ws, realtime_voice
from app.core import configure_logging, get_logger, settings
from app.models import close_db, init_db
from app.services.cache import cache_service
from app.services.llm import function_router, ollama_client
from app.services.rag import knowledge_base
from app.services.telecom import (
    check_billing_status,
    escalate_to_agent,
    fetch_plan_data,
    initiate_speed_test,
    verify_network_coverage,
)
from app.services.voice import voice_pipeline

# Configure logging
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting Telecom AI Assistant", version=settings.api_version)
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Connect to Redis (optional - app works without it)
        try:
            await cache_service.connect()
            logger.info("Cache service connected")
        except Exception as cache_error:
            logger.warning("Redis not available, running without cache", error=str(cache_error))
        
        # Initialize knowledge base
        await knowledge_base.initialize()
        logger.info("Knowledge base initialized")
        
        # Initialize voice pipeline
        await voice_pipeline.initialize()
        logger.info("Voice pipeline initialized")
        
        # Register telecom functions
        function_router.register("fetch_plan_data", fetch_plan_data)
        function_router.register("check_billing_status", check_billing_status)
        function_router.register("verify_network_coverage", verify_network_coverage)
        function_router.register("initiate_speed_test", initiate_speed_test)
        function_router.register("escalate_to_agent", escalate_to_agent)
        logger.info("Functions registered")
        
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error("Failed to initialize application", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Telecom AI Assistant")
    
    try:
        await cache_service.disconnect()
        await ollama_client.close()
        await close_db()
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error("Error during shutdown", error=str(e))


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Intelligent Telecommunication Support Bot with Voice AI",
    version=settings.api_version,
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, prefix=settings.api_prefix, tags=["Chat"])
app.include_router(voice.router, prefix=settings.api_prefix, tags=["Voice"])
app.include_router(assistants.router, prefix=settings.api_prefix, tags=["Assistants"])
app.include_router(calls.router, prefix=settings.api_prefix, tags=["Plans"])
app.include_router(knowledge.router, prefix=f"{settings.api_prefix}/knowledge", tags=["Knowledge Base"])

# Include WebSocket routers
app.include_router(chat_ws.router, tags=["WebSocket"])
app.include_router(voice_ws.router, tags=["WebSocket"])
app.include_router(realtime_voice.router, tags=["WebSocket"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.api_version,
        "docs": f"{settings.api_prefix}/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
