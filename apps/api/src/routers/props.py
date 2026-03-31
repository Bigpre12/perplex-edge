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


@router.get("/hero/{player_name}")
async def get_prop_hero(
    player_name: str,
    sport: str = Query("basketball_nba"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Returns 'Hero' view data for a specific player:
    - Current live lines
    - Historical hit rate vs current line
    """
    # 1. Get current live line
    stmt = select(PropLive).where(
        PropLive.player_name == player_name,
        PropLive.sport == sport
    ).order_by(desc(PropLive.last_updated_at)).limit(1)
    
    res = await db.execute(stmt)
    current = res.scalar_one_or_none()
    
    if not current:
        return {"status": "not_found", "message": "No live line found for player"}
        
    # 2. Get history and calculate real stats from settled PropLine results
    from models.prop import PropLine
    
    stat_display = current.market_key.replace("player_", "").replace("_", " ").title() if current.market_key else "Points"
    
    # Query settled results for this player and stat type
    settled_stmt = select(PropLine).where(
        PropLine.player_name == player_name,
        PropLine.sport_key == sport,
        PropLine.stat_type == stat_display,
        PropLine.is_settled == True
    ).order_by(desc(PropLine.start_time)).limit(20)
    
    settled_res = await db.execute(settled_stmt)
    settled_list = settled_res.scalars().all()
    
    l5_hits = [s.hit for s in settled_list[:5] if s.hit is not None]
    l10_hits = [s.hit for s in settled_list[:10] if s.hit is not None]
    
    l5_rate = sum(l5_hits) / len(l5_hits) if l5_hits else 0.0
    l10_rate = sum(l10_hits) / len(l10_hits) if l10_hits else 0.0
    
    # Season Avg based on actual recorded values
    actuals = [s.actual_value for s in settled_list if s.actual_value is not None]
    avg_val = sum(actuals) / len(actuals) if actuals else (current.line or 0.0)

    return {
        "status": "success",
        "player": player_name,
        "current_line": current.line,
        "history": [PropHistorySchema.model_validate(h) for h in history],
        "stats": {
            "l5_hit": round(l5_rate, 2),
            "l10_hit": round(l10_rate, 2),
            "season_avg": round(avg_val, 2)
        }
    }
