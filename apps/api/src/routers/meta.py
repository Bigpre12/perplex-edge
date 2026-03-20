from datetime import datetime, timezone
from fastapi import APIRouter

from sqlalchemy import text
from db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from schemas.universal import UniversalResponse, ResponseMeta
from services.heartbeat_service import HeartbeatService
from middleware.request_id import get_request_id

router = APIRouter()

@router.get("/inspect", response_model=UniversalResponse[dict])
async def data_inspector(db: AsyncSession = Depends(get_async_db)):
    """Source verification: inspect row counts in core tables."""
    tables = [
        "odds", "line_ticks", "ev_signals", "ev_signals_history", 
        "props_live", "props_history", "edges_ev_history", 
        "unified_odds", "whale_moves", "injury_impact_events"
    ]
    counts = {}
    for t in tables:
        try:
            res = await db.execute(text(f"SELECT count(*) FROM {t}"))
            counts[t] = res.scalar()
        except Exception:
            counts[t] = -1 # Table might not exist yet
            
    return UniversalResponse(
        status="ok",
        meta=ResponseMeta(
            request_id=get_request_id(),
            db_rows=sum(c for c in counts.values() if c > 0),
            last_sync=datetime.now(timezone.utc)
        ),
        data=[counts]
    )

@router.get("/health", response_model=UniversalResponse[dict])
async def meta_health(db: AsyncSession = Depends(get_async_db)):
    heartbeats = await HeartbeatService.get_all_heartbeats(db)
    feeds = [{
        "name": h.feed_name,
        "status": h.status,
        "last_success": h.last_success_at.isoformat() if h.last_success_at else None,
        "rows_today": h.rows_written_today
    } for h in heartbeats]
    
    return UniversalResponse(
        status="ok",
        meta=ResponseMeta(
            request_id=get_request_id(),
            last_sync=datetime.now(timezone.utc)
        ),
        data=[{"service": "meta", "feeds": feeds}]
    )

@router.get("/summary", response_model=UniversalResponse[dict])
async def meta_summary():
    return UniversalResponse(
        status="ok",
        meta=ResponseMeta(request_id=get_request_id()),
        data=[{"app": "Perplex Edge"}]
    )

@router.get("/username")
async def meta_username():
    return {"username": "demo-user"}
