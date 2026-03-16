print(f"DEBUG: db.session is initializing...")
import os
import logging
import contextlib
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Use absolute path calculation directly to avoid cyclic/shadowing import issues
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'perplex_local.db'))}"
)

logger = logging.getLogger(__name__)

# --- ENGINE SETUP ---
# Ensure we use psycopg2 for stability on Windows if using Postgres
sync_url = DATABASE_URL.replace("postgres://", "postgresql://").replace("postgresql+asyncpg://", "postgresql://")
if sync_url.startswith("postgresql://") and not sync_url.startswith("postgresql+psycopg2://"):
    sync_url = sync_url.replace("postgresql://", "postgresql+psycopg2://")

connect_args = {"check_same_thread": False} if sync_url.startswith("sqlite") else {
    "keepalives": 1,
    "keepalives_idle": 30,
    "keepalives_interval": 10,
    "keepalives_count": 5
}

engine = create_engine(sync_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

# --- ASYNC SHIM (for Windows/Legacy support) ---
class DummyAsyncResult:
    def __init__(self, sync_result):
        self._sync_result = sync_result
    def scalars(self): return self._sync_result.scalars()
    def scalar(self): return self._sync_result.scalar()
    def all(self): return self._sync_result.all()
    def __iter__(self): return iter(self._sync_result)

class DummyAsyncSession:
    def __init__(self, sync_session):
        self.sync_session = sync_session
    async def execute(self, stmt, *args, **kwargs):
        return DummyAsyncResult(self.sync_session.execute(stmt, *args, **kwargs))
    async def commit(self): self.sync_session.commit()
    async def rollback(self): self.sync_session.rollback()
    def add(self, obj): self.sync_session.add(obj)
    async def flush(self): self.sync_session.flush()
    async def close(self): self.sync_session.close()

@contextlib.asynccontextmanager
async def async_session_maker():
    session = SessionLocal()
    try:
        yield DummyAsyncSession(session)
    finally:
        session.close()

# --- DEPENDENCIES ---
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    async with async_session_maker() as session:
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
