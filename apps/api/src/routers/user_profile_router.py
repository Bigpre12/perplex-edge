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
    This creates a competitive environment and drives user retention.
    """
    # Mocking a list of verified top performers
    # In production, this would be a cached aggregation of the users table
    top_users = [
        {"username": "Oracle_Alpha", "roi": 8.4, "win_rate": 57.2, "volume": 412, "rank": 1},
        {"username": "EdgeMaster", "roi": 7.1, "win_rate": 56.5, "volume": 289, "rank": 2},
        {"username": "SharpBettor_99", "roi": 6.8, "win_rate": 55.9, "volume": 156, "rank": 3},
        {"username": "MiddlingKing", "roi": 5.2, "win_rate": 54.1, "volume": 842, "rank": 4},
        {"username": "ArbHunter", "roi": 4.9, "win_rate": 53.8, "volume": 1205, "rank": 5},
    ]
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
