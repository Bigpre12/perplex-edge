"""Public API endpoints for the betting analytics cheat sheet UI."""

from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from app.core.database import get_db
from app.models import Sport, Team, Game, Market, Player, ModelPick, Line
from app.schemas.public import (
    PublicSport,
    PublicSportList,
    PublicGame,
    PublicGameList,
    PublicMarket,
    PublicMarketList,
    PlayerPropPick,
    PlayerPropPickList,
    GameLinePick,
    GameLinePickList,
)

router = APIRouter()


# =============================================================================
# Sports Endpoints
# =============================================================================

@router.get("/sports", response_model=PublicSportList, tags=["public"])
async def list_sports(
    db: AsyncSession = Depends(get_db),
):
    """
    List all available sports and leagues.
    
    Returns sports like NBA, NFL, MLB with their league codes.
    """
    result = await db.execute(
        select(Sport).order_by(Sport.name)
    )
    sports = result.scalars().all()
    
    return PublicSportList(
        items=[PublicSport.model_validate(s) for s in sports],
        total=len(sports),
    )


# =============================================================================
# Games Endpoints
# =============================================================================

@router.get("/sports/{sport_id}/games/today", response_model=PublicGameList, tags=["public"])
async def list_games_today(
    sport_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    List today's games for a sport.
    
    Returns games with home/away team names and start times.
    """
    # Verify sport exists
    sport = await db.get(Sport, sport_id)
    if not sport:
        raise HTTPException(status_code=404, detail=f"Sport {sport_id} not found")
    
    # Calculate today's date range
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    # Alias for home and away teams
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)
    
    result = await db.execute(
        select(Game, HomeTeam, AwayTeam)
        .join(HomeTeam, Game.home_team_id == HomeTeam.id)
        .join(AwayTeam, Game.away_team_id == AwayTeam.id)
        .where(
            and_(
                Game.sport_id == sport_id,
                Game.start_time >= today,
                Game.start_time < tomorrow,
            )
        )
        .order_by(Game.start_time)
    )
    
    games = []
    for game, home_team, away_team in result.all():
        games.append(PublicGame(
            id=game.id,
            external_game_id=game.external_game_id,
            home_team=home_team.name,
            home_team_abbr=home_team.abbreviation,
            away_team=away_team.name,
            away_team_abbr=away_team.abbreviation,
            start_time=game.start_time,
            status=game.status,
        ))
    
    return PublicGameList(items=games, total=len(games))


# =============================================================================
# Markets Endpoints
# =============================================================================

@router.get("/sports/{sport_id}/markets", response_model=PublicMarketList, tags=["public"])
async def list_markets(
    sport_id: int,
    market_type: Optional[str] = Query(None, description="Filter by market type (spread, total, moneyline, player_prop)"),
    db: AsyncSession = Depends(get_db),
):
    """
    List available market types and stat types for a sport.
    
    Returns markets like spread, total, moneyline, and player props with stat types.
    """
    # Verify sport exists
    sport = await db.get(Sport, sport_id)
    if not sport:
        raise HTTPException(status_code=404, detail=f"Sport {sport_id} not found")
    
    query = select(Market).where(Market.sport_id == sport_id)
    
    if market_type:
        query = query.where(Market.market_type == market_type)
    
    query = query.order_by(Market.market_type, Market.stat_type)
    
    result = await db.execute(query)
    markets = result.scalars().all()
    
    return PublicMarketList(
        items=[PublicMarket.model_validate(m) for m in markets],
        total=len(markets),
    )


# =============================================================================
# Player Prop Picks Endpoints
# =============================================================================

@router.get("/sports/{sport_id}/picks/player-props", response_model=PlayerPropPickList, tags=["public"])
async def list_player_prop_picks(
    sport_id: int,
    stat_type: Optional[str] = Query(None, description="Filter by stat type (PTS, REB, AST, 3PM, PRA, etc.)"),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="Minimum confidence score (0-1)"),
    min_ev: float = Query(0.0, description="Minimum expected value (e.g., 0.03 for 3%)"),
    game_id: Optional[int] = Query(None, description="Filter by specific game"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get player prop picks for today's games.
    
    Returns picks with model probabilities, hit rates, and EV calculations.
    Filter by stat type (PTS, REB, AST, etc.), minimum confidence, and minimum EV.
    
    Response includes:
    - Player name and team
    - Stat type and line
    - Model probability vs implied probability
    - Expected value and confidence score
    - Hit rates over last 10 games and 30 days
    """
    # Verify sport exists
    sport = await db.get(Sport, sport_id)
    if not sport:
        raise HTTPException(status_code=404, detail=f"Sport {sport_id} not found")
    
    # Calculate today's date range
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    # Aliases for team joins
    PlayerTeam = aliased(Team)
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)
    
    # Build query with all necessary joins
    query = (
        select(ModelPick, Player, PlayerTeam, Game, HomeTeam, AwayTeam, Market)
        .join(Player, ModelPick.player_id == Player.id)
        .join(PlayerTeam, Player.team_id == PlayerTeam.id)
        .join(Game, ModelPick.game_id == Game.id)
        .join(HomeTeam, Game.home_team_id == HomeTeam.id)
        .join(AwayTeam, Game.away_team_id == AwayTeam.id)
        .join(Market, ModelPick.market_id == Market.id)
        .where(
            and_(
                ModelPick.sport_id == sport_id,
                ModelPick.is_active == True,
                ModelPick.player_id.isnot(None),
                Market.market_type == "player_prop",
                Game.start_time >= today,
                Game.start_time < tomorrow,
            )
        )
    )
    
    # Apply filters
    if stat_type:
        query = query.where(Market.stat_type == stat_type.upper())
    
    if min_confidence > 0:
        query = query.where(ModelPick.confidence_score >= min_confidence)
    
    if min_ev > 0:
        query = query.where(ModelPick.expected_value >= min_ev)
    
    if game_id:
        query = query.where(ModelPick.game_id == game_id)
    
    # Order by EV descending (best picks first)
    query = query.order_by(ModelPick.expected_value.desc())
    
    # Get total count before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    
    # Build response
    picks = []
    for row in result.all():
        pick, player, player_team, game, home_team, away_team, market = row
        
        # Determine opponent team
        if player_team.id == home_team.id:
            opponent_team = away_team.name
            opponent_abbr = away_team.abbreviation
        else:
            opponent_team = home_team.name
            opponent_abbr = home_team.abbreviation
        
        picks.append(PlayerPropPick(
            pick_id=pick.id,
            player_name=player.name,
            player_id=player.id,
            team=player_team.name,
            team_abbr=player_team.abbreviation,
            opponent_team=opponent_team,
            opponent_abbr=opponent_abbr,
            stat_type=market.stat_type or "",
            line=pick.line_value or 0.0,
            side=pick.side,
            odds=int(pick.odds),
            model_probability=pick.model_probability,
            implied_probability=pick.implied_probability,
            expected_value=pick.expected_value,
            hit_rate_30d=pick.hit_rate_30d,
            hit_rate_10g=pick.hit_rate_10g,
            confidence_score=pick.confidence_score,
            game_id=game.id,
            game_start_time=game.start_time,
        ))
    
    return PlayerPropPickList(
        items=picks,
        total=total,
        filters={
            "sport_id": sport_id,
            "stat_type": stat_type,
            "min_confidence": min_confidence,
            "min_ev": min_ev,
            "game_id": game_id,
        },
    )


