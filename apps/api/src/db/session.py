import os
import re
import logging
logger = logging.getLogger(__name__)
from typing import AsyncGenerator
from urllib.parse import urlparse
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.pool import NullPool
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

# Optional switch Supabase pooler URLs from Session Mode (5432) to Transaction Mode (6543).
# Default OFF: transaction mode can still surface prepared-statement issues in some workloads.
_is_pg = "postgresql" in DATABASE_URL
_is_pooler_url = _is_pg and "pooler" in DATABASE_URL
_force_tx_pooler = os.getenv("SUPABASE_POOLER_FORCE_TRANSACTION_MODE", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
if _is_pooler_url and ":5432" in DATABASE_URL and _force_tx_pooler:
    logger.info("Switching Supabase pooler from Session Mode (5432) to Transaction Mode (6543)")
    DATABASE_URL = DATABASE_URL.replace(":5432", ":6543", 1)

def _ensure_pg_query_params(url: str, params: dict[str, str]) -> str:
    parts = urlsplit(url)
    q = dict(parse_qsl(parts.query, keep_blank_values=True))
    q.update({k: v for k, v in params.items() if v is not None})
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q), parts.fragment))

if _is_pg:
    DATABASE_URL = _ensure_pg_query_params(
        DATABASE_URL,
        {
            "statement_cache_size": "0",
            "prepared_statement_cache_size": "0",
        },
    )

# Redacted logging for debugging
_raw_db_url = os.environ.get("DATABASE_URL", "NOT SET")
if _raw_db_url != "NOT SET":
    try:
        parsed = urlparse(DATABASE_URL)
        safe_url = DATABASE_URL.replace(parsed.password or "", "****")
        logger.info("Database Initialization: Connecting to DB: %s", safe_url)
    except Exception:
        logger.info("Database Initialization: Connecting to redacted URL (Parsing failed)")
else:
    logger.warning("Database Initialization: DATABASE_URL is NOT SET in current environment!")

# --- ASYNC ENGINE SETUP ---
if _is_pg:
    connect_args = {
        "ssl": "require",
        "server_settings": {"application_name": "perplex_edge_backend"},
        # PgBouncer transaction/statement mode cannot safely support prepared statements.
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    }
else:
    connect_args = {"check_same_thread": False}

engine_kwargs = {
    "echo": False,
    "connect_args": connect_args,
    "pool_pre_ping": True,
}
#
# IMPORTANT (Supabase pooler / PgBouncer):
# Session-mode poolers enforce a hard max connection count. If we allow large
# overflow (or unbounded connection creation), burst traffic trips:
#   asyncpg.exceptions.InternalServerError: (EMAXCONNSESSION) max clients reached
# Keep a small, explicit pool and do not allow large overflow.
#
_pool_size = max(1, int(os.getenv("DB_POOL_SIZE", "3")))
_max_overflow = max(0, int(os.getenv("DB_MAX_OVERFLOW", "0")))
_pool_timeout = max(1, int(os.getenv("DB_POOL_TIMEOUT_SECONDS", "30")))
_pool_recycle = max(60, int(os.getenv("DB_POOL_RECYCLE_SECONDS", "300")))

if _is_pg:
    engine_kwargs["pool_size"] = _pool_size
    engine_kwargs["max_overflow"] = _max_overflow
    engine_kwargs["pool_timeout"] = _pool_timeout
    engine_kwargs["pool_recycle"] = _pool_recycle
elif _is_pooler_url or ":6543" in DATABASE_URL:
    # Defensive: if a non-pg URL somehow matches pooler heuristics, avoid pooling.
    engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Standard exports for various utilities
__all__ = [
    "engine",
    "AsyncSessionLocal",
    "get_db",
    "get_async_db",
    "validate_db_connection",
    "Base",
    "SessionLocal",
]

from contextlib import asynccontextmanager

# --- DEPENDENCIES ---
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            # Ensure failed requests never leave an invalid transaction attached
            # to the pooled connection (prevents PendingRollbackError cascades).
            await session.rollback()
            raise

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Alias for get_db for backward compatibility."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def validate_db_connection() -> None:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection verified successfully.")
    except Exception as e:
        err = str(e)
        if "authentication" in err.lower() or "password" in err.lower():
            logger.critical(
                "DATABASE AUTH FAILED: Check DATABASE_URL username/password/SSL. "
                "The app cannot start safely."
            )
        else:
            logger.critical("Database connection failed at startup: %s", err)
        raise

# Legacy alias: many routers/services still import async_session_maker
async_session_maker = AsyncSessionLocal

# Legacy shim for SessionLocal if needed by external scripts (minimizing usage)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as sync_sessionmaker

sync_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://").replace("sqlite+aiosqlite://", "sqlite://")
_sync_connect_args = {"check_same_thread": False} if "sqlite" in sync_url else {}
_sync_engine_kwargs = {"connect_args": _sync_connect_args}
if _is_pg:
    _sync_engine_kwargs["pool_size"] = max(1, int(os.getenv("DB_SYNC_POOL_SIZE", "2")))
    _sync_engine_kwargs["max_overflow"] = max(0, int(os.getenv("DB_SYNC_MAX_OVERFLOW", "0")))

sync_engine = create_engine(sync_url, **_sync_engine_kwargs)
SessionLocal = sync_sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)
