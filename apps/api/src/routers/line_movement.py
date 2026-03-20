from fastapi import APIRouter, Query, Depends
from typing import Optional, List, Dict, Any
from services.line_movement_service import line_movement_service
from common_deps import get_user_tier

router = APIRouter(tags=["line_movement"])

@router.get("")
@router.get("/")
async def get_line_movement(
    sport: str = "basketball_nba",
    lookback: int = Query(15, description="Lookback minutes for movement detection"),
    tier: str = Depends(get_user_tier)
):
    """
    Returns active market movements (Steam, Whales, Sharp Moves) 
    based on real-time LineTick analysis.
    """
    # Tier check: Movement scanner usually requires Pro/Elite
    if tier == "free":
        # Return empty but with a message for the UI to gate it if needed
        return {
            "status": "gated",
            "message": "Premium subscription required for Line Movement scanner.",
            "data": [],
            "count": 0
        }

    try:
        moves = await line_movement_service.get_active_moves(sport, lookback_minutes=lookback)
        return {
            "status": "active",
            "count": len(moves),
            "data": moves
        }
    except Exception as e:
        import logging
        logging.error(f"Router: line_movement failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "data": [],
            "count": 0
        }