# =============================================================================
# Game Line Picks Endpoints
# =============================================================================

@router.get("/sports/{sport_id}/picks/game-lines", response_model=GameLinePickList, tags=["public"])
async def list_game_line_picks(
    sport_id: int,
    market_type: Optional[str] = Query(None, description="Filter by market type (spread, total, moneyline)"),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="Minimum confidence score (0-1)"),
    min_ev: float = Query(0.0, description="Minimum expected value (e.g., 0.03 for 3%)"),
    game_id: Optional[int] = Query(None, description="Filter by specific game"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get game line picks (spread, total, moneyline) for today's games.
    
    Returns picks with model probabilities and EV calculations.
    Filter by market type, minimum confidence, and minimum EV.
    
    Response includes:
    - Home and away teams
    - Market type (spread/total/moneyline) and line
    - Model probability vs implied probability
    - Expected value and confidence score
    """
    # Verify sport exists
    sport = await db.get(Sport, sport_id)
    if not sport:
        raise HTTPException(status_code=404, detail=f"Sport {sport_id} not found")
    
    # Calculate today's date range
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    # Aliases for team joins
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)
    
    # Game line market types
    game_line_types = ["spread", "total", "moneyline"]
    
    # Build query with all necessary joins
    query = (
        select(ModelPick, Game, HomeTeam, AwayTeam, Market)
        .join(Game, ModelPick.game_id == Game.id)
        .join(HomeTeam, Game.home_team_id == HomeTeam.id)
        .join(AwayTeam, Game.away_team_id == AwayTeam.id)
        .join(Market, ModelPick.market_id == Market.id)
        .where(
            and_(
                ModelPick.sport_id == sport_id,
                ModelPick.is_active == True,
                ModelPick.player_id.is_(None),  # Game lines only (no player)
                Market.market_type.in_(game_line_types),
                Game.start_time >= today,
                Game.start_time < tomorrow,
            )
        )
    )
    
    # Apply filters
    if market_type:
        if market_type.lower() not in game_line_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid market_type. Must be one of: {game_line_types}",
            )
        query = query.where(Market.market_type == market_type.lower())
    
    if min_confidence > 0:
        query = query.where(ModelPick.confidence_score >= min_confidence)
    
    if min_ev > 0:
        query = query.where(ModelPick.expected_value >= min_ev)
    
    if game_id:
        query = query.where(ModelPick.game_id == game_id)
    
    # Order by EV descending (best picks first)
    query = query.order_by(ModelPick.expected_value.desc())
    
    # Get total count before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    
    # Build response
    picks = []
    for row in result.all():
        pick, game, home_team, away_team, market = row
        
        picks.append(GameLinePick(
            pick_id=pick.id,
            game_id=game.id,
            home_team=home_team.name,
            home_team_abbr=home_team.abbreviation,
            away_team=away_team.name,
            away_team_abbr=away_team.abbreviation,
            game_start_time=game.start_time,
            market_type=market.market_type,
            line=pick.line_value,
            side=pick.side,
            odds=int(pick.odds),
            model_probability=pick.model_probability,
            implied_probability=pick.implied_probability,
            expected_value=pick.expected_value,
            confidence_score=pick.confidence_score,
        ))
    
    return GameLinePickList(
        items=picks,
        total=total,
        filters={
            "sport_id": sport_id,
            "market_type": market_type,
            "min_confidence": min_confidence,
            "min_ev": min_ev,
            "game_id": game_id,
        },
    )
