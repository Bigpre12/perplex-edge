import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from db.base import Base # Re-export Base for convenience

# --- CONFIGURATION ---
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'perplex_local.db'))}"
)

# Fix connection string for asyncpg/aiosqlite
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("sqlite://"):
    DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://", 1)

logger = logging.getLogger(__name__)

# --- ASYNC ENGINE SETUP ---
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_async_engine(
    DATABASE_URL, 
    connect_args=connect_args,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

# AsyncSessionLocal is the primary session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Export as async_session_maker for backward compatibility with existing services
async_session_maker = AsyncSessionLocal

# Standard exports for various utilities
__all__ = ["engine", "AsyncSessionLocal", "async_session_maker", "get_db", "get_async_db", "Base", "SessionLocal"]

# --- DEPENDENCIES ---
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async database sessions."""
    async with AsyncSessionLocal() as session:
        yield session

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Alias for get_db for backward compatibility."""
    async with AsyncSessionLocal() as session:
        yield session

# Legacy alias: many routers/services still import async_session_maker
import contextlib

@contextlib.asynccontextmanager
async def async_session_maker():
    """Backward-compatible async context manager for sessions."""
    async with AsyncSessionLocal() as session:
        yield session

# Legacy shim for SessionLocal if needed by external scripts (minimizing usage)
# In a pure async app, this should eventually be removed.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as sync_sessionmaker

sync_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://").replace("sqlite+aiosqlite://", "sqlite://")
sync_engine = create_engine(sync_url, connect_args=connect_args if "sqlite" in sync_url else {})
SessionLocal = sync_sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)
