class AsyncSession: pass
from fastapi import APIRouter, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse
import stripe
import logging
from sqlalchemy import select, update

from db.session import get_async_db
from models.user import User
from services.stripe_service import stripe_service
from routers.auth import get_current_user
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Billing"])

STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET

async def upgrade_user(db: AsyncSession, user_id: int, price_id: str, customer_id: str):
    tier = stripe_service.resolve_tier(price_id)
    logger.info(f"[Billing] Upgrading user {user_id} to {tier}")
    
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(
            subscription_tier=tier,
            stripe_customer_id=customer_id
        )
    )
    await db.execute(stmt)
    await db.commit()
    return tier

async def downgrade_user(db: AsyncSession, customer_id: str):
    logger.info(f"[Billing] Downgrading customer {customer_id} to free")
    stmt = (
        update(User)
        .where(User.stripe_customer_id == customer_id)
        .values(subscription_tier="free")
    )
    await db.execute(stmt)
    await db.commit()

@router.post("/create-checkout-session")
async def create_checkout_session(
    body: dict,
    current_user: User = Depends(get_current_user)
):
    price_id = body.get("price_id")
    if not price_id:
        raise HTTPException(status_code=400, detail="price_id required")

    try:
        url = stripe_service.create_checkout_session(
            price_id=price_id,
            customer_email=current_user.email,
            user_id=str(current_user.id)
        )
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-portal-session")
async def create_portal_session(current_user: User = Depends(get_current_user)):
    if not current_user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account found")
    try:
        url = stripe_service.create_portal_session(current_user.stripe_customer_id)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def billing_status(current_user: User = Depends(get_current_user)):
    if not current_user.stripe_customer_id:
        return {"status": "inactive", "tier": "free"}
    return await stripe_service.get_subscription_status(current_user.stripe_customer_id)

@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_async_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    etype = event["type"]
    data = event["data"]["object"]

    # ── checkout.session.completed ─────────────────────────
    if etype == "checkout.session.completed":
        user_id = data.get("metadata", {}).get("user_id")
        customer_id = data.get("customer")
        
        # We need the price_id to resolve the tier
        # Sessions usually have one-off checkouts or subscriptions
        # For subscriptions, we can also look at CustomerSubscriptionCreated later
        # but session.completed is faster for the UI redirect.
        try:
            items = stripe.checkout.Session.list_line_items(data["id"])
            price_id = items.data[0]["price"]["id"] if items.data else None
            
            if user_id and price_id:
                await upgrade_user(db, int(user_id), price_id, customer_id)
        except Exception as e:
            logger.error(f"[Billing] Error processing checkout session: {e}")

    # ── subscription updated ───────────────────────────────
    elif etype == "customer.subscription.updated":
        customer_id = data.get("customer")
        try:
            price_id = data["items"]["data"][0]["price"]["id"]
            # Find user by customer_id
            stmt = select(User).where(User.stripe_customer_id == customer_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user and price_id:
                await upgrade_user(db, user.id, price_id, customer_id)
        except Exception as e:
            logger.error(f"[Billing] Subscription update error: {e}")

    # ── subscription deleted ───────────────────────────────
    elif etype == "customer.subscription.deleted":
        await downgrade_user(db, data.get("customer"))

    # ── payment failed ────────────────────────────────────
    elif etype == "invoice.payment_failed":
        # Usually we want to wait for multiple failures, but simple logic is:
        # if the final attempt fails, downgrade
        if data.get("next_payment_attempt") is None: # This was the last attempt
             await downgrade_user(db, data.get("customer"))

    return JSONResponse({"received": True})
