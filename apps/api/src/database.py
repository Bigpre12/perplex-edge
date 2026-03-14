import os
import logging
import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL

# --- SYNC ENGINE SETUP ---
# Ensure we ALWAYS use psycopg2 to connect synchronously to avoid Windows python 3.14 async hangs
sync_url = DATABASE_URL.replace("postgres://", "postgresql://").replace("postgresql+asyncpg://", "postgresql://")
if sync_url.startswith("postgresql://") and not sync_url.startswith("postgresql+psycopg2://"):
    sync_url = sync_url.replace("postgresql://", "postgresql+psycopg2://")

if sync_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # Adding pooling settings for the supabase transaction pooler
    connect_args = {
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    }

engine = create_engine(sync_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DummyAsyncResult:
    def __init__(self, sync_result):
        self._sync_result = sync_result
    def scalars(self):
        return self._sync_result.scalars()
    def scalar(self):
        return self._sync_result.scalar()
    def scalar_one_or_none(self):
        return self._sync_result.scalar_one_or_none()
    def fetchall(self):
        return self._sync_result.fetchall()
    def fetchone(self):
        return self._sync_result.fetchone()
    def first(self):
        return self._sync_result.first()
    def all(self):
        return self._sync_result.all()
    def mappings(self):
        return self._sync_result.mappings()
    def __iter__(self):
        return iter(self._sync_result)
    def __aiter__(self):
        async def _async_iter():
            for row in self._sync_result:
                yield row
        return _async_iter()

class DummyAsyncSession:
    def __init__(self, sync_session):
        self.sync_session = sync_session

    async def execute(self, stmt, *args, **kwargs):
        res = self.sync_session.execute(stmt, *args, **kwargs)
        return DummyAsyncResult(res)

    async def flush(self):
        self.sync_session.flush()

    @contextlib.asynccontextmanager
    async def begin(self):
        with self.sync_session.begin():
            yield

    async def commit(self):
        self.sync_session.commit()

    async def rollback(self):
        self.sync_session.rollback()

    def add(self, obj):
        self.sync_session.add(obj)

    async def refresh(self, obj, *args, **kwargs):
        self.sync_session.refresh(obj, *args, **kwargs)

    async def delete(self, obj):
        self.sync_session.delete(obj)

    def add_all(self, objs):
        self.sync_session.add_all(objs)

    async def scalar(self, stmt, *args, **kwargs):
        return self.sync_session.scalar(stmt, *args, **kwargs)

    async def scalars(self, stmt, *args, **kwargs):
        return self.sync_session.scalars(stmt, *args, **kwargs)

import contextlib

@contextlib.asynccontextmanager
async def async_session_maker():
    session = SessionLocal()
    try:
        yield DummyAsyncSession(session)
    finally:
        session.close()

Base = declarative_base()

# --- DEPENDENCIES ---
def get_db():
    """Sync DB dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    """Async DB dependency"""
    async with async_session_maker() as session:
        yield session

# LEGACY / INSTITUTIONAL SUPPORT - Removed in favor of Alembic
def get_db_connection():
    """ Raw cursor-based connection (maintained for backward compatibility) """
    import sqlite3
    import psycopg2
    from urllib.parse import urlparse
    
    parsed = urlparse(sync_url)
    if parsed.scheme == 'postgresql':
        from psycopg2.extras import RealDictConnection
        conn = psycopg2.connect(
            dbname=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port,
            connection_factory=RealDictConnection
        )
        return conn
    else:
        db_path = parsed.path.lstrip('/')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
