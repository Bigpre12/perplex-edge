"""User API endpoints for authentication and profile management."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User, UserPlan


router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

class UserSyncRequest(BaseModel):
    """Request to sync user from Clerk."""
    clerk_id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponse(BaseModel):
    """User response with plan info."""
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    plan: str
    trial_ends_at: Optional[datetime] = None
    created_at: datetime
    props_viewed_today: int = 0
    
    class Config:
        from_attributes = True


class UserPlanUpdate(BaseModel):
    """Request to update user plan."""
    plan: str
    whop_membership_id: Optional[str] = None


class WhopCheckoutResponse(BaseModel):
    """Response with Whop checkout URLs."""
    free_checkout_url: str
    pro_monthly_checkout_url: Optional[str] = None
    pro_yearly_checkout_url: Optional[str] = None


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/users/sync", response_model=UserResponse, tags=["users"])
async def sync_user(
    request: UserSyncRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Sync user from Clerk authentication.
    
    Creates user if not exists, updates if exists.
    New users automatically get a 7-day free trial.
    """
    # Check if user exists
    result = await db.execute(
        select(User).where(User.id == request.clerk_id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        # Update existing user
        user.email = request.email
        if request.first_name:
            user.first_name = request.first_name
        if request.last_name:
            user.last_name = request.last_name
    else:
        # Create new user with 7-day trial
        trial_ends = datetime.now(timezone.utc) + timedelta(days=7)
        user = User(
            id=request.clerk_id,
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            plan=UserPlan.TRIAL.value,
            trial_ends_at=trial_ends,
        )
        db.add(user)
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        plan=user.plan,
        trial_ends_at=user.trial_ends_at,
        created_at=user.created_at,
        props_viewed_today=user.props_viewed_today,
    )


@router.get("/users/me", response_model=UserResponse, tags=["users"])
async def get_current_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user info.
    
    Requires valid Clerk JWT in Authorization header.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Extract user ID from JWT (simplified - full verification in auth.py)
    # For now, we trust the frontend to send valid tokens
    # In production, verify JWT signature with Clerk's public key
    try:
        # Token format: "Bearer <token>"
        token = authorization.replace("Bearer ", "")
        
        # Decode JWT payload (without verification for now)
        # In production, use clerk-backend-api or verify signature
        import base64
        import json
        
        # JWT has 3 parts: header.payload.signature
        parts = token.split(".")
        if len(parts) != 3:
            raise HTTPException(status_code=401, detail="Invalid token format")
        
        # Decode payload (add padding if needed)
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding
        
        decoded = json.loads(base64.urlsafe_b64decode(payload))
        user_id = decoded.get("sub")  # Clerk stores user ID in 'sub' claim
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no user ID")
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if trial has expired
    if user.plan == UserPlan.TRIAL.value and user.trial_ends_at:
        if datetime.now(timezone.utc) > user.trial_ends_at:
            # Trial expired, downgrade to free
            user.plan = UserPlan.FREE.value
            await db.commit()
            await db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        plan=user.plan,
        trial_ends_at=user.trial_ends_at,
        created_at=user.created_at,
        props_viewed_today=user.props_viewed_today,
    )


@router.post("/users/{user_id}/increment-props", tags=["users"])
async def increment_props_viewed(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Increment the props viewed count for a user.
    
    Resets daily at midnight UTC.
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if we need to reset the counter (new day)
    today = datetime.now(timezone.utc).date()
    if user.props_reset_date is None or user.props_reset_date.date() < today:
        user.props_viewed_today = 1
        user.props_reset_date = datetime.now(timezone.utc)
    else:
        user.props_viewed_today += 1
    
    await db.commit()
    
    return {
        "props_viewed_today": user.props_viewed_today,
        "reset_date": user.props_reset_date,
    }


@router.get("/users/whop-checkout", response_model=WhopCheckoutResponse, tags=["users"])
async def get_whop_checkout_urls():
    """
    Get Whop checkout URLs for subscription plans.
    
    Returns checkout URLs for free, pro monthly, and pro yearly plans.
    """
    from app.core.config import get_settings
    settings = get_settings()
    
    return WhopCheckoutResponse(
        free_checkout_url=settings.whop_free_checkout_url,
        pro_monthly_checkout_url=settings.whop_pro_monthly_checkout_url or None,
        pro_yearly_checkout_url=settings.whop_pro_yearly_checkout_url or None
    )
