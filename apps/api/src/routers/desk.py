# apps/api/src/routers/desk.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from db.session import get_async_db
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/desk", tags=["desk"])

@router.get("/summary")
async def get_desk_summary(
    db: AsyncSession = Depends(get_async_db)
):
    """
    Main Dashboard (Desk) Summary metrics.
    """
    try:
        # Aggregated stats for the Desk
        # 1. Total props currently live
        props_stmt = text("SELECT COUNT(*) FROM props_live")
        props_res = await db.execute(props_stmt)
        props_count = props_res.scalar() or 0
        
        # 2. Total active edges
        edges_stmt = text("SELECT COUNT(*) FROM ev_signals")
        edges_res = await db.execute(edges_stmt)
        edges_count = edges_res.scalar() or 0
        
        # 3. Model Status (Heartbeat check)
        from services.heartbeat_service import HeartbeatService
        hb = await HeartbeatService.get_heartbeat(db, "ingest_basketball_nba")
        
        return {
            "status": "ok",
            "metrics": {
                "live_props": props_count,
                "active_edges": edges_count,
                "engine_status": "healthy",
                "last_update": hb.last_success_at if hb else None
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Desk Summary Error: {e}")
        return {"status": "error", "message": str(e)}
