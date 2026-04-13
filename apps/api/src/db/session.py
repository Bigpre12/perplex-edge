import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

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

# Auto-switch Supabase pooler URLs from Session Mode (5432) to Transaction Mode (6543)
if "pooler" in DATABASE_URL and ":5432" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace(":5432", ":6543", 1)

_is_pg = "postgresql" in DATABASE_URL

logger = logging.getLogger(__name__)

# --- ASYNC ENGINE SETUP ---
if _is_pg:
    connect_args = {"prepared_statement_cache_size": 0}
else:
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_size=3,
    max_overflow=2,
    pool_recycle=300,
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

# Backward-compatible name used by some routers/services
async_session_maker = AsyncSessionLocal

# --- DEPENDENCIES ---
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async database sessions."""
    async with AsyncSessionLocal() as session:
        yield session

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Alias for get_db for backward compatibility."""
    async with AsyncSessionLocal() as session:
        yield session

# Legacy shim for SessionLocal if needed by external scripts (minimizing usage)
# In a pure async app, this should eventually be removed.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as sync_sessionmaker

sync_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://").replace("sqlite+aiosqlite://", "sqlite://")
_sync_connect_args = {"check_same_thread": False} if "sqlite" in sync_url else {}
sync_engine = create_engine(sync_url, connect_args=_sync_connect_args)
SessionLocal = sync_sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)
