from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
import stripe
import os
from database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/stripe", tags=["Stripe Monetization"])

# These should be pulled from secure environment variables in production
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_mock_key_only")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_mock_secret")

# The price ID from your Stripe Dashboard for the "Pro Subscription" product
PRO_PRICE_ID = os.environ.get("STRIPE_PRO_PRICE_ID", "price_mock_id")

class CheckoutRequest(BaseModel):
    user_email: str
    user_id: str

@router.post("/create-checkout-session")
async def create_checkout_session(req: CheckoutRequest):
    try:
        # Create a new Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=req.user_email,
            client_reference_id=req.user_id, # Link the Stripe session back to the Supabase User ID!
            line_items=[{
                'price': PRO_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=os.environ.get("FRONTEND_URL", "http://localhost:3000") + '/institutional/settings?checkout=success',
            cancel_url=os.environ.get("FRONTEND_URL", "http://localhost:3000") + '/institutional/settings?checkout=canceled',
        )
        return {"session_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        # Verify the webhook signature against Stripe's secret
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the successful checkout session event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        user_id = session.get('client_reference_id')
        customer_id = session.get('customer')
        
        if user_id:
            print(f"✅ Subscription Activated for Supabase User: {user_id}")
            # TODO: Here you would use the Supabase Admin SDK to update the user's `app_metadata` to { "tier": "pro" }
            # Or update a custom `profiles` table in Postgres where id = user_id 
            pass
            
    return {"status": "success"}
