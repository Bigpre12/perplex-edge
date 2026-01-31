"""Public API endpoints for the betting analytics cheat sheet UI."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query, HTTPException

logger = logging.getLogger(__name__)
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from app.core.database import get_db
from app.models import Sport, Team, Game, Market, Player, ModelPick, Line, Injury
from app.services.memory_cache import cache, CacheKey
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
    BookLine,
)

router = APIRouter()

# Eastern timezone (handles DST automatically)
EASTERN_TZ = ZoneInfo("America/New_York")


# =============================================================================
# Helper Functions for Per-Book Line Comparison
# =============================================================================

def calculate_ev_for_odds(model_prob: float, odds: int) -> float:
    """Calculate EV for given model probability and American odds."""
    if odds < 0:
        profit = 100 / abs(odds)
    else:
        profit = odds / 100
    
    ev = (model_prob * profit) - ((1 - model_prob) * 1)
    return round(ev, 4)


async def get_book_lines_for_pick(
    db: AsyncSession,
    game_id: int,
    player_id: int,
    market_id: int,
    side: str,
    model_prob: float,
) -> tuple[list[BookLine], str | None, float | None]:
    """
    Fetch all sportsbook lines for a specific player prop.
    
    Returns:
        tuple of (book_lines, best_book, line_variance)
    """
    # Query all current lines for this player/game/market combination
    result = await db.execute(
        select(Line).where(
            and_(
                Line.game_id == game_id,
                Line.player_id == player_id,
                Line.market_id == market_id,
                Line.side == side,
                Line.is_current == True,
            )
        )
    )
    lines = result.scalars().all()
    
    if not lines:
        return [], None, None
    
    # Build book lines with EV
    book_lines = []
    best_ev = float("-inf")
    best_book = None
    line_values = []
    
    for line in lines:
        ev = calculate_ev_for_odds(model_prob, int(line.odds))
        book_lines.append(BookLine(
            sportsbook=line.sportsbook,
            line=line.line_value,
            odds=int(line.odds),
            ev=ev,
        ))
        
        if ev > best_ev:
            best_ev = ev
            best_book = line.sportsbook
        
        if line.line_value is not None:
            line_values.append(line.line_value)
    
    # Calculate line variance (max difference from consensus)
    line_variance = None
    if len(line_values) >= 2:
        line_variance = round(max(line_values) - min(line_values), 1)
    
    return book_lines, best_book, line_variance


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
    Uses in-memory caching for fast response (1 hour TTL).
    """
    # Try cache first
    cached = await cache.get(CacheKey.SPORTS_LIST)
    if cached is not None:
        return cached
    
    # Fetch from database
    result = await db.execute(
        select(Sport).order_by(Sport.name)
    )
    sports = result.scalars().all()
    
    response = PublicSportList(
        items=[PublicSport.model_validate(s) for s in sports],
        total=len(sports),
    )
    
    # Cache for 1 hour (sports rarely change)
    await cache.set(CacheKey.SPORTS_LIST, response, ttl_seconds=3600)
    
    return response


# =============================================================================
# Games Endpoints
# =============================================================================

