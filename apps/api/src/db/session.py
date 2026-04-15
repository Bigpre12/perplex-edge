import os
import re
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

# Fix for asyncpg: strip 'sslmode' from URL as it's not supported as a query param by asyncpg
if "sslmode=" in DATABASE_URL:
    DATABASE_URL = re.sub(r"[?&]sslmode=[^&]*", "", DATABASE_URL)
    if "&" in DATABASE_URL and "?" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("&", "?", 1)

# Auto-switch Supabase pooler URLs from Session Mode (5432) to Transaction Mode (6543)
_is_pg = "postgresql" in DATABASE_URL
if _is_pg and "pooler" in DATABASE_URL and ":5432" in DATABASE_URL:
    logger.info("Switching Supabase pooler from Session Mode (5432) to Transaction Mode (6543)")
    DATABASE_URL = DATABASE_URL.replace(":5432", ":6543", 1)

# Redacted logging for debugging
_raw_db_url = os.environ.get("DATABASE_URL", "NOT SET")
if _raw_db_url != "NOT SET":
    try:
        from urllib.parse import urlparse
        parsed = urlparse(_raw_db_url.replace("postgresql+asyncpg://", "http://").replace("postgresql://", "http://"))
        logger.info(f"Database Initialization: Attempting connection to host={parsed.hostname} user={parsed.username} port={parsed.port}")
    except Exception:
        logger.info("Database Initialization: Connecting to redacted URL (Parsing failed)")
else:
    logger.warning("Database Initialization: DATABASE_URL is NOT SET in current environment!")

# --- ASYNC ENGINE SETUP ---
if _is_pg:
    connect_args = {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    }
else:
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=5,
    pool_timeout=60,
    pool_recycle=300,
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
async_session_maker = AsyncSessionLocal

# Legacy shim for SessionLocal if needed by external scripts (minimizing usage)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as sync_sessionmaker

sync_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://").replace("sqlite+aiosqlite://", "sqlite://")
_sync_connect_args = {"check_same_thread": False} if "sqlite" in sync_url else {}
sync_engine = create_engine(
    sync_url,
    connect_args=_sync_connect_args,
    pool_size=3,
    max_overflow=2,
)
SessionLocal = sync_sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)
