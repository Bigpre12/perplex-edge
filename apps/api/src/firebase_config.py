# firebase_config.py
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
# Expects GOOGLE_APPLICATION_CREDENTIALS to point to the service account JSON file
try:
    if not firebase_admin._apps:
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin initialized with service account.")
        else:
            # Try ADC, but catch if it fails too
            try:
                firebase_admin.initialize_app()
                logger.info("Firebase Admin initialized with ADC.")
            except Exception:
                logger.warning("Firebase Admin initialization failed. Firestore features will be disabled.")
except Exception as e:
    logger.error(f"Failed to initialize Firebase Admin: {e}")

# Global Firestore client (could be None if initialization failed)
try:
    db = firestore.client()
except Exception:
    db = None
    logger.warning("Firestore client not available.")

def verify_token(id_token: str) -> dict:
    """Verify Firebase JWT token and return decoded claims."""
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        logger.error(f"Invalid token verification attempt: {e}")
        raise ValueError(f"Invalid token: {e}")

def get_user_plan(uid: str) -> str:
    """Get user subscription plan from Firestore."""
    if db is None:
        return "free"
    try:
        doc = db.collection("users").document(uid).get()
        if doc.exists:
            return doc.to_dict().get("plan", "free")
    except Exception as e:
        logger.error(f"Error fetching plan for {uid}: {e}")
        return "free"

def set_user_trial(uid: str, days: int = 7):
    """Sets a trial expiration date for a new user."""
    if db is None:
        return False
    try:
        from datetime import datetime, timedelta
        expires_at = datetime.now() + timedelta(days=days)
        db.collection("users").document(uid).set({
            "trial_ends_at": expires_at,
            "plan": "pro" # Default to pro trial
        }, merge=True)
        return True
    except Exception as e:
        logger.error(f"Error setting trial for {uid}: {e}")
        return False

def get_business_metrics():
    """Calculate LTV and Churn from Firestore/Database."""
    # This is a stub that would normally query the 'payments' and 'users' collections
    # For now, it returns the unit economics logic for the dashboard
    return {
        "avg_ltv": 145.50, # Mocked institutional data
        "monthly_churn": 4.2, # Percentage
        "active_trials": 128,
        "conversion_rate": 12.5
    }
