from fastapi import APIRouter, HTTPException, Depends
from models.users import User
from routers.auth import get_current_user
import stripe
import os
from config import settings

router = APIRouter(tags=["user"])
stripe.api_key = settings.STRIPE_SECRET_KEY or os.getenv("STRIPE_SECRET_KEY")

@router.get("/tier")
async def get_user_tier(current_user: User = Depends(get_current_user)):
    return {
        "tier": (current_user.subscription_tier or "free").lower(),
        "status": "active",
    }

@router.get("/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "subscription_tier": (current_user.subscription_tier or "free").lower(),
    }

from services import stripe_service

@router.post("/create-checkout")
async def create_checkout(
    body: dict,
    current_user: User = Depends(get_current_user)
):
    price_id = body.get("price_id")
    if not price_id:
        raise HTTPException(status_code=400, detail="price_id required")

    try:
        session = stripe_service.create_checkout_session(
            price_id=price_id,
            customer_email=current_user.email,
            client_reference_id=str(current_user.id)
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/billing-portal")
async def billing_portal(current_user: User = Depends(get_current_user)):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe API key not configured")
        
    try:
        customers = stripe.Customer.list(email=current_user.email, limit=1)
        if not customers.data:
            raise HTTPException(status_code=404, detail="No subscription found")
            
        portal = stripe.billing_portal.Session.create(
            customer=customers.data[0].id,
            return_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3300')}/dashboard",
        )
        return {"portal_url": portal.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
