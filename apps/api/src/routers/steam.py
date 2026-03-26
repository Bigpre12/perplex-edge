# apps/api/src/routers/steam.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Query, Depends
from typing import Optional
from db.session import get_db, get_async_db
from datetime import datetime, timedelta, timezone

router = APIRouter(tags=["steam"])

# In-memory store for deduplication across requests

@router.get("")
@router.get("/alerts")
async def steam_alerts(
    sport: Optional[str] = Query("basketball_nba"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Returns live steam alerts from the persistent steam_events table.
    """
    from models.brain import SteamEvent
    from sqlalchemy import select, desc
    
    stmt = select(SteamEvent).where(SteamEvent.sport == sport)
    stmt = stmt.where(SteamEvent.timestamp >= datetime.now(timezone.utc) - timedelta(hours=24))
    stmt = stmt.order_by(desc(SteamEvent.timestamp)).limit(20)
    
    result = await db.execute(stmt)
    events = result.scalars().all()
    
    # Map to expected frontend format
    alerts = []
    for e in events:
        alerts.append({
            "player_name": e.player_name,
            "stat_type": e.stat_type,
            "side": e.side,
            "line": float(e.line) if e.line else 0.0,
            "movement": float(e.movement) if e.movement else 0.0,
            "severity": float(e.severity) if e.severity else 0.0,
            "description": e.description,
            "detected_at": e.timestamp.isoformat() if e.timestamp else None,
            "book_count": e.book_count
        })

    return {
        "alerts": alerts,
        "total": len(alerts),
        "sport": sport,
        "status": "success"
    }
