from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import get_async_db
from models.users import User
from pydantic import BaseModel
import secrets
import string

router = APIRouter(prefix="/api/referrals", tags=["referrals"])

def generate_referral_code():
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

@router.get("/{user_id}")
async def get_referral_status(user_id: str, db = Depends(get_async_db)):
    # Try to parse as int for local ID lookup
    try:
        if user_id.isdigit():
            stmt = select(User).filter(User.id == int(user_id))
        else:
            # Fallback to search by email if it looks like one
            stmt = select(User).filter(User.email == user_id)
            
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {
            "referral_code": getattr(user, 'referral_code', 'LUC_' + generate_referral_code()),
            "total_referrals": getattr(user, 'referrals_count', 0),
            "pending_rewards": getattr(user, 'pending_rewards', 0)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class ApplyReferralRequest(BaseModel):
    user_id: str
    referral_code: str

@router.post("/apply")
async def apply_referral(req: ApplyReferralRequest, db = Depends(get_async_db)):
    # Rough stub for applying a referral
    stmt = select(User).filter(User.referral_code == req.referral_code)
    res = await db.execute(stmt)
    referrer = res.scalar_one_or_none()
    
    if not referrer:
        raise HTTPException(status_code=400, detail="Invalid referral code")
        
    # Check if user is referring themselves
    if req.user_id.isdigit() and int(req.user_id) == referrer.id:
        raise HTTPException(status_code=400, detail="Cannot refer yourself")
    elif req.user_id == referrer.email:
        raise HTTPException(status_code=400, detail="Cannot refer yourself")
        
    return {"message": "Referral applied successfully!"}
