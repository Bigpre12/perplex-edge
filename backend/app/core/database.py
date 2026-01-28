"""Async database configuration for SQLAlchemy + asyncpg."""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Lazy initialization for engine
_engine: Optional[AsyncEngine] = None
_async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine() -> AsyncEngine:
    """Get or create the async engine (lazy initialization)."""
    global _engine
    if _engine is None:
        settings = get_settings()
        logger.info(f"Creating async engine with URL pattern: postgresql+asyncpg://...")
        _engine = create_async_engine(
            settings.database_url_async,
            echo=settings.is_development,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """Get or create the session maker (lazy initialization)."""
    global _async_session_maker
    if _async_session_maker is None:
        _async_session_maker = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session."""
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def db_lifespan(app: FastAPI):
    """Database lifespan - initialize on startup, cleanup on shutdown."""
    global _engine
    
    logger.info("Initializing database connection...")
    try:
        # Create engine (validates URL format)
        engine = get_engine()
        # Test connection
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        # Don't crash - let app start without DB for health checks
    
    yield
    
    # Cleanup
    if _engine is not None:
        await _engine.dispose()
        logger.info("Database connection closed")
