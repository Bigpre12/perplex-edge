from fastapi import APIRouter, Query, Depends
from typing import Optional, List, Dict, Any
from services.line_movement_service import line_movement_service
from common_deps import get_user_tier
from db.session import AsyncSessionLocal

router = APIRouter(tags=["line_movement"])


@router.get("/history/{sport}")
async def get_line_movement_history(
    sport: str,
    hours: int = Query(24, ge=1, le=168),
    tier: str = Depends(get_user_tier),
):
    """
    Line movement from line_movement_history (TheOddsAPI snapshots after ingest).
    """
    if tier == "free":
        return {
            "status": "gated",
            "message": "Premium subscription required.",
            "data": [],
            "count": 0,
        }
    try:
        from services.line_tracker import get_movement_for_sport

        async with AsyncSessionLocal() as db:
            rows = await get_movement_for_sport(db, sport, hours=hours)
        return {"status": "ok", "count": len(rows), "data": rows, "sport": sport}
    except Exception as e:
        import logging

        logging.error("line_movement history: %s", e)
        return {"status": "error", "message": str(e), "data": [], "count": 0}


@router.get("")
@router.get("/")
async def get_line_movement(
    sport: str = "basketball_nba",
    event_id: Optional[str] = Query(None),
    lookback: int = Query(15, description="Lookback minutes for movement detection"),
    tier: str = Depends(get_user_tier)
):
    """
    Returns active market movements (Steam, Whales, Sharp Moves) 
    OR specific event history if event_id is provided.
    """
    # Tier check: Movement scanner usually requires Pro/Elite
    if tier == "free":
        return {
            "status": "gated",
            "message": "Premium subscription required for Line Movement scanner.",
            "data": [],
            "count": 0
        }

    try:
        if event_id:
            # Return detailed book-level history for sparklines
            res = await line_movement_service.get_movement_for_event(event_id, sport)
            return {
                "status": "active",
                "event_id": event_id,
                "books": res.get("books", [])
            }

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
