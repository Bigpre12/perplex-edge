"""
Database module for the sports betting system
"""
import asyncpg
import os
from typing import AsyncGenerator, Optional

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """Get database connection"""
    if not DATABASE_URL:
        # Return None if no database URL - allows app to start without DB
        return None
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            yield conn
        finally:
            await conn.close()
    except Exception as e:
        # Log error but don't crash app
        print(f"Database connection error: {e}")
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
