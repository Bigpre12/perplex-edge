from fastapi import APIRouter, Query, Depends
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from db.session import AsyncSessionLocal, get_async_db
from models import EdgeEVHistory, Injury
from models.user import User
from services.db import db
from schemas.universal import UniversalResponse, ResponseMeta
from services.heartbeat_service import HeartbeatService
from middleware.request_id import get_request_id
from api_utils.tier_guards import require_tier

router = APIRouter(tags=["Intel Intelligence"])

@router.get("/ev-top", response_model=UniversalResponse[dict])
async def get_ev_top(
    sport: str = Query("basketball_nba", description="sport key, e.g. 'basketball_nba'"),
    limit: int = Query(10, ge=1, le=100),
    min_edge: float = Query(0.0, description="minimum edge pct"),
    current_user: User = Depends(require_tier("pro"))
):
    """
    Return latest EV edges for each unique prop (game+player+market+book+side),
    sorted by edge_pct descending.
    """
    try:
        rows = await db.fetch_all(
            """
            with latest as (
              select distinct on (game_id, player_id, market_key, book, side)
                sport, league, game_id, game_start_time,
                player_id, player_name, team,
                market_key, market_label, line,
                book, side, odds,
                model_prob, implied_prob, edge_pct,
                snapshot_at
              from public.edges_ev_history
              where sport = :sport
              order by game_id, player_id, market_key, book, side, snapshot_at desc
            )
            select *
            from latest
            where edge_pct >= :min_edge
            order by edge_pct desc
            limit :limit;
            """,
            {"sport": sport, "min_edge": min_edge, "limit": limit},
        )

        async with AsyncSessionLocal() as session:
            heartbeat = await HeartbeatService.get_heartbeat(session, f"ingest_{sport}")

        return UniversalResponse(
            status="ok" if rows else "no_data",
            meta=ResponseMeta(
                source="ev_history",
                db_rows=len(rows),
                last_sync=heartbeat.last_success_at if heartbeat else None,
                request_id=get_request_id()
            ),
            data=[dict(r) for r in rows]
        )
    except Exception as e:
        return UniversalResponse(
            status="pipeline_error",
            message=str(e),
            meta=ResponseMeta(request_id=get_request_id()),
            data=[]
        )

@router.get("/ev-history", response_model=UniversalResponse[dict])
async def get_ev_history(
    sport: str = Query("basketball_nba"),
    event_id: Optional[str] = None,
    limit: int = Query(100),
    db_session: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_tier("pro"))
):
    """Returns historical EV signals for trend analysis using EdgeEVHistory."""
    try:
        stmt = select(EdgeEVHistory).where(EdgeEVHistory.sport == sport)
        if event_id:
            stmt = stmt.where(EdgeEVHistory.game_id == event_id)
        
        stmt = stmt.order_by(desc(EdgeEVHistory.snapshot_at)).limit(limit)
        result = await db_session.execute(stmt)
        history = result.scalars().all()
        
        heartbeat = await HeartbeatService.get_heartbeat(db_session, f"ingest_{sport}")
        
        return UniversalResponse(
            status="ok" if history else "no_data",
            meta=ResponseMeta(
                source="ev_history_raw",
                db_rows=len(history),
                last_sync=heartbeat.last_success_at if heartbeat else None,
                request_id=get_request_id()
            ),
            data=[h.to_dict() if hasattr(h, "to_dict") else {c.name: getattr(h, c.name) for c in h.__table__.columns} for h in history]
        )
    except Exception as e:
        return UniversalResponse(
            status="pipeline_error",
            message=str(e),
            meta=ResponseMeta(request_id=get_request_id()),
            data=[]
        )

@router.get("/injuries", response_model=UniversalResponse[dict])
async def proxy_injuries(
    sport: str = Query("basketball_nba"),
    db_session: AsyncSession = Depends(get_async_db)
):
    """Proxy for /api/injuries/live to satisfy frontend legacy/intel calls."""
    try:
        stmt = select(Injury).filter(Injury.sport == sport).order_by(desc(Injury.created_at)).limit(50)
        result = await db_session.execute(stmt)
        rows = result.scalars().all()
        
        heartbeat = await HeartbeatService.get_heartbeat(db_session, f"ingest_{sport}_injuries")
        
        return UniversalResponse(
            status="ok" if rows else "no_data",
            meta=ResponseMeta(
                source="injury_service",
                db_rows=len(rows),
                last_sync=heartbeat.last_success_at if heartbeat else None,
                request_id=get_request_id()
            ),
            data=[r.to_dict() if hasattr(r, "to_dict") else {c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows]
        )
    except Exception as e:
        return UniversalResponse(
            status="pipeline_error",
            message=str(e),
            meta=ResponseMeta(request_id=get_request_id()),
            data=[]
        )
