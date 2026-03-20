from datetime import datetime, timezone
from fastapi import APIRouter

from sqlalchemy import text
from db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

router = APIRouter()

@router.get("/inspect")
async def data_inspector(db: AsyncSession = Depends(get_async_db)):
    """Source verification: inspect row counts in core tables."""
    tables = [
        "odds", "line_ticks", "ev_signals", "ev_signals_history", 
        "props_live", "props_history", "edges_ev_history", 
        "whale_moves", "injury_impact_events"
    ]
    counts = {}
    for t in tables:
        try:
            # Note: This is a diagnostic endpoint, table presence check
            res = await db.execute(text(f"SELECT count(*) FROM {t}"))
            counts[t] = res.scalar()
        except Exception:
            counts[t] = -1 # Table might not exist yet
            
    return {
        "status": "inspector_active",
        "counts": counts,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/health")
async def meta_health():
    return {
        "status": "healthy",
        "service": "meta",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@router.get("/summary")
async def meta_summary():
    return {
        "status": "ok",
        "app": "Perplex Edge",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@router.get("/username")
async def meta_username():
    return {"username": "demo-user"}
