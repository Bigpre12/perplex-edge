from fastapi import APIRouter, Query, Depends
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from db.session import get_async_db
from routers.schemas.ev import EvEdge
from services.db import db

router = APIRouter()

@router.get("/ev-top", response_model=List[EvEdge])
async def get_ev_top(
    sport: str = Query("basketball_nba", description="sport key, e.g. 'basketball_nba'"),
    limit: int = Query(10, ge=1, le=100),
    min_edge: float = Query(0.0, description="minimum edge pct"),
) -> List[EvEdge]:
    """
    Return latest EV edges for each unique prop (game+player+market+book+side),
    sorted by edge_pct descending.
    """
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

    return [EvEdge(**dict(r)) for r in rows]

@router.get("/ev-history", response_model=Dict[str, Any])
async def get_ev_history(
    sport: str = Query("basketball_nba"),
    event_id: Optional[str] = None,
    limit: int = Query(100),
    db: AsyncSession = Depends(get_async_db)
):
    """Returns historical EV signals for trend analysis using EdgeEVHistory."""
    stmt = select(EdgeEVHistory).where(EdgeEVHistory.sport == sport)
    if event_id:
        stmt = stmt.where(EdgeEVHistory.game_id == event_id)
    
    stmt = stmt.order_by(desc(EdgeEVHistory.snapshot_at)).limit(limit)
    result = await db.execute(stmt)
    history = result.scalars().all()
    
    return {
        "status": "success",
        "data": [EvEdgeSchema.model_validate(h) for h in history]
    }
