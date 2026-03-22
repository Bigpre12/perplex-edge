import logging
from sqlalchemy import select, func
from db.session import AsyncSessionLocal
from models import UnifiedEVSignal, PropLive

logger = logging.getLogger(__name__)

async def get_dashboard_metrics(db=None) -> dict:
    """
    Returns high-level system metrics used by StatsCards.
    Supports usage with an existing session (from FastAPI Depends) or standalone.
    """
    try:
        async def _fetch_metrics(session):
            ev_count = await session.scalar(select(func.count()).select_from(UnifiedEVSignal))
            prop_count = await session.scalar(select(func.count()).select_from(PropLive))
            avg_ev = await session.scalar(select(func.avg(UnifiedEVSignal.edge_percent)))
            
            return {
                "total_ev_signals": ev_count or 0,
                "total_props": prop_count or 0,
                "average_ev": round(float(avg_ev), 4) if avg_ev else 0.0,
            }

        if db:
            return await _fetch_metrics(db)
        else:
            async with AsyncSessionLocal() as session:
                return await _fetch_metrics(session)
                
    except Exception as e:
        logger.error(f"dashboard metrics error: {e}")
        return {"total_ev_signals": 0, "total_props": 0, "average_ev": 0.0}
