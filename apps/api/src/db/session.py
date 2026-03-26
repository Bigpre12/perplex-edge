import os
import logging
logger = logging.getLogger(__name__)
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from db.base import Base # Re-export Base for convenience

# --- CONFIGURATION ---
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./data/perplex_local.db")

if DATABASE_URL.startswith("sqlite") and "aiosqlite" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://") and "asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Fix for Supabase Transaction Pooler (Port 6543)
if ":6543" in DATABASE_URL and "prepared_statement_cache_size" not in DATABASE_URL:
    separator = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL += f"{separator}prepared_statement_cache_size=0"

# Fix for asyncpg: strip 'sslmode' from URL as it's not supported as a query param by asyncpg
if "sslmode=" in DATABASE_URL:
    import re
    DATABASE_URL = re.sub(r"[?&]sslmode=[^&]*", "", DATABASE_URL)

# Redacted logging for debugging
db_url = os.environ.get("DATABASE_URL", "NOT SET")
if db_url != "NOT SET":
    # host-only log to prevent leaking secrets in deployment logs
    try:
        from urllib.parse import urlparse
        # urlparse handles http:// better for simple host extraction
        parsed = urlparse(db_url.replace("postgresql+asyncpg://", "http://").replace("postgresql://", "http://"))
        logger.info(f"Database Initialization: Attempting connection to host={parsed.hostname} user={parsed.username} port={parsed.port}")
    except Exception:
        logger.info(f"Database Initialization: Connecting to redacted URL (Parsing failed)")
else:
    logger.warning("Database Initialization: DATABASE_URL is NOT SET in current environment!")

# --- ASYNC ENGINE SETUP ---
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_async_engine(
    DATABASE_URL, 
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True if "sqlite" not in DATABASE_URL else False,
    # Supabase/Postgres Connection Pool Optimization
    pool_size=3,              # Keep it small to avoid MaxClientsInSessionMode
    max_overflow=0,           # Strictly limit to pool_size
    pool_recycle=1800,        # Recycle connections every 30 mins
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Standard exports for various utilities
__all__ = ["engine", "AsyncSessionLocal", "get_db", "get_async_db", "Base", "SessionLocal"]

from contextlib import asynccontextmanager

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
# Note: This is an alias to the factory, allowing 'async with async_session_maker()'
async_session_maker = AsyncSessionLocal

# Legacy shim for SessionLocal if needed by external scripts (minimizing usage)
# In a pure async app, this should eventually be removed.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as sync_sessionmaker

sync_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://").replace("sqlite+aiosqlite://", "sqlite://")
sync_engine = create_engine(
    sync_url, 
    connect_args=connect_args if "sqlite" in sync_url else {},
    pool_size=2,
    max_overflow=1
)
SessionLocal = sync_sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)
