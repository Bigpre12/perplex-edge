import stripe
import os
import logging
from core.config import settings

logger = logging.getLogger(__name__)

# Centralize Stripe API Key
stripe.api_key = settings.STRIPE_SECRET_KEY or os.getenv("STRIPE_SECRET_KEY")

class StripeService:
    def __init__(self):
        self.frontend_url = settings.FRONTEND_URL.rstrip('/')

    def resolve_tier(self, price_id: str) -> str:
        """Maps Stripe Price IDs to internal tier names."""
        price_map = {
            settings.STRIPE_PRO_MONTHLY_PRICE_ID: "pro",
            settings.STRIPE_PRO_ANNUAL_PRICE_ID: "pro",
            settings.STRIPE_ELITE_MONTHLY_PRICE_ID: "elite",
            settings.STRIPE_ELITE_ANNUAL_PRICE_ID: "elite",
        }
        # Also check env directly in case settings haven't refreshed
        if not price_map.get(price_id):
            if price_id in [os.getenv("STRIPE_PRO_MONTHLY_PRICE_ID"), os.getenv("STRIPE_PRO_ANNUAL_PRICE_ID")]:
                return "pro"
            if price_id in [os.getenv("STRIPE_ELITE_MONTHLY_PRICE_ID"), os.getenv("STRIPE_ELITE_ANNUAL_PRICE_ID")]:
                return "elite"
        
        return price_map.get(price_id, "free")

    def create_checkout_session(
        self,
        price_id: str,
        customer_email: str,
        user_id: str,
        success_path: str = "/dashboard?upgraded=true",
        cancel_path: str = "/pricing",
        mode: str = "subscription"
    ):
        """Creates a Stripe Checkout Session with user_id metadata."""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode=mode,
                line_items=[{"price": price_id, "quantity": 1}],
                customer_email=customer_email,
                success_url=f"{self.frontend_url}{success_path}",
                cancel_url=f"{self.frontend_url}{cancel_path}",
                client_reference_id=user_id,
                metadata={"user_id": user_id},
                subscription_data={"trial_period_days": 7} if mode == "subscription" else None,
                allow_promotion_codes=True,
            )
            return session.url
        except Exception as e:
            logger.error(f"Stripe Checkout Error: {e}")
            raise e

    def create_portal_session(self, customer_id: str):
        """Creates a Stripe Customer Portal session."""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=f"{self.frontend_url}/dashboard",
            )
            return session.url
        except Exception as e:
            logger.error(f"Stripe Portal Error: {e}")
            raise e

    async def get_subscription_status(self, customer_id: str):
        """Retrieves active subscription tier and status for a customer."""
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status="active",
                limit=1
            )
            if not subscriptions.data:
                return {"status": "inactive", "tier": "free"}
            
            sub = subscriptions.data[0]
            price_id = sub['items']['data'][0]['price']['id']
            return {
                "status": sub.status,
                "tier": self.resolve_tier(price_id),
                "current_period_end": sub.current_period_end
            }
        except Exception as e:
            logger.error(f"Stripe Status Error: {e}")
            return {"status": "error", "tier": "free"}

stripe_service = StripeService()