@router.get("/sports/{sport_id}/games/today", response_model=PublicGameList, tags=["public"])
async def list_games_today(
    sport_id: int,
    upcoming_only: bool = Query(False, description="Only show games that haven't started yet"),
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
    
    # Calculate today's date range using US Eastern time (handles DST)
    # This ensures games show for today's US schedule even after midnight UTC
    now_et = datetime.now(EASTERN_TZ)
    utc_now_naive = datetime.now(timezone.utc).replace(tzinfo=None)  # Naive UTC for DB comparison
    
    # Get today's date boundaries in Eastern time
    today_start_et = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start_et = today_start_et + timedelta(days=1)
    
    # Convert to UTC (naive datetimes for PostgreSQL)
    today = today_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    tomorrow = tomorrow_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    
    # Alias for home and away teams
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)
    
    # Build filter conditions
    conditions = [
        Game.sport_id == sport_id,
        Game.start_time >= today,
        Game.start_time < tomorrow,
    ]
    
    # Only show games that haven't started
    if upcoming_only:
        conditions.append(Game.start_time > utc_now_naive)
    
    result = await db.execute(
        select(Game, HomeTeam, AwayTeam)
        .join(HomeTeam, Game.home_team_id == HomeTeam.id)
        .join(AwayTeam, Game.away_team_id == AwayTeam.id)
        .where(and_(*conditions))
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
    fresh_only: bool = Query(True, description="Only show fresh picks (generated within 12h, games not started)"),
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
    
    # Calculate today's date range using US Eastern time (handles DST)
    now_et = datetime.now(EASTERN_TZ)
    utc_now_naive = datetime.now(timezone.utc).replace(tzinfo=None)  # Naive UTC for DB comparison
    
    # Get today's date boundaries in Eastern time
    today_start_et = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start_et = today_start_et + timedelta(days=1)
    
    # Convert to UTC (naive datetimes for PostgreSQL)
    today = today_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    tomorrow = tomorrow_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    
    # Freshness threshold - picks generated within last 24 hours
    # Increased from 12h to 24h to be more resilient to sync gaps
    freshness_cutoff = utc_now_naive - timedelta(hours=24)
    
    # Aliases for team joins
    PlayerTeam = aliased(Team)
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)
    
    # Subquery to find injured player IDs (filter them out)
    injured_subquery = (
        select(Injury.player_id)
        .where(Injury.status.in_(["OUT", "DOUBTFUL", "GTD", "DAY_TO_DAY"]))
        .scalar_subquery()
    )
    
    # Base filter conditions
    base_conditions = [
        ModelPick.sport_id == sport_id,
        # ModelPick.is_active == True,  # Disabled - show all picks regardless of active status
        ModelPick.player_id.isnot(None),
        ModelPick.player_id.notin_(injured_subquery),  # Exclude injured players
        Market.market_type == "player_prop",
        Game.start_time >= today,
        Game.start_time < tomorrow + timedelta(days=7),  # Include upcoming week
    ]
    
    # Add freshness filters if requested
    if fresh_only:
        base_conditions.extend([
            # Only games that haven't started yet
            Game.start_time > utc_now_naive,
            # Only picks generated recently
            ModelPick.generated_at >= freshness_cutoff,
        ])
    
    # Build query with all necessary joins (outerjoin for PlayerTeam since team_id can be null)
    query = (
        select(ModelPick, Player, PlayerTeam, Game, HomeTeam, AwayTeam, Market)
        .join(Player, ModelPick.player_id == Player.id)
        .outerjoin(PlayerTeam, Player.team_id == PlayerTeam.id)
        .join(Game, ModelPick.game_id == Game.id)
        .join(HomeTeam, Game.home_team_id == HomeTeam.id)
        .join(AwayTeam, Game.away_team_id == AwayTeam.id)
        .join(Market, ModelPick.market_id == Market.id)
        .where(and_(*base_conditions))
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
    skipped_count = 0
    for row in result.all():
        pick, player, player_team, game, home_team, away_team, market = row
        
        # Skip picks without valid line values (these are likely data issues)
        if pick.line_value is None or pick.line_value == 0:
            skipped_count += 1
            continue
        
        # Handle player_team being None (players without assigned team)
        if player_team is not None:
            team_name = player_team.name
            team_abbr = player_team.abbreviation
            # Determine opponent team
            if player_team.id == home_team.id:
                opponent_team = away_team.name
                opponent_abbr = away_team.abbreviation
            else:
                opponent_team = home_team.name
                opponent_abbr = home_team.abbreviation
        else:
            # Player without team - use game teams as context
            team_name = "Unknown"
            team_abbr = "UNK"
            opponent_team = f"{away_team.name} vs {home_team.name}"
            opponent_abbr = f"{away_team.abbreviation} vs {home_team.abbreviation}"
        
        # Fetch per-book lines for this prop (enables sportsbook comparison)
        book_lines, best_book, line_variance = await get_book_lines_for_pick(
            db,
            game_id=game.id,
            player_id=player.id,
            market_id=market.id,
            side=pick.side,
            model_prob=pick.model_probability,
        )
        
        # Calculate Kelly sizing for this pick
        from app.services.parlay_service import calculate_kelly_fraction
        kelly = calculate_kelly_fraction(
            win_prob=pick.model_probability,
            american_odds=int(pick.odds),
        )
        
        picks.append(PlayerPropPick(
            pick_id=pick.id,
            player_name=player.name,
            player_id=player.id,
            team=team_name,
            team_abbr=team_abbr,
            opponent_team=opponent_team,
            opponent_abbr=opponent_abbr,
            stat_type=market.stat_type or "",
            line=pick.line_value,  # Already validated non-null/non-zero above
            side=pick.side,
            odds=int(pick.odds),
            model_probability=pick.model_probability,
            implied_probability=pick.implied_probability,
            expected_value=pick.expected_value,
            hit_rate_30d=pick.hit_rate_30d,
            hit_rate_10g=pick.hit_rate_10g,
            hit_rate_5g=pick.hit_rate_5g,
            hit_rate_3g=pick.hit_rate_3g,
            confidence_score=pick.confidence_score,
            game_id=game.id,
            game_start_time=game.start_time,
            # Per-book comparison data
            book_lines=book_lines if book_lines else None,
            best_book=best_book,
            line_variance=line_variance,
            # Kelly sizing
            kelly_units=kelly["suggested_units"],
            kelly_edge_pct=kelly["edge_pct"],
            kelly_risk_level=kelly["risk_level"],
        ))
    
    # Debug logging to track filtered/skipped picks
    logger.info(
        f"[player-props] sport_id={sport_id}, fresh_only={fresh_only}: "
        f"returning {len(picks)} picks, skipped {skipped_count} with invalid line_value, total={total}"
    )
    
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
    fresh_only: bool = Query(True, description="Only show fresh picks (generated within 12h, games not started)"),
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
    
    # Calculate today's date range using US Eastern time (handles DST)
    now_et = datetime.now(EASTERN_TZ)
    utc_now_naive = datetime.now(timezone.utc).replace(tzinfo=None)  # Naive UTC for DB comparison
    
    # Get today's date boundaries in Eastern time
    today_start_et = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start_et = today_start_et + timedelta(days=1)
    
    # Convert to UTC (naive datetimes for PostgreSQL)
    today = today_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    tomorrow = tomorrow_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    
    # Freshness threshold - picks generated within last 24 hours
    # Increased from 12h to 24h to be more resilient to sync gaps
    freshness_cutoff = utc_now_naive - timedelta(hours=24)
    
    # Aliases for team joins
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)
    
    # Game line market types
    game_line_types = ["spread", "total", "moneyline"]
    
    # Base filter conditions
    base_conditions = [
        ModelPick.sport_id == sport_id,
        # ModelPick.is_active == True,  # Disabled - show all picks regardless of active status
        ModelPick.player_id.is_(None),  # Game lines only (no player)
        Market.market_type.in_(game_line_types),
        Game.start_time >= today,
        Game.start_time < tomorrow + timedelta(days=7),  # Include upcoming week
    ]
    
    # Add freshness filters if requested
    if fresh_only:
        base_conditions.extend([
            # Only games that haven't started yet
            Game.start_time > utc_now_naive,
            # Only picks generated recently
            ModelPick.generated_at >= freshness_cutoff,
        ])
    
    # Build query with all necessary joins
    query = (
        select(ModelPick, Game, HomeTeam, AwayTeam, Market)
        .join(Game, ModelPick.game_id == Game.id)
        .join(HomeTeam, Game.home_team_id == HomeTeam.id)
        .join(AwayTeam, Game.away_team_id == AwayTeam.id)
        .join(Market, ModelPick.market_id == Market.id)
        .where(and_(*base_conditions))
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
    
    # Debug logging to track filtered/skipped picks
    logger.info(
        f"[game-lines] sport_id={sport_id}, fresh_only={fresh_only}: "
        f"returning {len(picks)} picks, total={total}"
    )
    
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


# =============================================================================
# 100% Hit Rate Props Endpoint
# =============================================================================

@router.get("/sports/{sport_id}/picks/100pct-hits", tags=["public"])
async def list_100_percent_props(
    sport_id: int,
    window: str = Query("last_5", description="Time window: season, last_10, last_5"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get player props with 100% hit rate over specified time window.
    
    These are props where the player has hit EVERY game in the window.
    Great for high-floor parlay legs.
    
    Args:
        sport_id: Sport database ID
        window: Time window - "season", "last_10", "last_5"
        limit: Maximum results to return
    
    Returns:
        List of 100% hit rate props with hit rate stats and model outputs
    """
    from app.services.parlay_service import get_100_percent_props
    from app.schemas.public import HundredPercentPropList
    
    # Validate sport exists
    sport = await db.get(Sport, sport_id)
    if not sport:
        raise HTTPException(status_code=404, detail=f"Sport {sport_id} not found")
    
    # Validate window
    valid_windows = ["season", "last_10", "last_5"]
    if window not in valid_windows:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid window: {window}. Valid options: {valid_windows}",
        )
    
    props = await get_100_percent_props(db, sport_id, window, limit)
    
    return HundredPercentPropList(
        items=props,
        total=len(props),
        window=window,
    )


# Convenience endpoint alias
@router.get("/hitrate/100", tags=["public"])
async def hitrate_100_alias(
    sport: str = Query(..., description="Sport key (nba, ncaab, nfl) or sport_id"),
    window: str = Query("last_5", description="Time window: season, last_10, last_5"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get player props with 100% hit rate (alias endpoint).
    
    This is a convenience alias for /sports/{sport_id}/picks/100pct-hits.
    
    Accepts sport as a key (nba, ncaab, nfl) or numeric sport_id.
    """
    from app.services.parlay_service import get_100_percent_props
    from app.schemas.public import HundredPercentPropList
    
    # Resolve sport key to ID
    sport_mapping = {
        "nba": "basketball_nba",
        "ncaab": "basketball_ncaab",
        "nfl": "americanfootball_nfl",
    }
    
    sport_key = sport_mapping.get(sport.lower(), sport.lower())
    
    # Try to find by key first
    result = await db.execute(
        select(Sport).where(Sport.key == sport_key)
    )
    sport_obj = result.scalar_one_or_none()
    
    # If not found by key, try by ID
    if not sport_obj and sport.isdigit():
        sport_obj = await db.get(Sport, int(sport))
    
    if not sport_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Sport '{sport}' not found. Use nba, ncaab, nfl, or a sport_id.",
        )
    
    # Validate window
    valid_windows = ["season", "last_10", "last_5"]
    if window not in valid_windows:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid window: {window}. Valid options: {valid_windows}",
        )
    
    props = await get_100_percent_props(db, sport_obj.id, window, limit)
    
    return HundredPercentPropList(
        items=props,
        total=len(props),
        window=window,
    )


# =============================================================================
# Parlay Builder Endpoint
# =============================================================================

@router.get("/sports/{sport_id}/parlays/builder", tags=["public"])
async def build_parlay(
    sport_id: int,
    leg_count: int = Query(3, ge=2, le=15, description="Number of legs (2-15)"),
    include_100_pct: bool = Query(False, description="Require at least one 100% hit rate leg"),
    min_leg_grade: str = Query("C", description="Minimum grade per leg (A, B, C, D)"),
    max_results: int = Query(5, ge=1, le=10, description="Number of parlays to return"),
    block_correlated: bool = Query(True, description="Block high-correlation parlays"),
    max_correlation_risk: str = Query("MEDIUM", description="Max allowed: LOW, MEDIUM, HIGH, CRITICAL"),
    db: AsyncSession = Depends(get_db),
):
    """
    Build optimized parlays from today's player prop picks.
    
    Grades each leg (A-F based on edge), calculates combined odds and EV,
    and returns LOCK/PLAY/SKIP recommendations.
    
    Grading:
    - A: Edge >= 5%
    - B: Edge >= 3%
    - C: Edge >= 1%
    - D: Edge >= 0%
    - F: Negative edge
    
    Labels:
    - LOCK: High-confidence parlay (all legs edge >= 2%, parlay EV >= 3%)
    - PLAY: Moderate confidence (parlay EV >= 1%)
    - SKIP: Not recommended (negative edge or low probability)
    
    Args:
        sport_id: Sport database ID
        leg_count: Number of legs per parlay (2-15)
        include_100_pct: Require at least one 100% hit rate leg
        min_leg_grade: Minimum grade for each leg
        max_results: Number of parlays to return
    
    Returns:
        ParlayBuilderResponse with recommended parlays
    """
    from app.services.parlay_service import build_parlays
    
    # Validate sport exists
    sport = await db.get(Sport, sport_id)
    if not sport:
        raise HTTPException(status_code=404, detail=f"Sport {sport_id} not found")
    
    # Validate grade
    valid_grades = ["A", "B", "C", "D", "F"]
    if min_leg_grade.upper() not in valid_grades:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid grade: {min_leg_grade}. Valid options: {valid_grades}",
        )
    
    # Validate correlation risk level
    valid_risk_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    if max_correlation_risk.upper() not in valid_risk_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid correlation risk: {max_correlation_risk}. Valid options: {valid_risk_levels}",
        )
    
    return await build_parlays(
        db,
        sport_id,
        leg_count=leg_count,
        include_100_pct=include_100_pct,
        min_leg_grade=min_leg_grade.upper(),
        max_results=max_results,
        block_correlated=block_correlated,
        max_correlation_risk=max_correlation_risk.upper(),
    )


