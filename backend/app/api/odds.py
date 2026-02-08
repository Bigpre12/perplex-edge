"""Odds/Lines API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Line, Game, Market, Sport
from app.schemas.line import LineList, LineRead, LineComparison, BookmakerLine

router = APIRouter()

@router.get("", response_model=LineList)
async def list_lines(
    game_id: Optional[int] = Query(None, description="Filter by game"),
    market_type: Optional[str] = Query(None, description="Filter by market type"),
    sportsbook: Optional[str] = Query(None, description="Filter by sportsbook"),
    current_only: bool = Query(True, description="Only show current lines"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    """List betting lines with optional filters."""
    query = select(Line).options(selectinload(Line.market))

    if game_id:
        query = query.where(Line.game_id == game_id)
    
    if market_type:
        query = query.join(Market).where(Market.market_type == market_type)
    
    if sportsbook:
        query = query.where(Line.sportsbook == sportsbook)
    
    if current_only:
        query = query.where(Line.is_current == True)

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

@router.get("/compare/{game_id}", response_model=list[LineComparison])
async def compare_lines(
    game_id: int,
    market_type: Optional[str] = Query(None, description="Filter by market type"),
    db: AsyncSession = Depends(get_db),
):
    """Compare current lines across sportsbooks for a game."""
    query = (
        select(Line)
        .options(selectinload(Line.market), selectinload(Line.player))
        .where(Line.game_id == game_id, Line.is_current == True)
    )

    if market_type:
        query = query.join(Market).where(Market.market_type == market_type)

    result = await db.execute(query.limit(1000))
    lines = result.scalars().all()

    if not lines:
        raise HTTPException(status_code=404, detail="No lines found for this game")

    # Group lines by market/side/player
    grouped: dict[tuple, list[Line]] = {}
    for line in lines:
        market = line.market
        key = (
            market.market_type if market else "unknown",
            market.stat_type if market else None,
            line.side,
            line.player_id,
        )
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(line)

    # Build comparison results
    comparisons = []
    for (mkt_type, stat_type, side, player_id), group in grouped.items():
        bookmaker_lines = [
            BookmakerLine(
                sportsbook=line.sportsbook,
                odds=line.odds,
                line_value=line.line_value,
            )
            for line in group
        ]

        # Find best odds (highest for positive, closest to 0 for negative)
        best = max(group, key=lambda x: x.odds)
        
        # Calculate consensus line if applicable
        line_values = [l.line_value for l in group if l.line_value is not None]
        consensus = sum(line_values) / len(line_values) if line_values else None

        # Get player name if it's a prop
        player_name = None
        if player_id and group[0].player:
            player_name = group[0].player.name

        comparisons.append(LineComparison(
            game_id=game_id,
            market_type=mkt_type,
            side=side,
            stat_type=stat_type,
            player_name=player_name,
            lines=bookmaker_lines,
            best_odds=best.odds,
            best_sportsbook=best.sportsbook,
            consensus_line=consensus,
        ))

    return comparisons

@router.get("/best", response_model=list[LineComparison])
async def get_best_lines(
    sport: Optional[str] = Query(None, description="Filter by sport"),
    market_type: Optional[str] = Query("moneyline", description="Market type"),
    limit: int = Query(20, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get best available lines across all games."""
    # Get today's games using Eastern time (consistent with other endpoints)
    from datetime import datetime, timedelta, timezone
    from zoneinfo import ZoneInfo
    EASTERN_TZ = ZoneInfo("America/New_York")
    
    now_et = datetime.now(EASTERN_TZ)
    today_start_et = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start_et = today_start_et + timedelta(days=1)
    
    # Convert to UTC naive for PostgreSQL
    today = today_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    tomorrow = tomorrow_start_et.astimezone(timezone.utc).replace(tzinfo=None)

    query = (
        select(Line)
        .options(
            selectinload(Line.market),
            selectinload(Line.game),
        )
        .join(Game)
        .join(Market)
        .where(
            Line.is_current == True,
            Game.start_time >= today,
            Game.start_time < tomorrow,
            Market.market_type == market_type,
        )
    )

    if sport:
        query = query.join(Sport).where(Sport.league_code.ilike(f"%{sport}%"))

    result = await db.execute(query.limit(1000))
    lines = result.scalars().all()

    # Group by game and find best
    game_lines: dict[int, list[Line]] = {}
    for line in lines:
        if line.game_id not in game_lines:
            game_lines[line.game_id] = []
        game_lines[line.game_id].append(line)

    # Build comparison for each game
    comparisons = []
    for game_id, group in list(game_lines.items())[:limit]:
        # Group by side
        by_side: dict[str, list[Line]] = {}
        for line in group:
            if line.side not in by_side:
                by_side[line.side] = []
            by_side[line.side].append(line)

        for side, side_lines in by_side.items():
            bookmaker_lines = [
                BookmakerLine(
                    sportsbook=l.sportsbook,
                    odds=l.odds,
                    line_value=l.line_value,
                )
                for l in side_lines
            ]

            best = max(side_lines, key=lambda x: x.odds)

            comparisons.append(LineComparison(
                game_id=game_id,
                market_type=market_type,
                side=side,
                lines=bookmaker_lines,
                best_odds=best.odds,
                best_sportsbook=best.sportsbook,
                consensus_line=None,
            ))

    return comparisons
