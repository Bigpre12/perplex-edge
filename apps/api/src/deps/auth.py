import asyncpg
import logging
from typing import Dict, Any
from core.config import settings
from core.asyncpg_dsn import asyncpg_dsn_from_database_url

logger = logging.getLogger(__name__)


async def get_db_conn():
    """Helper to get a direct asyncpg connection"""
    url = asyncpg_dsn_from_database_url(settings.DATABASE_URL)

    # asyncpg doesn't support sqlite; yield nothing (async generator cannot return a value).
    if "sqlite" in url:
        return

    conn = await asyncpg.connect(url)
    try:
        yield conn
    finally:
        await conn.close()

async def provision_user_jit(user_payload: Dict[str, Any], db):
    """
    JIT Provisioning using the user's Supabase UUID.
    Matches the business logic requested by the user.
    """
    auth_id = user_payload.get("sub")
    email = user_payload.get("email")
    
    if not auth_id:
        logger.warning("No 'sub' found in user payload for JIT provisioning")
        return None

    # deps/auth.py — change the lookup column
    row = await db.fetchrow(
        "SELECT * FROM users WHERE auth_id = $1", 
        auth_id  # Supabase JWT 'sub' is the UUID
    )
    
    if not row:
        logger.info(f"Provisioning new user: {email} ({auth_id})")
        await db.execute("""
            INSERT INTO users (auth_id, email, subscription_tier, is_active)
            VALUES ($1, $2, 'free', true)
            ON CONFLICT (auth_id) DO NOTHING
        """, auth_id, email)
        
        # Fetch the newly created row
        row = await db.fetchrow(
            "SELECT * FROM users WHERE auth_id = $1", 
            auth_id
        )
        
    return row
