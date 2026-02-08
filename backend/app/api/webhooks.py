"""Webhook handlers for external services (Whop, Clerk)."""

import hashlib
import hmac
import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User, UserPlan

router = APIRouter()

# =============================================================================
# Whop Webhook Schemas
# =============================================================================

class WhopMembershipEvent(BaseModel):
    """Whop membership event payload."""
    action: str  # "payment.completed", "membership.cancelled", etc.
    data: dict

class WhopPaymentData(BaseModel):
    """Whop payment data."""
    membership_id: str
    user_id: Optional[str] = None  # Custom field we pass at checkout
    email: Optional[str] = None
    status: str

# =============================================================================
# Webhook Verification
# =============================================================================

WHOP_WEBHOOK_SECRET = os.getenv("WHOP_WEBHOOK_SECRET", "")

def verify_whop_signature(payload: bytes, signature: str) -> bool:
    """
    Verify Whop webhook signature.
    
    Whop uses HMAC-SHA256 for webhook signatures.
    """
    if not WHOP_WEBHOOK_SECRET:
        # In development, skip verification if no secret set
        return True
    
    expected = hmac.new(
        WHOP_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)

# =============================================================================
# Whop Webhooks
# =============================================================================

@router.post("/webhooks/whop", tags=["webhooks"])
async def handle_whop_webhook(
    request: Request,
    x_whop_signature: str = Header(None, alias="X-Whop-Signature"),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Whop webhook events.
    
    Events handled:
    - payment.completed: User purchased or renewed subscription
    - membership.cancelled: User cancelled subscription
    - membership.expired: Subscription expired
    """
    # Get raw body for signature verification
    body = await request.body()
    
    # Verify signature in production
    if WHOP_WEBHOOK_SECRET and x_whop_signature:
        if not verify_whop_signature(body, x_whop_signature):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    # Parse event
    try:
        event = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    action = event.get("action", "")
    data = event.get("data", {})
    
    # Handle different event types
    if action == "payment.completed":
        return await handle_payment_completed(data, db)
    elif action in ["membership.cancelled", "membership.expired"]:
        return await handle_membership_ended(data, db)
    else:
        # Unknown event type - log and return success
        print(f"[Whop Webhook] Unhandled event: {action}")
        return {"status": "ignored", "action": action}

async def handle_payment_completed(data: dict, db: AsyncSession):
    """
    Handle successful payment.
    
    Upgrades user to Pro plan.
    """
    membership_id = data.get("membership_id") or data.get("id")
    user_id = data.get("user_id")  # Custom field from checkout URL
    email = data.get("email")
    
    if not membership_id:
        return {"status": "error", "message": "No membership_id in payload"}
    
    # Find user by Clerk user ID (preferred) or email
    user = None
    
    if user_id:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
    
    if not user and email:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
    
    if not user:
        # User doesn't exist yet - they might not have signed up
        # Log for manual follow-up
        print(f"[Whop Webhook] Payment for unknown user: {user_id or email}")
        return {
            "status": "pending",
            "message": "User not found - will be updated on next login",
            "membership_id": membership_id,
        }
    
    # Update user to Pro
    user.plan = UserPlan.PRO.value
    user.whop_membership_id = membership_id
    user.trial_ends_at = None  # Clear trial since they're now Pro
    
    await db.commit()
    
    print(f"[Whop Webhook] Upgraded user {user.email} to Pro")
    
    return {
        "status": "success",
        "user_id": user.id,
        "plan": user.plan,
    }

async def handle_membership_ended(data: dict, db: AsyncSession):
    """
    Handle membership cancellation or expiration.
    
    Downgrades user to Free plan.
    """
    membership_id = data.get("membership_id") or data.get("id")
    
    if not membership_id:
        return {"status": "error", "message": "No membership_id in payload"}
    
    # Find user by membership ID
    result = await db.execute(
        select(User).where(User.whop_membership_id == membership_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        print(f"[Whop Webhook] Cancellation for unknown membership: {membership_id}")
        return {"status": "ignored", "message": "User not found"}
    
    # Downgrade to free
    user.plan = UserPlan.FREE.value
    user.whop_membership_id = None
    
    await db.commit()
    
    print(f"[Whop Webhook] Downgraded user {user.email} to Free")
    
    return {
        "status": "success",
        "user_id": user.id,
        "plan": user.plan,
    }

# =============================================================================
# Clerk Webhooks (optional - for user deletion, etc.)
# =============================================================================

CLERK_WEBHOOK_SECRET = os.getenv("CLERK_WEBHOOK_SECRET", "")

@router.post("/webhooks/clerk", tags=["webhooks"])
async def handle_clerk_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Clerk webhook events.
    
    Events handled:
    - user.deleted: Remove user from database
    """
    body = await request.body()
    
    # In production, verify Clerk webhook signature using svix
    # See: https://clerk.com/docs/integrations/webhooks/sync-data
    
    try:
        event = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    event_type = event.get("type", "")
    data = event.get("data", {})
    
    if event_type == "user.deleted":
        user_id = data.get("id")
        if user_id:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                await db.delete(user)
                await db.commit()
                print(f"[Clerk Webhook] Deleted user {user_id}")
                return {"status": "success", "user_id": user_id}
    
    return {"status": "ignored", "event_type": event_type}

# =============================================================================
# Test Endpoint (for development)
# =============================================================================

@router.post("/webhooks/test-upgrade/{user_id}", tags=["webhooks"])
async def test_upgrade_user(
    user_id: str,
    plan: str = "pro",
    db: AsyncSession = Depends(get_db),
):
    """
    Test endpoint to manually upgrade/downgrade a user.
    
    Only available in development mode.
    """
    if os.getenv("ENVIRONMENT", "development") == "production":
        raise HTTPException(status_code=403, detail="Not available in production")
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.plan = plan
    if plan != UserPlan.TRIAL.value:
        user.trial_ends_at = None
    
    await db.commit()
    
    return {
        "status": "success",
        "user_id": user.id,
        "plan": user.plan,
    }
