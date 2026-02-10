"""
Database module for the sports betting system
"""
import os
from typing import AsyncGenerator, Optional

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_db() -> AsyncGenerator[None, None]:
    """Get database connection - mock implementation for Railway deployment"""
    # Mock database dependency for now
    # This allows FastAPI to start without actual database
    yield None

async def get_db_connection() -> Optional[asyncpg.Connection]:
    """Get database connection"""
    if not DATABASE_URL:
        return None
    
    try:
        return await asyncpg.connect(DATABASE_URL)
    except Exception as e:
        print(f"Database connection error: {e}")
        return None
