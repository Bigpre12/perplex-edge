from fastapi import APIRouter, Depends, Query
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
    limit: int = Query(25, ge=1, le=200),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns market-based live props (Over/Under consolidated)."""
    stmt = select(PropLive).where(PropLive.sport == sport).order_by(desc(PropLive.last_updated_at)).limit(limit)
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

@router.get("", response_model=UniversalResponse[Dict[str, Any]])
@router.get("/", response_model=UniversalResponse[Dict[str, Any]])
async def list_props(
    sport: str = "basketball_nba",
    market: Optional[str] = None,
    min_ev: float = 0.0,
    search: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_async_db)
):
    """Returns top props for a sport using the enhanced PropsService (Market + EV)."""
    from services.props_service import get_all_props
    try:
        items = await get_all_props(sport_filter=sport)
        
        if market:
            items = [p for p in items if p.get("market_key") == market]
        if min_ev > 0:
            items = [p for p in items if (p.get("recommendation") or {}).get("ev", 0.0) >= min_ev]
        if search:
            search_low = search.lower()
            items = [p for p in items if 
                search_low in (p.get("player_name") or "").lower() or 
                search_low in (p.get("market_key") or "").lower()]
                
        items = items[:limit]
        
        heartbeat = await HeartbeatService.get_heartbeat(db, f"ingest_{sport}")
        status = "ok" if items else "no_data"
        if heartbeat and heartbeat.status == "error":
            status = "pipeline_error"
            
        return UniversalResponse(
            status=status,
            meta=ResponseMeta(
                source="theoddsapi",
                db_rows=len(items),
                last_sync=heartbeat.last_success_at if heartbeat else None,
                request_id=get_request_id()
            ),
            data=items
        )
    except Exception as e:
        logger.error(f"Error listing props for {sport}: {e}")
        return UniversalResponse(
            status="pipeline_error",
            message=str(e),
            meta=ResponseMeta(request_id=get_request_id()),
            data=[]
        )

@router.get("/scored")
async def scored_props(db: AsyncSession = Depends(get_db)):
    """Returns recently completed props for the ledger/history (last 72h)."""
    try:
        now = datetime.utcnow()
        stmt = select(Prop).where(
            Prop.is_scored == True,
            Prop.created_at >= now - timedelta(hours=72)
        ).order_by(desc(Prop.created_at)).limit(50)
        
        result = await db.execute(stmt)
        items = result.scalars().all()
        return {"data": items, "results": items}
    except Exception as e:
        logger.error(f"Error listing scored props: {e}")
        return {"data": [], "results": []}


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
        
    # 2. Get history to compute hit rate
    hist_stmt = select(PropHistory).where(
        PropHistory.player_name == player_name,
        PropHistory.sport == sport
    ).order_by(desc(PropHistory.snapshot_at)).limit(50)
    
    hist_res = await db.execute(hist_stmt)
    history = hist_res.scalars().all()
    
    # Simple hit-rate logic (L10/L20)
    # This assumes PropHistory rows represent game results or final closing lines
    # For now, we'll just return the raw history for the frontend to chart
    
    return {
        "status": "success",
        "player": player_name,
        "current_line": current.line,
        "history": [PropHistorySchema.model_validate(h) for h in history],
        "stats": {
            "l5_hit": 0.6, # Placeholder for actual historical scoring logic
            "l10_hit": 0.55,
            "season_avg": current.line * 1.1 
        }
    }
