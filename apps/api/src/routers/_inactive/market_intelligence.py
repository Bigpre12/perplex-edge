class AsyncSession: pass
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, col
from typing import List, Optional
from datetime import datetime, timezone
from models.sql_models import Game, Prop, Edge, Pick
from db_sqlmodel import get_sqlmodel_session
from api_utils.auth_supabase import get_current_user_supabase

router = APIRouter(prefix="/api", tags=["Market Intelligence"])

@router.get("/live/games", response_model=List[Game])
async def get_live_games(
    sport: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_sqlmodel_session)
):
    """
    Fetch live and upcoming games from the database.
    """
    stmt = select(Game).where(Game.commence_time > datetime.now(timezone.utc))
    if sport:
        stmt = stmt.where(Game.sport == sport)
    
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/edges/top")
async def get_top_edges(
    min_ev: float = Query(2.0),
    min_hit_rate: float = Query(55.0),
    limit: int = Query(10),
    session: AsyncSession = Depends(get_sqlmodel_session)
):
    """
    Fetch the highest EV edges currently available.
    """
    stmt = (
        select(Edge, Prop, Game)
        .join(Prop, Edge.prop_id == Prop.id)
        .join(Game, Prop.game_id == Game.id)
        .where(Edge.ev >= min_ev)
        .where(Edge.hit_rate >= min_hit_rate)
        .order_by(Edge.ev.desc())
        .limit(limit)
    )
    
    result = await session.execute(stmt)
    rows = result.all()
    
    # Format response to nest child objects properly
    formatted = []
    for edge, prop, game in rows:
        formatted.append({
            "id": edge.id,
            "ev": edge.ev,
            "hit_rate": edge.hit_rate,
            "prop": {
                **prop.model_dump(),
                "game": game.model_dump()
            }
        })
    return formatted

@router.get("/picks", response_model=List[Pick])
async def get_user_picks(
    user: dict = Depends(get_current_user_supabase),
    session: AsyncSession = Depends(get_sqlmodel_session)
):
    """
    Retrieve the current user's picks and track record.
    """
    stmt = select(Pick).where(Pick.user_id == user.id).order_by(Pick.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()
