from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from datetime import datetime, timezone
import logging

router = APIRouter()

@router.get("/sharp-moves")
async def sharp_moves(
    sport: str = Query("basketball_nba"),
    db: Session = Depends(get_db),
):
    return {"sport": sport, "items": []}

@router.get("/freshness")
async def freshness(
    db: Session = Depends(get_db),
    sport: str = Query("basketball_nba"),
):
    try:
        from sqlalchemy import text
        result = await db.execute(text(f"""
            SELECT MAX(last_updated_at) as last_odds,
                   MAX(created_at) as last_ev
            FROM props_live
            WHERE sport = :sport
        """), {"sport": sport})
        row = result.mappings().first()
        
        return {
            "sport": sport,
            "status": "fresh",
            "last_odds_update": row["last_odds"].isoformat() if row and row["last_odds"] else None,
            "last_ev_update": row["last_ev"].isoformat() if row and row["last_ev"] else None,
            "server_time": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "sport": sport,
            "status": "error",
            "message": str(e),
            "last_odds_update": None,
            "last_ev_update": None,
            "server_time": datetime.now(timezone.utc).isoformat()
        }

# Alias for intel.py import
get_signals = sharp_moves
