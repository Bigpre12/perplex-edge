"""Authentication middleware for Clerk JWT verification."""

import base64
import json
import os
from datetime import datetime, timezone
from typing import Optional, Annotated

from fastapi import Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User, UserPlan


# =============================================================================
# JWT Token Handling
# =============================================================================

def decode_jwt_payload(token: str) -> dict:
    """
    Decode JWT payload without signature verification.
    
    Note: In production, you should verify the JWT signature using
    Clerk's public key. This simplified version trusts the token
    for development purposes.
    
    For production, use:
    - clerk-backend-api package
    - Or manually verify with jwcrypto using Clerk's JWKS endpoint
    """
    try:
        # Remove "Bearer " prefix if present
        if token.startswith("Bearer "):
            token = token[7:]
        
        # JWT has 3 parts: header.payload.signature
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")
        
        # Decode payload (add padding if needed)
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding
        
        return json.loads(base64.urlsafe_b64decode(payload))
    
    except Exception as e:
        raise ValueError(f"Failed to decode JWT: {str(e)}")


def get_user_id_from_token(token: str) -> str:
    """Extract user ID (sub claim) from Clerk JWT."""
    payload = decode_jwt_payload(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise ValueError("No user ID in token")
    
    return user_id


# =============================================================================
# Dependency Functions
# =============================================================================

async def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    
    Use this for endpoints that work for both authenticated and anonymous users,
    but may return different data based on authentication.
    """
    if not authorization:
        return None
    
    try:
        user_id = get_user_id_from_token(authorization)
        
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        # Check if trial has expired
        if user and user.plan == UserPlan.TRIAL.value and user.trial_ends_at:
            if datetime.now(timezone.utc) > user.trial_ends_at:
                user.plan = UserPlan.FREE.value
                await db.commit()
        
        return user
    
    except Exception:
        # Invalid token - treat as anonymous
        return None


async def get_current_user(
    authorization: str = Header(..., description="Bearer token from Clerk"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user.
    
    Raises 401 if not authenticated or user not found.
    Use this for endpoints that require authentication.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required",
        )
    
    try:
        user_id = get_user_id_from_token(authorization)
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}",
        )
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found. Please sign in again.",
        )
    
    # Check if trial has expired
    if user.plan == UserPlan.TRIAL.value and user.trial_ends_at:
        if datetime.now(timezone.utc) > user.trial_ends_at:
            user.plan = UserPlan.FREE.value
            await db.commit()
    
    return user


async def get_pro_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and verify they have Pro access.
    
    Raises 403 if user doesn't have Pro access.
    Use this for Pro-only endpoints.
    """
    if not user.is_pro:
        raise HTTPException(
            status_code=403,
            detail="Pro subscription required for this feature",
        )
    return user


# =============================================================================
# Type Aliases for Dependency Injection
# =============================================================================

# Optional user (for endpoints that work with or without auth)
OptionalUser = Annotated[Optional[User], Depends(get_optional_user)]

# Required user (for authenticated endpoints)
CurrentUser = Annotated[User, Depends(get_current_user)]

# Pro user (for Pro-only endpoints)
ProUser = Annotated[User, Depends(get_pro_user)]


# =============================================================================
# Helper Functions
# =============================================================================

def check_user_plan(user: Optional[User], required_plan: str = "free") -> bool:
    """
    Check if user meets the required plan level.
    
    Plan hierarchy: free < trial < pro
    """
    if user is None:
        return required_plan == "free"
    
    plan_levels = {
        UserPlan.FREE.value: 0,
        UserPlan.TRIAL.value: 1,
        UserPlan.PRO.value: 2,
    }
    
    user_level = plan_levels.get(user.plan, 0)
    required_level = plan_levels.get(required_plan, 0)
    
    # Trial with active expiry counts as pro level
    if user.is_trial:
        user_level = plan_levels[UserPlan.PRO.value]
    
    return user_level >= required_level


def get_user_sports(user: Optional[User]) -> list[int]:
    """
    Get list of sport IDs the user can access.
    
    Free users: NBA (30) + NFL (31) only
    Trial/Pro users: All sports
    """
    FREE_SPORTS = [30, 31]  # NBA, NFL
    ALL_SPORTS = [30, 31, 32, 40, 41, 42, 43, 53]  # All supported sports
    
    if user is None:
        return FREE_SPORTS
    
    if user.is_pro or user.is_trial:
        return ALL_SPORTS
    
    return FREE_SPORTS
