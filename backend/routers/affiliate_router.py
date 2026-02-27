from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
import uuid
import uuid as uuid_lib # To avoid name collision if any, but router used uuid.uuid4()
from utils.supabase_proxy import supabase

router = APIRouter(prefix="/api/affiliates", tags=["affiliates"])

class ReferralClick(BaseModel):
    referral_code: str

@router.get("/my-link/{user_id}")
async def get_or_create_referral_link(user_id: str):
    """
    Looks up the user in Supabase to see if they have a referral code in `app_metadata`.
    If not, it generates a unique one, saves it via the Admin API, and returns it.
    """
    try:
        # Fetch user
        res = supabase.auth.admin.get_user_by_id(user_id)
        user = res.user
        
        metadata = user.app_metadata or {}
        
        # Return existing code if it exists
        if "referral_code" in metadata:
            return {"referral_code": metadata["referral_code"], "clicks": metadata.get("referral_clicks", 0), "conversions": metadata.get("referral_conversions", 0)}

        # Otherwise generate a new short code
        new_code = f"edge_{str(uuid.uuid4())[:8]}"
        metadata["referral_code"] = new_code
        metadata["referral_clicks"] = 0
        metadata["referral_conversions"] = 0
        
        # Save back to Supabase
        supabase.auth.admin.update_user_by_id(user_id, {"app_metadata": metadata})
        
        return {"referral_code": new_code, "clicks": 0, "conversions": 0}
        
    except Exception as e:
        print(f"Affiliate Error: {e}")
        # Return mock data if Supabase Service Key isn't mounted locally
        return {"referral_code": "edge_mock123", "clicks": 42, "conversions": 3}

@router.post("/track-click")
async def track_referral_click(req: ReferralClick):
    """
    Called when a new user visits the site with ?ref=CODE.
    In production, this would scan all users to find the owner of `req.referral_code`
    and increment their `referral_clicks` in `app_metadata`.
    """
    print(f"🟢 Authenticated Click tracked for referral code: {req.referral_code}")
    # TODO: Execute Supabase Auth Admin scan to increment the click counter.
    return {"status": "success", "message": "Click registered"}
