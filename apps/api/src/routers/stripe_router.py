from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
import stripe, os
from db.session import get_db
from sqlalchemy.orm import Session
from core.config import settings
from common_deps import get_db, require_elite
from api_utils.supabase_proxy import supabase

router = APIRouter(tags=["Stripe Monetization"])

# These should be pulled from secure environment variables in production
stripe.api_key = settings.STRIPE_SECRET_KEY or os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
# Note: settings doesn't cleanly export STRIPE_WEBHOOK_SECRET today, fallback to OS

# The price ID from your Stripe Dashboard for the "Pro Subscription" product.
PRO_PRICE_ID = getattr(settings, "STRIPE_PRO_PRICE_ID", os.environ.get("STRIPE_PRO_PRICE_ID"))

class CheckoutRequest(BaseModel):
    user_email: str
    user_id: str

@router.post("/create-checkout-session")
async def create_checkout_session(req: CheckoutRequest):
    try:
        # Prevent mock key bypass if not in development mode
        if not stripe.api_key:
            if not settings.DEVELOPMENT_MODE:
                raise HTTPException(status_code=400, detail="Stripe Secret Key not configured for production.")
            return {"session_url": settings.FRONTEND_URL + '/institutional/settings?checkout=success&mock=true'}

        # Get the latest price ID dynamically at request time
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

        # Create a new Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=req.user_email,
            client_reference_id=req.user_id, # Link the Stripe session back to the user ID
            line_items=[{
                'price': settings.STRIPE_PRO_MONTHLY_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=settings.FRONTEND_URL + '/institutional/settings?checkout=success',
            cancel_url=settings.FRONTEND_URL + '/institutional/settings?checkout=canceled',
        )
        return {"session_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Use client_reference_id if it's the local DB ID, or search by email
        user_id = session.get('client_reference_id')
        customer_email = session.get('customer_details', {}).get('email')
        
        from models.user import User

        # Search for user to update
        user = None
        if user_id and user_id.isdigit():
            stmt = select(User).where(User.id == int(user_id))
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
        elif customer_email:
            stmt = select(User).where(User.email == customer_email)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

        if user:
            # Resolve tier dynamically from price ID
            from services.stripe_service import stripe_service
            
            line_items = session.get('line_items', {}).get('data', [])
            if not line_items:
                # Fallback: try to get from the session's subscription object if available
                try:
                    sub_id = session.get('subscription')
                    if sub_id:
                        subscription = stripe.Subscription.retrieve(sub_id)
                        price_id = subscription['items']['data'][0]['price']['id']
                    else:
                        price_id = settings.STRIPE_PRO_MONTHLY_PRICE_ID # Default
                except:
                    price_id = settings.STRIPE_PRO_MONTHLY_PRICE_ID
            else:
                price_id = line_items[0]['price']['id']

            user.subscription_tier = stripe_service.resolve_tier(price_id)
            await db.commit()
            
            # Sync with Supabase profiles
            try:
                if user.clerk_id:
                    print(f"[Supabase] Syncing {user.subscription_tier} for clerk_id {user.clerk_id}")
                    await supabase.table("profiles").update({
                        "tier": user.subscription_tier
                    }).eq("clerk_id", user.clerk_id).execute()
            except Exception as e:
                print(f"[Supabase] Sync failed: {e}")

            print(f"✅ Subscription tier updated to {user.subscription_tier} for user {user.email}")
        else:
            print(f"⚠️ User not found for Stripe completion: ID={user_id}, Email={customer_email}")
            
    return {"status": "success"}
