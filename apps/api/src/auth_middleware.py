# auth_middleware.py
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_config import verify_token, get_user_plan
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

# Normalize owner emails for case-insensitive matching
OWNER_EMAILS = [email.strip().lower() for email in os.getenv("OWNER_EMAILS", "").split(",") if email.strip()]
security = HTTPBearer()

async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """FastAPI dependency to verify Firebase Auth token."""
    token = credentials.credentials
    try:
        user = verify_token(token)
        return user
    except ValueError as e:
        logger.warning(f"Unauthorized access attempt: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))

async def require_pro(user=Depends(require_auth)):
    """FastAPI dependency to verify Pro plan or higher/active trial."""
    uid = user.get("uid")
    # Fetch full user data from Firestore for trial check
    from firebase_config import db_fs
    user_doc = db_fs.collection("users").document(uid).get()
    user_data = user_doc.to_dict() if user_doc.exists else {}
    
    plan = user_data.get("plan", "free")
    email = user.get("email", "").lower()
    
    # OWNER BYPASS
    if email in OWNER_EMAILS:
        logger.info(f"Owner bypass triggered for {email} (UID: {uid})")
        return user

    trial_ends_at = user_data.get("trial_ends_at")
    
    is_trial_active = trial_ends_at and trial_ends_at.replace(tzinfo=None) > datetime.now()
    
    if plan not in ("pro", "premium", "elite", "syndicate", "admin") and not is_trial_active:
        logger.info(f"Access denied for user {uid} (Plan: {plan}, Trial Active: {is_trial_active})")
        raise HTTPException(
            status_code=403,
            detail="Lucrix Pro subscription or active trial required."
        )
    return user

async def require_elite(user=Depends(require_auth)):
    """FastAPI dependency to verify Elite plan or higher."""
    uid = user.get("uid")
    email = user.get("email", "").lower()
    
    if email in OWNER_EMAILS:
        return user
        
    plan = get_user_plan(uid)
    if plan not in ("elite", "syndicate", "admin"):
        logger.info(f"Access denied for user {uid} (Plan: {plan})")
        raise HTTPException(
            status_code=403,
            detail="Lucrix Elite subscription required."
        )
    return user

async def require_syndicate(user=Depends(require_auth)):
    """FastAPI dependency to verify Syndicate ($99/mo) plan."""
    uid = user.get("uid")
    email = user.get("email", "").lower()
    
    if email in OWNER_EMAILS:
        return user
        
    plan = get_user_plan(uid)
    if plan not in ("syndicate", "admin"):
        logger.info(f"Access denied for user {uid} (Plan: {plan})")
        raise HTTPException(
            status_code=403,
            detail="Lucrix Syndicate subscription required."
        )
    return user

async def require_elite(user=Depends(require_auth)):
    """FastAPI dependency to verify Elite plan."""
    uid = user.get("uid")
    plan = get_user_plan(uid)
    if plan not in ("elite", "admin"):
        logger.info(f"Access denied for user {uid} (Plan: {plan})")
        raise HTTPException(
            status_code=403,
            detail="Lucrix Elite subscription required for this operation."
        )
    return user
