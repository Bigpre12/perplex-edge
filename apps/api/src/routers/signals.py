from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.session import get_db
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/sharp-moves")
async def sharp_moves(
    sport: str = Query("basketball_nba"),
    db: AsyncSession = Depends(get_db),
):
    return {"sport": sport, "items": []}

@router.get("/freshness")
async def freshness(
    db: AsyncSession = Depends(get_db),
    sport: str = Query("basketball_nba"),
):
    try:
        result = await db.execute(text("""
            SELECT MAX(last_updated_at) as last_odds,
                   MAX(created_at) as last_ev
            FROM props_live
            WHERE sport = :sport
        """), {"sport": sport})
        row = result.mappings().first()
        
        # Calculate age if needed by frontend
        last_odds = row["last_odds"] if row and row["last_odds"] else None
        
        return {
            "sport": sport,
            "status": "fresh",
            "last_odds_update": last_odds.isoformat() if last_odds else None,
            "last_ev_update": row["last_ev"].isoformat() if row and row["last_ev"] else None,
            "server_time": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Freshness check failed: {e}")
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
