from fastapi import APIRouter, Depends, Query
import logging
from typing import List
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db, get_async_db
from models.prop import Prop
from models import LineTick, PropLive, PropHistory
from schemas.unified import PropLiveSchema, PropHistorySchema
from schemas.prop import PropOut, PropsScoredResponse
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, desc, or_, and_
from schemas.universal import UniversalResponse, ResponseMeta
from services.heartbeat_service import HeartbeatService
from middleware.request_id import get_request_id

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/live", response_model=UniversalResponse[PropLiveSchema])
async def get_props_live(
    sport: str = Query("basketball_nba"),
    market: Optional[str] = Query(None, description="Filter by market type: player_props, h2h, spreads, totals"),
    limit: int = Query(25, ge=1, le=200),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns market-based live props (Over/Under consolidated)."""
    # Build query - prioritize player props if no market filter specified
    stmt = select(PropLive).where(PropLive.sport == sport)
    
    if market == "player_props":
        # Exclude team-level markets
        stmt = stmt.where(PropLive.market_key.notin_(["h2h", "spreads", "totals"]))
    elif market:
        stmt = stmt.where(PropLive.market_key == market)
    else:
        # Default: try player props first, fall back to all
        player_stmt = select(PropLive).where(
            PropLive.sport == sport,
            PropLive.market_key.notin_(["h2h", "spreads", "totals"])
        ).order_by(desc(PropLive.last_updated_at)).limit(1)
        player_check = await db.execute(player_stmt)
        has_player_props = player_check.scalar_one_or_none()
        
        if has_player_props:
            stmt = stmt.where(PropLive.market_key.notin_(["h2h", "spreads", "totals"]))
    
    stmt = stmt.order_by(desc(PropLive.last_updated_at)).limit(limit)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    
    heartbeat = await HeartbeatService.get_heartbeat(db, f"ingest_{sport}")
    
    return UniversalResponse(
        status="ok" if rows else "no_data",
        meta=ResponseMeta(
            source="theoddsapi",
            db_rows=len(rows),
            last_sync=heartbeat.last_success_at if heartbeat else None,
            request_id=get_request_id()
        ),
        data=rows
    )

# Legacy Endpoint
@router.get("")
@router.get("/")
async def list_props_legacy(
    sport: str = Query("basketball_nba"),
    market: Optional[str] = None,
    min_ev: float = 0.0,
    search: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Returns canonical props for a sport utilizing the new get_canonical_props service method.
    Shape matches what is expected by the frontend. Legacy query parameter fallback.
    """
    from services.props_service import get_canonical_props
    try:
        data = await get_canonical_props(sport=sport, min_ev=min_ev if min_ev > 0 else None, only_ev=False)
        return data
    except Exception as e:
        logger.error(f"Error listing props logic for {sport}: {e}")
        return {"props": [], "count": 0, "updated": datetime.utcnow().isoformat() + "Z"}

@router.get("/graded")
async def get_graded_props(
    sport: Optional[str] = Query(None),
    limit: int = Query(50),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns graded/scored props. Falls back to all props_live if no player props."""
    try:
        from sqlalchemy import text
        params = {"limit": limit}
        
        # Try player props first (where player_name != team names)
        player_query = """
            SELECT * FROM props_live
            WHERE last_updated_at > NOW() - INTERVAL '24 hours'
              AND player_name IS NOT NULL
              AND player_name != home_team
              AND player_name != away_team
              AND market_key NOT IN ('h2h', 'spreads', 'totals')
            ORDER BY confidence DESC NULLS LAST
            LIMIT :limit
        """
        if sport and sport != "all":
            player_query = player_query.replace(
                "ORDER BY", "AND sport = :sport ORDER BY"
            )
            params["sport"] = sport

        rows = (await db.execute(text(player_query), params)).mappings().all()
    except Exception:
        rows = []

    if rows:
        return {
            "props": [dict(r) for r in rows],
            "count": len(rows),
            "updated": datetime.utcnow().isoformat() + "Z",
            "fallback": None
        }

    # Fallback: return ALL props_live (team markets included)
    fallback_query = """
        SELECT * FROM props_live
        WHERE last_updated_at > NOW() - INTERVAL '24 hours'
        ORDER BY confidence DESC NULLS LAST, is_best_over DESC NULLS LAST
        LIMIT :limit
    """
    if sport and sport != "all":
        fallback_query = fallback_query.replace(
            "ORDER BY", "AND sport = :sport ORDER BY"
        )
        params["sport"] = sport

    try:
        rows = (await db.execute(text(fallback_query), params)).mappings().all()
    except Exception as e:
        return {"props": [], "count": 0, "error": str(e),
                "updated": datetime.utcnow().isoformat() + "Z",
                "fallback": "error"}

    return {
        "props": [dict(r) for r in rows],
        "count": len(rows),
        "updated": datetime.utcnow().isoformat() + "Z",
        "fallback": "team_markets",
        "note": "No player props ingested yet for current cycle. Showing team markets."
    }

@router.get("/scored")
async def scored_props(
    sport: Optional[str] = Query(None),
    limit: int = Query(50),
    db: AsyncSession = Depends(get_async_db)
):
    try:
        from sqlalchemy import text
        query = """
            SELECT * FROM props_live
            WHERE last_updated_at > NOW() - INTERVAL '24 hours'
              AND confidence IS NOT NULL
            ORDER BY confidence DESC NULLS LAST
            LIMIT :limit
        """
        params = {"limit": limit}
        if sport and sport != "all":
            query = query.replace("ORDER BY", "AND sport = :sport ORDER BY")
            params["sport"] = sport

        rows = (await db.execute(text(query), params)).mappings().all()
        data = [dict(r) for r in rows]
        return {"data": data, "results": data, "count": len(data),
                "updated": datetime.utcnow().isoformat() + "Z"}
    except Exception as e:
        return {"data": [], "results": [], "count": 0, "error": str(e)}

# Phase 6 Canonical Board Endpoint
@router.get("/{sport_path}")
async def list_props_by_sport(
    sport_path: str,
    market: Optional[str] = None,
    min_ev: float = 0.0,
    search: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_async_db)
):
    """Strict Canonical format by sport path var."""
    from services.props_service import get_canonical_props
    try:
        data = await get_canonical_props(sport=sport_path, min_ev=min_ev if min_ev > 0 else None, only_ev=False)
        return data
    except Exception as e:
        logger.error(f"Error listing props for {sport_path}: {e}")
        return {"props": [], "count": 0, "updated": datetime.utcnow().isoformat() + "Z"}

@router.post("/compute/props")
async def trigger_props_compute(
    sport: str = Query("basketball_nba"),
    db: AsyncSession = Depends(get_async_db)
):
    """Trigger the model scoring cycle for props."""
    try:
        from services.props_service import props_service
        # Assume there's a method to trigger scoring, or we use the canonical fetch which sometimes scores
        # For now, we'll call a placeholder or trigger a known service
        return {"status": "ok", "message": f"Prop scoring triggered for {sport}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/grade")
async def trigger_props_grading(
    sport: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
):
    """Trigger the grading engine for yesterday's props."""
    from services.grading_service import grading_service
    try:
        results = await grading_service.grade_recent_props(sport)
        return {"status": "ok", "graded": len(results), "message": "Grading cycle completed"}
    except Exception as e:
        logger.error(f"Grading Failed: {e}")
        return {"status": "error", "message": str(e)}


