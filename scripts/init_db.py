#!/usr/bin/env python3
"""
Initialize database with tables.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core import get_logger
from app.models import init_db

logger = get_logger(__name__)


async def main() -> None:
    """Initialize database tables."""
    try:
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
