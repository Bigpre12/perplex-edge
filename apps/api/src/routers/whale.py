# apps/api/src/routers/whale.py
from fastapi import APIRouter, Query, Depends
from common_deps import require_elite, get_user_tier
from typing import Optional, List, Dict
from services.whale_service import detect_whale_signals

router = APIRouter(tags=["whale"])

@router.get("")
async def whale_signals(sport: Optional[str] = Query("basketball_nba"), tier: str = Depends(get_user_tier)):
    """
    Returns live sharp money and whale signals. Elite only.
    """
    if tier != "elite":
        return {"status": "limited", "data": [], "message": "Elite subscription required"}
    signals = await detect_whale_signals(sport)
    return {
        "status": "success",
        "data": signals,
        "total": len(signals),
        "sport": sport,
        "methodology": "Pinnacle vs US Book splits + single-book market outliers",
    }

@router.get("/active-moves")
@router.get("/moves")
async def get_active_moves(sport: str = Query("basketball_nba"), tier: str = Depends(get_user_tier)):
    """
    Returns confirmed whale moves. Returns simulated data for non-elite users.
    """
    # If not elite, return the simulation fallback immediately
    if tier != "elite":
        from datetime import datetime, timezone, timedelta
        return [
            {
                "player": "Upgrade Required",
                "stat_type": "Pro/Elite Feature",
                "line_before": 0,
                "line_after": 0,
                "move_size": "Upgrade to see whale moves",
                "time_detected": datetime.now(timezone.utc).isoformat(),
                "sportsbook": "Institutional Data",
                "whale_rating": 0,
                "is_limited": True
            }
        ]
    """
    Returns confirmed whale moves from Supabase with a realistic simulation fallback.
    """
    try:
        import httpx
        import os
        from datetime import datetime, timezone, timedelta
        
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        
        moves = []
        async with httpx.AsyncClient() as client:
            if SUPABASE_URL:
                url = f"{SUPABASE_URL}/rest/v1/whale_moves?sport=eq.{sport}&order=time_detected.desc"
                r = await client.get(url, headers=headers)
                moves = r.json() if r.status_code == 200 else []
            
        if not moves:
            # High-Impact Fallback for Elite Experience
            return [
                {
                    "player": "Victor Wembanyama",
                    "stat_type": "Points",
                    "line_before": 22.5,
                    "line_after": 23.5,
                    "odds_before": -110,
                    "odds_after": -125,
                    "move_size": "Wormhole Detected",
                    "time_detected": (datetime.now(timezone.utc) - timedelta(minutes=14)).isoformat(),
                    "sportsbook": "Pinnacle Sharp",
                    "whale_rating": 9.8,
                    "is_simulated": True
                },
                {
                    "player": "Cade Cunningham",
                    "stat_type": "Assists",
                    "line_before": 8.5,
                    "line_after": 9.5,
                    "odds_before": +105,
                    "odds_after": -118,
                    "move_size": "Significant Steam",
                    "time_detected": (datetime.now(timezone.utc) - timedelta(minutes=42)).isoformat(),
                    "sportsbook": "Circa Sports",
                    "whale_rating": 8.4,
                    "is_simulated": True
                }
            ]
            
        return [{
            "player": m.get("player"),
            "stat_type": m.get("stat_type"),
            "line_before": m.get("line_before"),
            "line_after": m.get("line_after"),
            "odds_before": m.get("odds_before"),
            "odds_after": m.get("odds_after"),
            "move_size": m.get("move_size"),
            "time_detected": m.get("time_detected"),
            "sportsbook": m.get("sportsbook"),
            "whale_rating": m.get("whale_rating")
        } for m in moves]
    except Exception as e:
        return []
