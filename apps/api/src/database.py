from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os
from dotenv import load_dotenv, find_dotenv

# Load env variables before any other processing
load_dotenv(find_dotenv())

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # Sensible default relative to current working directory
    DATABASE_URL = "sqlite:///./data/perplex_local.db"

# Sync version
sync_url = DATABASE_URL
engine = create_engine(sync_url, connect_args={"check_same_thread": False} if "sqlite" in sync_url else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async version
async_url = DATABASE_URL
if "sqlite://" in async_url and "sqlite+aiosqlite://" not in async_url:
    async_url = async_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
elif "postgresql://" in async_url and "postgresql+asyncpg://" not in async_url:
    async_url = async_url.replace("postgresql://", "postgresql+asyncpg://", 1)

async_engine = create_async_engine(async_url, connect_args={"check_same_thread": False} if "sqlite" in async_url else {})
async_session_maker = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    async with async_session_maker() as session:
        yield session