# =============================================================================
# Alt-Line Explorer Endpoint
# =============================================================================

@router.get("/picks/{pick_id}/alt-lines", tags=["public"])
async def explore_alt_lines(
    pick_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Explore alternate lines for a player prop.
    
    Shows a ladder of alternate lines with:
    - Over/under probabilities from the model
    - Fair odds (no vig) based on model probability
    - Estimated market odds
    - EV for each line
    
    Use this to:
    - Find the best line for a player prop
    - Decide between safer vs riskier alt lines for parlays
    - Identify value at specific lines
    
    Args:
        pick_id: The ModelPick ID to explore
    
    Returns:
        AltLineExplorerResponse with all alternate lines
    """
    from app.services.parlay_service import explore_alt_lines as explore_fn
    from app.schemas.public import AltLineExplorerResponse
    
    try:
        return await explore_fn(db, pick_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# Metadata Endpoints
# =============================================================================

@router.get("/meta", tags=["public"])
async def get_data_freshness(
    db: AsyncSession = Depends(get_db),
):
    """
    Get data freshness metadata for all sports.
    
    Returns last_updated timestamps for each sport so the UI can show:
    "NBA slate last updated: 6:05 AM CT"
    
    This helps users know if data is fresh or stale.
    """
    from app.services.sync_metadata_service import get_frontend_meta
    
    return await get_frontend_meta(db)


@router.get("/meta/{sport_key}", tags=["public"])
async def get_sport_freshness(
    sport_key: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get data freshness for a specific sport.
    
    Args:
        sport_key: Sport identifier (e.g., "basketball_nba")
    
    Returns:
        Last updated timestamp and sync details
    """
    from app.services.sync_metadata_service import get_sync_metadata
    
    VALID_SPORTS = ["basketball_nba", "basketball_ncaab", "americanfootball_nfl"]
    
    if sport_key not in VALID_SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport_key}. Valid options: {VALID_SPORTS}",
        )
    
    metadata = await get_sync_metadata(db, sport_key, "games")
    
    if not metadata:
        return {
            "sport_key": sport_key,
            "last_updated": None,
            "relative": "never synced",
            "is_healthy": False,
        }
    
    now = datetime.now(timezone.utc)
    hours_ago = (now - metadata.last_updated).total_seconds() / 3600 if metadata.last_updated else None
    
    if hours_ago is not None:
        if hours_ago < 1:
            relative = "just now"
        elif hours_ago < 24:
            relative = f"{int(hours_ago)}h ago"
        else:
            relative = f"{int(hours_ago/24)}d ago"
    else:
        relative = "never"
    
    return {
        "sport_key": sport_key,
        "last_updated": metadata.last_updated.isoformat() if metadata.last_updated else None,
        "relative": relative,
        "games_count": metadata.games_count,
        "lines_count": metadata.lines_count,
        "props_count": metadata.props_count,
        "picks_count": metadata.picks_count,
        "source": metadata.source,
        "sync_duration_seconds": metadata.sync_duration_seconds,
        "is_healthy": metadata.is_healthy,
    }


