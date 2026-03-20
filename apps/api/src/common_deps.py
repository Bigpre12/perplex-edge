from sqlalchemy.ext.asyncio import AsyncSession
import logging
logger = logging.getLogger(__name__)
from fastapi import Header, HTTPException, Depends
from services.auth_service import auth_service
from db.session import get_async_db, get_db
from models.user import UserOverride
from sqlalchemy.future import select
from datetime import datetime, timezone
import os
from core.config import settings

OWNER_EMAILS = os.getenv("OWNER_EMAILS", "").split(",")

async def get_user_tier(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
) -> str:
    if settings.DEVELOPMENT_MODE:
        return "elite"
        
    if not authorization:
        return "free"
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = auth_service.decode_access_token(token)
        if not payload:
            return "free"
            
        email = payload.get("email", "")
        if email and email.lower() in [e.lower() for e in OWNER_EMAILS if e]:
            return "elite"
            
        now = datetime.now(timezone.utc)
        stmt = select(UserOverride).where(UserOverride.email == email).where(
            (UserOverride.expires_at == None) | (UserOverride.expires_at > now)
        )
        result = await db.execute(stmt)
        override = result.scalar_one_or_none()
        if override:
            return override.tier.lower()
            
        return payload.get("tier", "free").lower()
    except Exception:
        return "free"

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import uuid

security = HTTPBearer(auto_error=False)

async def get_current_user_supabase(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not credentials:
        return None
    
    from api_utils.supabase_proxy import supabase
    token = credentials.credentials
    try:
        sb_response = supabase.auth.get_user(token)
        if hasattr(sb_response, 'user') and sb_response.user:
            return sb_response.user
        if isinstance(sb_response, dict) and 'user' in sb_response:
            return sb_response['user']
    except Exception as e:
        logger.warning(f"Supabase auth error in common_deps: {e}")
    return None

def require_elite(tier: str = Depends(get_user_tier)):
    if tier != "elite":
        raise HTTPException(status_code=403, detail="Elite subscription required")

def require_pro(tier: str = Depends(get_user_tier)):
    if tier not in ("pro", "elite"):
        raise HTTPException(status_code=403, detail="Pro or Elite subscription required")
