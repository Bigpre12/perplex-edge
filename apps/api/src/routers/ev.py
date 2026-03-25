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
    limit: int = Query(500, description="Max results"),
    db: AsyncSession = Depends(get_async_db)
):
    """Legacy endpoint supporting query params."""
    from datetime import datetime
    from sqlalchemy import text
    try:
        # Try ev_signals table first
        ev_query = "SELECT * FROM ev_signals WHERE edge_percent >= :min_ev"
        params = {"min_ev": min_ev, "limit": limit}

        if sport and sport != "all":
            ev_query += " AND sport = :sport"
            params["sport"] = sport
            
        ev_query += " ORDER BY edge_percent DESC LIMIT :limit"
        
        result = await db.execute(text(ev_query), params)
        rows = result.mappings().all()
        
        if rows:
            return {"props": [dict(r) for r in rows], "count": len(rows), 
                    "updated": datetime.utcnow().isoformat() + "Z", "fallback": None}
                    
        # Fallback: compute EV on the fly from props_live
        live_query = """
            SELECT *, 
                   ROUND((CAST(1 AS NUMERIC)/NULLIF(implied_over,0) - implied_over) * 100, 2) as ev_percentage
            FROM props_live
            WHERE last_updated_at > NOW() - INTERVAL '24 hours'
              AND implied_over > 0
              AND implied_over < 1
        """
        
        if sport and sport != "all":
            live_query += " AND sport = :sport"
            
        live_query += " ORDER BY ev_percentage DESC NULLS LAST LIMIT :limit"
        
        result_live = await db.execute(text(live_query), params)
        live_rows = result_live.mappings().all()
        
        return {
            "props": [dict(r) for r in live_rows],
            "count": len(live_rows),
            "updated": datetime.utcnow().isoformat() + "Z",
            "fallback": "computed_live"
        }
    except Exception as e:
        logger.error(f"EV Router: Error fetching logic for {sport}: {e}", exc_info=True)
        return {"props": [], "count": 0, "updated": datetime.utcnow().isoformat() + "Z"}

# Phase 6 Canonical Board Endpoint
@router.get("/{sport_path}")
async def get_ev_signals_by_sport(
    sport_path: str,
    min_ev: float = Query(0.0, description="Minimum edge percentage"),
    limit: int = Query(500, description="Max results")
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