# =============================================================================
# Debug/Diagnostic Endpoint
# =============================================================================

@router.get("/debug/date-check", tags=["debug"])
async def debug_date_check(db: AsyncSession = Depends(get_db)):
    """
    Debug endpoint to check date calculations and database state.
    
    Use this to verify timezone handling and what games are in the database.
    """
    from sqlalchemy import func
    
    # Current times
    now_et = datetime.now(EASTERN_TZ)
    now_utc = datetime.now(timezone.utc)
    
    # Today's boundaries in ET
    today_start_et = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start_et = today_start_et + timedelta(days=1)
    
    # Convert to UTC naive for DB
    today_utc = today_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    tomorrow_utc = tomorrow_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    
    # Count games in different time ranges
    total_games = await db.scalar(select(func.count(Game.id)))
    
    today_games = await db.scalar(
        select(func.count(Game.id)).where(
            Game.start_time >= today_utc,
            Game.start_time < tomorrow_utc,
        )
    )
    
    # Get a sample of recent games
    recent_games_result = await db.execute(
        select(Game.external_game_id, Game.start_time)
        .order_by(Game.start_time.desc())
        .limit(10)
    )
    recent_games = [
        {"id": g.external_game_id, "start_time": g.start_time.isoformat() if g.start_time else None}
        for g in recent_games_result.fetchall()
    ]
    
    return {
        "server_time": {
            "now_et": now_et.isoformat(),
            "now_utc": now_utc.isoformat(),
            "today_date_et": now_et.date().isoformat(),
        },
        "filter_boundaries": {
            "today_start_utc": today_utc.isoformat(),
            "tomorrow_start_utc": tomorrow_utc.isoformat(),
        },
        "database_counts": {
            "total_games": total_games,
            "games_matching_today_filter": today_games,
        },
        "recent_games_sample": recent_games,
        "diagnosis": (
            "STALE DATA: No games match today's filter. Run force-refresh."
            if today_games == 0 else
            f"OK: {today_games} games found for today ({now_et.date().isoformat()})"
        ),
    }
