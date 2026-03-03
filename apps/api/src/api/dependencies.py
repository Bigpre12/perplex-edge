from fastapi import Header, HTTPException, Depends
from services.auth_service import auth_service
from database import get_async_db
from models.users import UserOverride
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
import os

OWNER_EMAILS = os.getenv("OWNER_EMAILS", "").split(",")

async def get_user_tier(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_async_db)
) -> str:
    """
    Returns 'free', 'basic', 'pro', or 'elite' based on bypasses, overrides, or JWT tier claim.
    If no token or invalid token, defaults to 'free'.
    """
    if not authorization:
        return "free"
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = auth_service.decode_access_token(token)
        if not payload:
            return "free"
            
        email = payload.get("email", "")
        
        # 1. Owner bypass — always elite, no Stripe needed
        if email and email in OWNER_EMAILS:
            return "elite"
            
        # 2. Check override table
        now = datetime.now(timezone.utc)
        stmt = select(UserOverride).where(
            UserOverride.email == email
        ).where(
            (UserOverride.expires_at == None) | (UserOverride.expires_at > now)
        )
        result = await db.execute(stmt)
        override = result.scalar_one_or_none()
        if override:
            return override.tier
            
        # 3. Fall back to JWT tier (Stripe subscription)
        return payload.get("tier", "free")
    except Exception:
        return "free"

def require_pro(tier: str = Depends(get_user_tier)):
    """Dependency to ensure user is at least Pro tier."""
    if tier not in ("pro", "elite"):
        raise HTTPException(status_code=403, detail="Pro or Elite subscription required")

def require_basic(tier: str = Depends(get_user_tier)):
    """Dependency to ensure user is at least Basic tier."""
    if tier not in ("basic", "pro", "elite"):
        raise HTTPException(status_code=403, detail="Paid subscription required")
