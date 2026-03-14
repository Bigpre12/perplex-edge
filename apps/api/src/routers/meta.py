# apps/api/src/routers/meta.py
from fastapi import APIRouter, Query, Depends
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from models.unified import UnifiedOdds, UnifiedEVSignal

router = APIRouter(tags=["Metadata"])

@router.get("/freshness")
async def get_freshness(sport: str = Query(...), session: AsyncSession = Depends(get_async_db)):
    """Returns the latest ingestion and computation timestamps for a sport."""
    # 1. Latest Odds
    stmt_odds = select(func.max(UnifiedOdds.ingested_ts)).where(UnifiedOdds.sport == sport)
    res_odds = await session.execute(stmt_odds)
    odds_ts = res_odds.scalar()
    
    # 2. Latest EV Engine Run
    stmt_ev = select(func.max(UnifiedEVSignal.updated_at)).where(UnifiedEVSignal.sport == sport)
    res_ev = await session.execute(stmt_ev)
    ev_ts = res_ev.scalar()
        
    return {
        "sport": sport,
        "odds_last_updated": odds_ts.isoformat() if odds_ts else None,
        "ev_last_updated": ev_ts.isoformat() if ev_ts else None,
        "server_time": datetime.now(timezone.utc).isoformat()
    }
