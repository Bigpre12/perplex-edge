from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.session import get_db
from datetime import datetime, timezone
from services.heartbeat_service import HeartbeatService
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
        # 1. Fetch Ingestion Heartbeat (last odds update)
        ingest_hb = await HeartbeatService.get_heartbeat(db, f"ingest_{sport}")
        last_odds = ingest_hb.last_success_at if ingest_hb else None
        
        # 2. Fetch EV/Intelligence Heartbeat (last ev update)
        # We try ev_grader first, then intelligence
        ev_hb = await HeartbeatService.get_heartbeat(db, f"ev_grader_{sport}")
        if not ev_hb:
            ev_hb = await HeartbeatService.get_heartbeat(db, f"intelligence_{sport}")
        
        last_ev = ev_hb.last_success_at if ev_hb else None
        
        return {
            "sport": sport,
            "status": "fresh" if last_odds else "stale",
            "last_odds_update": last_odds.isoformat() if last_odds else None,
            "last_ev_update": last_ev.isoformat() if last_ev else None,
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
