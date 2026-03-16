# apps/api/src/routers/ev.py
import logging
from fastapi import APIRouter, Query
from sqlalchemy import select, desc
from db.session import async_session_maker
from models.unified import UnifiedEVSignal

router = APIRouter(tags=["Brain Intelligence"])
logger = logging.getLogger(__name__)

@router.get("/ev-top")
@router.get("/")
@router.get("/track")
async def track_clv(
    sport: str = Query("basketball_nba", description="e.g. basketball_nba"),
    min_ev: float = Query(2.0, description="Minimum edge percentage"),
    limit: int = Query(50, description="Max results")
):
    """
    Returns top EV signals from the pre-computed signals table.
    Strictly database-first.
    """
    try:
        async with async_session_maker() as session:
            stmt = select(UnifiedEVSignal).where(
                UnifiedEVSignal.sport == sport,
                UnifiedEVSignal.edge_percent >= min_ev
            ).order_by(desc(UnifiedEVSignal.edge_percent)).limit(limit)
            
            result = await session.execute(stmt)
            signals = result.scalars().all()
            
            return {
                "sport": sport,
                "count": len(signals),
                "data": [
                    {
                        "id": s.id,
                        "event_id": s.event_id,
                        "player_name": s.player_name,
                        "stat_type": s.market_key,
                        "side": s.outcome_key.upper(),
                        "line": float(s.line) if s.line else None,
                        "odds": int(s.price),
                        "true_prob": float(s.true_prob),
                        "ev_percentage": float(s.edge_percent),
                        "book": s.bookmaker,
                        "updated_at": s.updated_at.isoformat()
                    } for s in signals
                ]
            }
    except Exception as e:
        logger.error(f"EV Router: Error fetching for {sport}: {e}")
        return {"data": [], "error": str(e)}

# Alias for use by intel.py
get_top_ev = track_clv
