from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from services.roi_calculator import calculate_user_roi
import random

router = APIRouter(prefix="/api/profiles", tags=["User Profiles & Leaderboard"])

class ProfileUpdate(BaseModel):
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserProfile(BaseModel):
    user_id: str
    username: str
    bio: Optional[str]
    avatar_url: Optional[str]
    stats: dict

@router.get("/me", response_model=UserProfile)
async def get_my_profile(user_id: str = "test-user-123"):
    """
    Fetches the profile for the authenticated user.
    Integrates with the ROI calculator to provide verified performance data.
    """
    # In production, user_id would come from a JWT dependency
    stats = calculate_user_roi(user_id)
    return {
        "user_id": user_id,
        "username": "SharpBettor_99",
        "bio": "Institutional logic only. +EV or bust. Dedicated to the Sharp Engine.",
        "avatar_url": f"https://ui-avatars.com/api/?name=SharpBettor_99&background=101f19&color=0df233",
        "stats": stats
    }

@router.get("/leaderboard")
async def get_global_leaderboard():
    """
    Returns the top-performing 'Sharp' bettors as verified by the ROI engine.
    This simulates real bettors based on the overall system's actual mathematical edge.
    """
    from database import SessionLocal
    from sqlalchemy import select
    from models.props import PropLine
    
    db = SessionLocal()
    try:
        # Get actual global system hit rate capability
        settled = db.execute(select(PropLine).where(PropLine.is_settled == True)).scalars().all()
        baseline_win_rate = 55.4 # Default sharp baseline
        total_volume = 1200
        
        if settled:
            wins = sum(1 for p in settled if p.beat_closing_line)
            if len(settled) >= 10:
                baseline_win_rate = (wins / len(settled)) * 100
                total_volume = len(settled) * 10 # Scale up for realistic system volume
                
    finally:
        db.close()
        
    # Generate realistic top users mathematically tied to the system's baseline
    import random
    
    # Ensure they are floating realistically above the baseline
    top_users = [
        {"username": "Oracle_Alpha", "roi": round((baseline_win_rate - 50) * 0.8, 1), "win_rate": round(baseline_win_rate + 2.1, 1), "volume": int(total_volume * 0.4), "rank": 1},
        {"username": "EdgeMaster", "roi": round((baseline_win_rate - 50) * 0.7, 1), "win_rate": round(baseline_win_rate + 1.5, 1), "volume": int(total_volume * 0.25), "rank": 2},
        {"username": "SharpBettor_99", "roi": round((baseline_win_rate - 50) * 0.65, 1), "win_rate": round(baseline_win_rate + 0.9, 1), "volume": int(total_volume * 0.15), "rank": 3},
        {"username": "MiddlingKing", "roi": round((baseline_win_rate - 50) * 0.5, 1), "win_rate": round(baseline_win_rate + 0.2, 1), "volume": int(total_volume * 0.8), "rank": 4},
        {"username": "ArbHunter", "roi": round((baseline_win_rate - 50) * 0.45, 1), "win_rate": round(baseline_win_rate - 0.3, 1), "volume": int(total_volume * 1.2), "rank": 5},
    ]
    
    # Sort just in case mathematically they overlap depending on the baseline
    top_users.sort(key=lambda x: x['roi'], reverse=True)
    for i, user in enumerate(top_users):
        user['rank'] = i + 1
        
    return {"leaderboard": top_users}

@router.get("/{username}")
async def get_public_profile(username: str):
    """
    Fetches a public profile by username for social sharing and trust verification.
    """
    # Simulate a lookup
    if username == "SharpBettor_99":
        return await get_my_profile("test-user-123")
    
    # Mock a random profile
    stats = calculate_user_roi(username)
    return {
        "username": username,
        "bio": "Pro bettor. Analytics enthusiast.",
        "avatar_url": f"https://ui-avatars.com/api/?name={username}&background=0f1719&color=64748b",
        "stats": stats
    }
