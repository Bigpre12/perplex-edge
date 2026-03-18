import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .base import Base

# Use absolute path calculation directly to avoid cyclic/shadowing import issues
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'perplex_local.db'))}"
)

logger = logging.getLogger(__name__)

# --- ENGINE SETUP ---
async_url = DATABASE_URL
if async_url.startswith("postgres://"):
    async_url = async_url.replace("postgres://", "postgresql+asyncpg://")
elif async_url.startswith("postgresql://") and not async_url.startswith("postgresql+asyncpg://"):
    async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")
elif async_url.startswith("sqlite://"):
    async_url = async_url.replace("sqlite://", "sqlite+aiosqlite://")

connect_args = {"check_same_thread": False} if async_url.startswith("sqlite") else {}

engine = create_async_engine(async_url, connect_args=connect_args)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# --- DEPENDENCIES ---
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

def get_db_connection():
    """Legacy cursor-based connection shim for backward compatibility."""
    import sqlite3
    from urllib.parse import urlparse
    parsed = urlparse(sync_url)
    if parsed.scheme.startswith("postgresql"):
        try:
            import psycopg2
            from psycopg2.extras import RealDictConnection
            return psycopg2.connect(
                dbname=parsed.path[1:], user=parsed.username,
                password=parsed.password, host=parsed.hostname, port=parsed.port,
                connection_factory=RealDictConnection
            )
        except Exception:
            pass
    db_path = parsed.path.lstrip("/")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
