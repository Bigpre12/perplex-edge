# apps/api/src/routers/ev.py
import logging
from fastapi import APIRouter, Query
from sqlalchemy import select, desc
from db.session import async_session_maker
from models import UnifiedEVSignal
from schemas.universal import UniversalResponse, ResponseMeta
from services.heartbeat_service import HeartbeatService
from middleware.request_id import get_request_id

router = APIRouter(tags=["Brain Intelligence"])
logger = logging.getLogger(__name__)

def _prob_to_american(prob: float) -> int:
    if prob <= 0: return 0
    if prob >= 1: return -10000
    if prob > 0.5:
        return int(-((prob / (1 - prob)) * 100))
    else:
        return int(((1 - prob) / prob) * 100)

def _calculate_kelly(price: int, prob: float) -> float:
    # Convert American odds to decimal
    if price > 0:
        b = price / 100
    else:
        b = 100 / abs(price)
    
    # Kelly Formula: f* = (bp - q) / b
    q = 1 - prob
    f_star = (b * prob - q) / b
    
    # Standard 1/4 Kelly suggested for sports
    quarter_kelly = (f_star * 0.25) * 100
    return round(max(0, quarter_kelly), 2)

@router.get("", response_model=UniversalResponse[dict])
@router.get("/")
@router.get("/ev-top", response_model=UniversalResponse[dict])
async def get_ev_signals(
    sport: str = Query("all", description="e.g. basketball_nba or all"),
    min_ev: float = Query(0.0, description="Minimum edge percentage"),
    limit: int = Query(50, description="Max results")
):
    """
    Returns top EV signals from the pre-computed signals table.
    Strictly database-driven - NO MOCK DATA.
    """
    try:
        async with async_session_maker() as session:
            stmt = select(UnifiedEVSignal).where(
                UnifiedEVSignal.edge_percent >= min_ev
            )
            
            if sport != "all":
                stmt = stmt.where(UnifiedEVSignal.sport == sport)
                
            stmt = stmt.order_by(desc(UnifiedEVSignal.edge_percent)).limit(limit)
            
            result = await session.execute(stmt)
            signals = result.scalars().all()
            
            # Use a representative heartbeat
            hb_key = f"ingest_{sport}" if sport != "all" else "ingest_basketball_nba"
            heartbeat = await HeartbeatService.get_heartbeat(session, hb_key)
            
            data = [
                {
                    "id": s.id,
                    "event_id": s.event_id,
                    "sport": s.sport,
                    "player_name": s.player_name,
                    "stat_type": s.market_key,
                    "side": s.outcome_key.upper(),
                    "line": float(s.line) if s.line else None,
                    "odds": int(s.price),
                    "true_prob": float(s.true_prob),
                    "ev_percentage": float(s.edge_percent),
                    "implied_prob": float(s.implied_prob),
                    "fair_odds": _prob_to_american(float(s.true_prob)),
                    "kelly_percentage": _calculate_kelly(int(s.price), float(s.true_prob)),
                    "book": s.bookmaker,
                    "engine_version": s.engine_version,
                    "updated_at": s.updated_at.isoformat()
                } for s in signals
            ]
            
            return UniversalResponse(
                status="ok" if signals else "no_data",
                meta=ResponseMeta(
                    source="ev_engine",
                    db_rows=len(signals),
                    last_sync=heartbeat.last_success_at if heartbeat else None,
                    request_id=get_request_id()
                ),
                data=data
            )
    except Exception as e:
        logger.error(f"EV Router: Error fetching for {sport}: {e}")
        return UniversalResponse(
            status="pipeline_error",
            message=str(e),
            meta=ResponseMeta(request_id=get_request_id()),
            data=[]
        )

# Alias for use by intel.py
get_top_ev = get_ev_signals
