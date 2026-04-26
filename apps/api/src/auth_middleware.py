# apps/api/src/auth_middleware.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging, os

logger = logging.getLogger(__name__)

# Load owner emails and bypass setting from environment
OWNER_EMAILS = [e.strip().lower() for e in os.getenv("OWNER_EMAILS", "").split(",") if e.strip()]
security = HTTPBearer(auto_error=False)

# Mock user for bypass mode
BYPASS_USER = {
    "uid": "owner-bypass",
    "email": OWNER_EMAILS[0] if OWNER_EMAILS else "dev@lucrix.io",
    "plan": "elite",
    "subscription_tier": "elite",
}

async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """FastAPI dependency to verify auth or bypass."""
    from core.config import settings
    bypass_auth = settings.BYPASS_AUTH
    if settings.IS_PRODUCTION and bypass_auth:
        raise HTTPException(status_code=503, detail="BYPASS_AUTH is forbidden in production")
    if bypass_auth:
        return BYPASS_USER
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization required")
    try:
        # Fallback to local JWT auth if not bypassing
        from routers.auth import get_current_user
        # Note: routers.auth.py get_current_user already expects token/credentials via Depends
        # We call the logic directly or rely on the dependency chain.
        # The user provided a specific snippet with 'get_current_user_from_token'
        # but our auth.py uses 'get_current_user'. Balancing user request vs codebase.
        from core.config import settings
        from api_utils.supabase_proxy import create_client
        
        # Original logic or user's specific bypass-friendly logic
        return await get_current_user(token=credentials.credentials)
    except Exception as e:
        logger.warning(f"Auth failed: {e}")
        raise HTTPException(status_code=401, detail=str(e))

async def require_pro(user=Depends(require_auth)):
    """FastAPI dependency to verify Pro plan or higher/bypass."""
    from core.config import settings
    if settings.BYPASS_AUTH or user.get("email", "").lower() in OWNER_EMAILS:
        return user
    if user.get("plan", "free") not in ("pro", "premium", "elite", "syndicate", "admin"):
        raise HTTPException(status_code=403, detail="Pro subscription required.")
    return user

async def require_elite(user=Depends(require_auth)):
    """FastAPI dependency to verify Elite plan or higher/bypass."""
    from core.config import settings
    if settings.BYPASS_AUTH or user.get("email", "").lower() in OWNER_EMAILS:
        return user
    if user.get("plan", "free") not in ("elite", "syndicate", "admin"):
        raise HTTPException(status_code=403, detail="Elite subscription required.")
    return user

async def require_syndicate(user=Depends(require_auth)):
    """FastAPI dependency to verify Syndicate plan or higher/bypass."""
    from core.config import settings
    if settings.BYPASS_AUTH or user.get("email", "").lower() in OWNER_EMAILS:
        return user
    if user.get("plan", "free") not in ("syndicate", "admin"):
        raise HTTPException(status_code=403, detail="Syndicate subscription required.")
    return user
