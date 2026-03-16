from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
import stripe, os
from db.session import get_db
from sqlalchemy.orm import Session
from core.config import settings
from common_deps import get_db, require_elite

router = APIRouter(prefix="/stripe", tags=["Stripe Monetization"])

# These should be pulled from secure environment variables in production
stripe.api_key = settings.STRIPE_SECRET_KEY or os.environ.get("STRIPE_SECRET_KEY", "sk_test_mock_key_only")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_mock_secret")
# Note: settings doesn't cleanly export STRIPE_WEBHOOK_SECRET today, fallback to OS

# The price ID from your Stripe Dashboard for the "Pro Subscription" product.
PRO_PRICE_ID = getattr(settings, "STRIPE_PRO_PRICE_ID", os.environ.get("STRIPE_PRO_PRICE_ID", "price_mock_id"))

class CheckoutRequest(BaseModel):
    user_email: str
    user_id: str

@router.post("/create-checkout-session")
async def create_checkout_session(req: CheckoutRequest):
    try:
        # Prevent mock key bypass if not in development mode
        if stripe.api_key == "sk_test_mock_key_only":
            if not settings.DEVELOPMENT_MODE:
                raise HTTPException(status_code=400, detail="Stripe Secret Key not configured for production.")
            return {"session_url": settings.FRONTEND_URL + '/institutional/settings?checkout=success&mock=true'}

        # Get the latest price ID dynamically at request time
        price_id = os.environ.get("STRIPE_PRO_PRICE_ID", "price_mock_id")

        # Create a new Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=req.user_email,
            client_reference_id=req.user_id, # Link the Stripe session back to the user ID
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=settings.FRONTEND_URL + '/institutional/settings?checkout=success',
            cancel_url=settings.FRONTEND_URL + '/institutional/settings?checkout=canceled',
        )
        return {"session_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
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
        from sqlalchemy import update, select

        # Search for user to update
        user = None
        if user_id and user_id.isdigit():
            user = db.query(User).filter(User.id == int(user_id)).first()
        elif customer_email:
            user = db.query(User).filter(User.email == customer_email).first()

        if user:
            user.subscription_tier = "pro"
            db.commit()
            print(f"✅ Subscription tier updated to pro for user {user.email}")
        else:
            print(f"⚠️ User not found for Stripe completion: ID={user_id}, Email={customer_email}")
            
    return {"status": "success"}
