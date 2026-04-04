from functools import wraps
from fastapi import HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from typing import Optional, List, Dict


class TierCheckMiddleware(BaseHTTPMiddleware):
    """
    Middleware stub for tier-based request gating.
    Currently a pass-through — tier enforcement is handled per-route
    via the require_tier() decorator below.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        return response

# Tier Levels Mapping
TIER_LEVELS = {
    "free": 0,
    "pro": 1,
    "elite": 2,
    "owner": 3 # Admin/Owner tier
}

def require_tier(minimum: str):
    """
    Decorator to enforce a minimum tier requirement on a FastAPI route.
    Assumes user info is already injected via get_current_user_supabase.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to get user from kwargs, injected by Depends(get_current_user_supabase)
            user = kwargs.get("user")
            
            if not user:
                # If no user and endpoint requires a tier, it's a 401/403
                # (Some endpoints might handle optional auth, but require_tier makes it restricted)
                raise HTTPException(
                    status_code=403,
                    detail={
                        "code": "AUTH_REQUIRED",
                        "message": "Authentiction required for this feature"
                    }
                )
            
            # Fetch tier from Supabase user metadata or attributes
            # user_metadata is where we'll likely store the 'tier' string
            user_meta = getattr(user, "user_metadata", {})
            user_tier = user_meta.get("tier", "free").lower()
            
            # Allow owners to bypass tier checks
            is_owner = user_tier == "owner" or user.email in ["brydsonpreion31@gmail.com"]
            
            if not is_owner and TIER_LEVELS.get(user_tier, 0) < TIER_LEVELS.get(minimum.lower(), 0):
                raise HTTPException(
                    status_code=403,
                    detail={
                        "code": "TIER_REQUIRED",
                        "required": minimum,
                        "current": user_tier,
                        "upgrade_url": "/pricing",
                        "message": f"This feature requires {minimum} tier access."
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def get_tier_limits(tier: str) -> Dict:
    """Helper to get limits for a tier"""
    tier = tier.lower()
    if tier == "elite" or tier == "owner":
        return {"oracle_daily": 1000, "sim_count": 10000, "refresh_sec": 30}
    if tier == "pro":
        return {"oracle_daily": 10, "sim_count": 100, "refresh_sec": 60}
    return {"oracle_daily": 0, "sim_count": 0, "refresh_sec": 300}
