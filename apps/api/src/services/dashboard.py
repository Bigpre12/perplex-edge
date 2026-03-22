import logging
from sqlalchemy import select, func
from db.session import AsyncSessionLocal
from models.ev_signals import EvSignal

logger = logging.getLogger(__name__)

async def get_dashboard_metrics() -> dict:
    try:
        async with AsyncSessionLocal() as session:
            ev_count = await session.scalar(select(func.count()).select_from(EvSignal))
            avg_ev = await session.scalar(select(func.avg(EvSignal.edge_percent)))
            return {
                "total_ev_signals": ev_count or 0,
                "average_ev": round(float(avg_ev), 4) if avg_ev else 0.0,
            }
    except Exception as e:
        logger.error(f"dashboard metrics error: {e}")
        return {"total_ev_signals": 0, "average_ev": 0.0}
