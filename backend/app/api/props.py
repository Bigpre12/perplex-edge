"""Player Props API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Line, Game, Market, Player, Sport
from app.schemas.line import LineList, LineRead, LineComparison, BookmakerLine

router = APIRouter()


@router.get("", response_model=LineList)
async def list_props(
    game_id: Optional[int] = Query(None, description="Filter by game"),
    player_id: Optional[int] = Query(None, description="Filter by player"),
    stat_type: Optional[str] = Query(None, description="Filter by stat type (PTS, REB, AST)"),
    sportsbook: Optional[str] = Query(None, description="Filter by sportsbook"),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    """List player props with optional filters."""
    query = (
        select(Line)
        .options(selectinload(Line.market), selectinload(Line.player))
        .join(Market)
        .where(
            Line.is_current == True,
            Line.player_id.isnot(None),
            Market.market_type == "player_prop",
        )
    )

    if game_id:
        query = query.where(Line.game_id == game_id)
    
    if player_id:
        query = query.where(Line.player_id == player_id)
    
    if stat_type:
        query = query.where(Market.stat_type == stat_type.upper())
    
    if sportsbook:
        query = query.where(Line.sportsbook == sportsbook)

    query = query.order_by(Line.fetched_at.desc())

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Get paginated results
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    lines = result.scalars().all()

    return LineList(
        items=[LineRead.model_validate(line) for line in lines],
        total=total or 0,
    )


@router.get("/compare/{game_id}/{player_id}", response_model=list[LineComparison])
async def compare_player_props(
    game_id: int,
    player_id: int,
    stat_type: Optional[str] = Query(None, description="Filter by stat type"),
    db: AsyncSession = Depends(get_db),
):
    """Compare props for a specific player across sportsbooks."""
    query = (
        select(Line)
        .options(selectinload(Line.market), selectinload(Line.player))
        .join(Market)
        .where(
            Line.game_id == game_id,
            Line.player_id == player_id,
            Line.is_current == True,
            Market.market_type == "player_prop",
        )
    )

    if stat_type:
        query = query.where(Market.stat_type == stat_type.upper())

    result = await db.execute(query)
    lines = result.scalars().all()

    if not lines:
        raise HTTPException(status_code=404, detail="No props found for this player")

    # Get player name
    player = lines[0].player
    player_name = player.name if player else "Unknown"

    # Group by stat type and side
    grouped: dict[tuple, list[Line]] = {}
    for line in lines:
        market = line.market
        key = (market.stat_type if market else None, line.side)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(line)

    # Build comparisons
    comparisons = []
    for (stat, side), group in grouped.items():
        bookmaker_lines = [
            BookmakerLine(
                sportsbook=line.sportsbook,
                odds=line.odds,
                line_value=line.line_value,
            )
            for line in group
        ]

        best = max(group, key=lambda x: x.odds)
        
        line_values = [l.line_value for l in group if l.line_value is not None]
        consensus = sum(line_values) / len(line_values) if line_values else None

        comparisons.append(LineComparison(
            game_id=game_id,
            market_type="player_prop",
            side=side,
            stat_type=stat,
            player_name=player_name,
            lines=bookmaker_lines,
            best_odds=best.odds,
            best_sportsbook=best.sportsbook,
            consensus_line=consensus,
        ))

    return comparisons


@router.get("/players/{game_id}")
async def list_players_with_props(
    game_id: int,
    db: AsyncSession = Depends(get_db),
):
    """List all players that have props for a specific game."""
    query = (
        select(Player)
        .join(Line, Line.player_id == Player.id)
        .join(Market)
        .where(
            Line.game_id == game_id,
            Line.is_current == True,
            Market.market_type == "player_prop",
        )
        .distinct()
    )

    result = await db.execute(query)
    players = result.scalars().all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "position": p.position,
            "team_id": p.team_id,
        }
        for p in players
    ]


@router.get("/stat-types")
async def list_stat_types(
    sport: Optional[str] = Query(None, description="Filter by sport"),
    db: AsyncSession = Depends(get_db),
):
    """List available stat types for props."""
    query = (
        select(Market.stat_type)
        .where(
            Market.market_type == "player_prop",
            Market.stat_type.isnot(None),
        )
        .distinct()
    )

    if sport:
        query = query.join(Sport).where(Sport.league_code.ilike(f"%{sport}%"))

    result = await db.execute(query)
    stat_types = result.scalars().all()

    return {"stat_types": stat_types}
