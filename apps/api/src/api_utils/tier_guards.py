from fastapi import HTTPException, status, Depends
from models.user import User
from routers.auth import get_current_user

# Rank-based access control
TIER_RANK = {
    "free": 0,
    "pro": 1,
    "elite": 2,
    "admin": 3
}

def require_tier(min_tier: str):
    """
    FastAPI dependency that ensures the current user has at least the required tier.
    Admin users bypass all checks.
    """
    async def tier_dependency(current_user: User = Depends(get_current_user)):
        # Admin bypass (role-based)
        if current_user.is_admin or current_user.role == "admin":
            return current_user
            
        user_tier = (current_user.subscription_tier or "free").lower()
        
        # Check rank vs requirement
        if TIER_RANK.get(user_tier, 0) < TIER_RANK.get(min_tier.lower(), 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires a {min_tier.capitalize()} subscription."
            )
        return current_user
        
    return tier_dependency
