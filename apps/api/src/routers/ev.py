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

# Legacy EV Endpoints
@router.get("/ev-top")
@router.get("")
@router.get("/")
async def get_ev_signals_legacy(
    sport: str = Query("all", description="e.g. basketball_nba or all"),
    min_ev: float = Query(0.0, description="Minimum edge percentage"),
    limit: int = Query(50, description="Max results")
):
    """Legacy endpoint supporting query params."""
    from services.props_service import get_canonical_props
    from datetime import datetime
    try:
        data = await get_canonical_props(sport=sport, min_ev=min_ev if min_ev > 0 else None, only_ev=True)
        return data
    except Exception as e:
        logger.error(f"EV Router: Error fetching logic for {sport}: {e}")
        return {"props": [], "count": 0, "updated": datetime.utcnow().isoformat() + "Z"}

# Phase 6 Canonical Board Endpoint
@router.get("/{sport_path}")
async def get_ev_signals_by_sport(
    sport_path: str,
    min_ev: float = Query(0.0, description="Minimum edge percentage"),
    limit: int = Query(50, description="Max results")
):
    """Strict Canonical format by sport path var."""
    from services.props_service import get_canonical_props
    from datetime import datetime
    try:
        data = await get_canonical_props(sport=sport_path, min_ev=min_ev if min_ev > 0 else None, only_ev=True)
        return data
    except Exception as e:
        logger.error(f"EV Router: Error fetching for {sport_path}: {e}")
        return {"props": [], "count": 0, "updated": datetime.utcnow().isoformat() + "Z"}

# Alias for use by intel.py
get_top_ev = get_ev_signals_legacy
