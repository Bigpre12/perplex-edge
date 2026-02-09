"""
Database module for the sports betting system
"""
import asyncpg
import os
from typing import AsyncGenerator

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """Get database connection"""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not found")
    
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

async def get_db_connection() -> asyncpg.Connection:
    """Get database connection"""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not found")
    
    return await asyncpg.connect(DATABASE_URL)
