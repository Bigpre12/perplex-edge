"""Injuries API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Injury, Player, Team, Sport
from app.schemas.injury import InjuryList, InjuryWithPlayer

router = APIRouter()


@router.get("", response_model=InjuryList)
async def list_injuries(
    sport: Optional[str] = Query(None, description="Filter by sport"),
    team_id: Optional[int] = Query(None, description="Filter by team"),
    status: Optional[str] = Query(None, description="Filter by status (OUT, QUESTIONABLE, etc.)"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    """List injuries with optional filters."""
    query = (
        select(Injury)
        .options(
            selectinload(Injury.player).selectinload(Player.team),
        )
        .order_by(Injury.updated_at.desc())
    )

    if sport:
        query = query.join(Sport).where(Sport.league_code.ilike(f"%{sport}%"))
    
    if team_id:
        query = query.join(Player).where(Player.team_id == team_id)
    
    if status:
        query = query.where(Injury.status == status.upper())

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Get paginated results
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    injuries = result.scalars().all()

    # Build response with player details
    items = []
    for injury in injuries:
        player = injury.player
        team = player.team if player else None
        
        items.append(InjuryWithPlayer(
            id=injury.id,
            sport_id=injury.sport_id,
            player_id=injury.player_id,
            status=injury.status,
            status_detail=injury.status_detail,
            is_starter_flag=injury.is_starter_flag,
            probability=injury.probability,
            source=injury.source,
            updated_at=injury.updated_at,
            player_name=player.name if player else "Unknown",
            team_name=team.name if team else None,
            position=player.position if player else None,
        ))

    return InjuryList(items=items, total=total or 0)


@router.get("/by-game/{game_id}", response_model=InjuryList)
async def get_injuries_by_game(
    game_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get injuries for players in a specific game."""
    from app.models import Game

    # Get game to find teams
    game_result = await db.execute(select(Game).where(Game.id == game_id))
    game = game_result.scalar_one_or_none()

    if not game:
        return InjuryList(items=[], total=0)

    # Get injuries for players on either team
    query = (
        select(Injury)
        .options(
            selectinload(Injury.player).selectinload(Player.team),
        )
        .join(Player)
        .where(Player.team_id.in_([game.home_team_id, game.away_team_id]))
        .order_by(Injury.updated_at.desc())
    )

    result = await db.execute(query)
    injuries = result.scalars().all()

    items = []
    for injury in injuries:
        player = injury.player
        team = player.team if player else None
        
        items.append(InjuryWithPlayer(
            id=injury.id,
            sport_id=injury.sport_id,
            player_id=injury.player_id,
            status=injury.status,
            status_detail=injury.status_detail,
            is_starter_flag=injury.is_starter_flag,
            probability=injury.probability,
            source=injury.source,
            updated_at=injury.updated_at,
            player_name=player.name if player else "Unknown",
            team_name=team.name if team else None,
            position=player.position if player else None,
        ))

    return InjuryList(items=items, total=len(items))


@router.get("/statuses")
async def list_injury_statuses():
    """List available injury status values."""
    return {
        "statuses": [
            {"code": "OUT", "description": "Player is out and will not play"},
            {"code": "DOUBTFUL", "description": "Player is doubtful to play (~25% chance)"},
            {"code": "QUESTIONABLE", "description": "Player is questionable (~50% chance)"},
            {"code": "PROBABLE", "description": "Player is probable to play (~75% chance)"},
            {"code": "GTD", "description": "Game-time decision"},
            {"code": "AVAILABLE", "description": "Player is available to play"},
        ]
    }
