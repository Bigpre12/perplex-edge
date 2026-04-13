import logging
from typing import Dict, Any
from sqlalchemy import select, func
from db.session import AsyncSessionLocal
from models.brain import UnifiedEVSignal

logger = logging.getLogger(__name__)

async def get_dashboard_metrics(db=None) -> Dict[str, Any]:
    """
    Returns core system metrics. Accepts optional db session from routers.
    """
    try:
        async def _fetch(session) -> Dict[str, Any]:
            ev_count = await session.scalar(
                select(func.count()).select_from(UnifiedEVSignal)
            )
            avg_ev = await session.scalar(
                select(func.avg(UnifiedEVSignal.edge_percent))
            )
            return {
                "total_ev_signals": int(ev_count) if ev_count is not None else 0,
                "average_ev": round(float(avg_ev), 4) if avg_ev is not None else 0.0,
            }

        if db:
            return await _fetch(db)
        else:
            async with AsyncSessionLocal() as session:
                return await _fetch(session)
    except Exception as e:
        logger.error(f"dashboard metrics error: {e}")
        return {"total_ev_signals": 0, "average_ev": 0.0}
