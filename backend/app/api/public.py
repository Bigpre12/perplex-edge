"""Public API endpoints for the betting analytics cheat sheet UI."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query, HTTPException
from app.core.endpoint_rate_limiter import picks_rate_limit, parlays_rate_limit

logger = logging.getLogger(__name__)
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from app.core.database import get_db
from app.core.sport_availability import get_sport_status, get_all_sport_statuses, get_current_tennis_tournaments
from app.models import Sport, Team, Game, Market, Player, ModelPick, Line, Injury
from app.models.injury import EXCLUDED_INJURY_STATUSES
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
    QuoteRequest,
)
from app.services.prop_filters import dedupe_player_props

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
# Sport Availability Endpoint
# =============================================================================

@router.get("/sports/availability", tags=["public"])
async def get_sports_availability():
    """
    Get current availability status for all sports.
    
    Returns whether each sport is in-season, off-season, or playoffs,
    along with helpful messages about why data might be empty.
    
    Use this to understand why a sport might have no props:
    - Off-season: No live games available
    - Active: Should have data (check sync status if empty)
    """
    statuses = get_all_sport_statuses()
    tennis_tournaments = get_current_tennis_tournaments()
    
    return {
        "checked_at": datetime.now(EASTERN_TZ).isoformat(),
        "sports": statuses,
        "tennis_tournaments": tennis_tournaments,
        "notes": {
            "tennis": "Tennis uses tournament-specific data. Empty results may indicate no active tournaments for that tour.",
            "nfl": "NFL is seasonal (September-February). No data available during off-season.",
            "ncaaf": "College football is seasonal (August-January). No data available during off-season.",
        }
    }


@router.get("/sports/{sport_id}/availability", tags=["public"])
async def get_sport_availability(
    sport_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get availability status for a specific sport.
    
    Returns whether the sport is in-season and why data might be empty.
    For unknown sport IDs, returns a default "not configured" response instead of 404.
    """
    from app.core.constants import SPORT_ID_TO_KEY
    
    sport_key = SPORT_ID_TO_KEY.get(sport_id)
    if not sport_key:
        # Return graceful response for unknown sport IDs instead of 404
        return {
            "sport_id": sport_id,
            "sport_key": None,
            "status": {
                "is_active": False,
                "message": f"Sport {sport_id} not configured",
                "next_action": "This sport may not be supported yet.",
            },
            "data_counts": {
                "games_today": 0,
                "total_picks": 0,
            },
            "data_reason": f"Sport ID {sport_id} is not mapped in the system.",
            "tennis_note": None,
        }
    
    status = get_sport_status(sport_key)
    
    # Also get actual data counts
    now_et = datetime.now(EASTERN_TZ)
    today_start_et = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start_et = today_start_et + timedelta(days=1)
    today_utc = today_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    tomorrow_utc = tomorrow_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    
    # Count games and picks
    games_count = await db.scalar(
        select(func.count(Game.id))
        .where(and_(
            Game.sport_id == sport_id,
            Game.start_time >= today_utc,
            Game.start_time < tomorrow_utc,
        ))
    )
    
    picks_count = await db.scalar(
        select(func.count(ModelPick.id))
        .where(ModelPick.sport_id == sport_id)
    )
    
    # Determine why data might be empty
    reason = None
    if not status["is_active"]:
        reason = status["message"]
    elif games_count == 0:
        reason = "No games scheduled for today. Data sync may be pending or no games posted yet."
    elif picks_count == 0:
        reason = "Games exist but no picks generated. Check sync status."
    
    return {
        "sport_id": sport_id,
        "sport_key": sport_key,
        "status": status,
        "data_counts": {
            "games_today": games_count,
            "total_picks": picks_count,
        },
        "data_reason": reason,
        "tennis_note": "Tennis uses tournament-specific APIs. Check /sports/availability for active tournaments." if "tennis" in sport_key else None,
    }


# =============================================================================
# Tonight Summary Endpoint (What's On Tonight Dashboard)
# =============================================================================

@router.get("/tonight/summary", tags=["public"])
async def get_tonight_summary(
    db: AsyncSession = Depends(get_db),
):
    """
    Get tonight's slate summary across all sports.
    
    Returns game counts, prop counts, and best EV for each sport,
    plus an overall slate quality indicator.
    
    Use this to answer: "What should I focus on tonight?"
    """
    from app.schemas.public import SportTonightSummary, TonightSummaryResponse
    from app.models import ModelPick
    
    # Calculate today's date range using US Eastern time
    now_et = datetime.now(EASTERN_TZ)
    today_start_et = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start_et = today_start_et + timedelta(days=1)
    
    # Convert to UTC (naive datetimes for PostgreSQL)
    today_utc = today_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    tomorrow_utc = tomorrow_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    
    # Get all sports
    sports_result = await db.execute(select(Sport).order_by(Sport.name))
    all_sports = sports_result.scalars().all()
    
    sport_summaries = []
    total_games = 0
    total_props = 0
    overall_best_ev = None
    
    for sport in all_sports:
        # Count games for this sport today
        games_count_result = await db.execute(
            select(func.count(Game.id))
            .where(
                and_(
                    Game.sport_id == sport.id,
                    Game.start_time >= today_utc,
                    Game.start_time < tomorrow_utc,
                )
            )
        )
        games_count = games_count_result.scalar() or 0
        
        # Count player props for this sport today
        props_result = await db.execute(
            select(
                func.count(ModelPick.id),
                func.max(ModelPick.expected_value),
                func.avg(ModelPick.expected_value),
            )
            .join(Game, ModelPick.game_id == Game.id)
            .where(
                and_(
                    Game.sport_id == sport.id,
                    Game.start_time >= today_utc,
                    Game.start_time < tomorrow_utc,
                    ModelPick.player_id.isnot(None),  # Player props only
                )
            )
        )
        props_row = props_result.one()
        props_count = props_row[0] or 0
        best_ev = props_row[1]
        avg_ev = props_row[2]
        
        # Determine slate quality for this sport
        if games_count == 0:
            slate_quality = "empty"
        elif props_count >= 100:
            slate_quality = "loaded"
        elif props_count >= 30:
            slate_quality = "normal"
        else:
            slate_quality = "thin"
        
        # Only include sports with games today
        if games_count > 0:
            sport_summaries.append(SportTonightSummary(
                sport_id=sport.id,
                sport_name=sport.name,
                sport_key=sport.key,
                games_count=games_count,
                props_count=props_count,
                best_ev=round(best_ev, 4) if best_ev else None,
                avg_ev=round(avg_ev, 4) if avg_ev else None,
                slate_quality=slate_quality,
            ))
            
            total_games += games_count
            total_props += props_count
            
            if best_ev and (overall_best_ev is None or best_ev > overall_best_ev):
                overall_best_ev = best_ev
    
    # Sort by props count (most action first)
    sport_summaries.sort(key=lambda s: s.props_count, reverse=True)
    
    # Overall slate quality
    if total_props >= 200:
        overall_quality = "loaded"
    elif total_props >= 50:
        overall_quality = "normal"
    elif total_props > 0:
        overall_quality = "thin"
    else:
        overall_quality = "empty"
    
    return TonightSummaryResponse(
        date=now_et.strftime("%Y-%m-%d"),
        timezone="US/Eastern",
        sports=sport_summaries,
        total_games=total_games,
        total_props=total_props,
        overall_best_ev=round(overall_best_ev, 4) if overall_best_ev else None,
        slate_quality=overall_quality,
    )


# =============================================================================
# Hot/Cold Players Endpoints
# =============================================================================

@router.get("/players/hot-cold", tags=["public"])
async def get_hot_cold_players_endpoint(
    sport_id: Optional[int] = Query(None, description="Filter by sport ID"),
    min_picks: int = Query(3, ge=1, le=20, description="Minimum picks in 7 days to qualify"),
    limit: int = Query(25, ge=1, le=100, description="Max results per category"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get hot and cold players based on recent performance.
    
    Hot players: 3+ win streak OR 70%+ hit rate in last 7 days
    Cold players: 3+ loss streak OR below 40% hit rate in last 7 days
    
    Returns aggregated stats across all markets for each player.
    """
    from app.services.hot_cold_service import get_hot_cold_players
    
    result = await get_hot_cold_players(
        db,
        sport_id=sport_id,
        min_picks=min_picks,
        limit=limit,
    )
    
    return {
        "hot": result["hot"],
        "cold": result["cold"],
        "filters": {
            "sport_id": sport_id,
            "min_picks": min_picks,
            "limit": limit,
        },
    }


@router.get("/players/hot-cold/by-market", tags=["public"])
async def get_hot_cold_players_by_market_endpoint(
    sport_id: Optional[int] = Query(None, description="Filter by sport ID"),
    market: Optional[str] = Query(None, description="Filter by market (PTS, REB, AST, 3PM, PRA)"),
    side: Optional[str] = Query(None, description="Filter by side (over, under)"),
    min_picks: int = Query(3, ge=1, le=20, description="Minimum picks in 7 days to qualify"),
    limit: int = Query(25, ge=1, le=100, description="Max results per category"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get hot and cold players by specific market (stat type).
    
    Market-aware hot/cold tracking enables labels like:
    "CJ McCollum – 6/6 on 3PM OVER (100% hit rate)"
    
    Hot players: 3+ win streak OR 70%+ hit rate in last 7 days
    Cold players: 3+ loss streak OR below 40% hit rate in last 7 days
    
    Returns per-market stats (e.g., separate entries for PTS OVER vs PTS UNDER).
    """
    from app.services.hot_cold_service import get_hot_cold_players_by_market
    
    result = await get_hot_cold_players_by_market(
        db,
        sport_id=sport_id,
        market=market,
        side=side,
        min_picks=min_picks,
        limit=limit,
    )
    
    return {
        "hot": result["hot"],
        "cold": result["cold"],
        "filters": {
            "sport_id": sport_id,
            "market": market,
            "side": side,
            "min_picks": min_picks,
            "limit": limit,
        },
    }


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

@router.get("/sports/{sport_id}/picks/player-props", response_model=PlayerPropPickList, tags=["public"], dependencies=[Depends(picks_rate_limit)])
async def list_player_prop_picks(
    sport_id: int,
    stat_type: Optional[str] = Query(None, description="Filter by stat type (PTS, REB, AST, 3PM, PRA, etc.)"),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="Minimum confidence score (0-1)"),
    min_ev: float = Query(0.0, description="Minimum expected value (e.g., 0.03 for 3%)"),
    risk_levels: Optional[str] = Query(None, description="Comma-separated Kelly risk levels: NO_BET,SMALL,STANDARD,CONFIDENT,STRONG,MAX"),
    game_id: Optional[int] = Query(None, description="Filter by specific game"),
    player_id: Optional[int] = Query(None, description="Filter by specific player"),
    side: Optional[str] = Query(None, description="Filter by side (over/under)"),
    fresh_only: bool = Query(True, description="Filter out stale props (games started, old picks). Set to false to show all."),
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
    # This ensures picks show for today's US schedule even after midnight UTC
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
        .where(Injury.status.in_(EXCLUDED_INJURY_STATUSES))
        .scalar_subquery()
    )
    
    # Stat types hidden from the UI (still tracked in the engine)
    HIDDEN_STAT_TYPES = {"STL", "BLK"}

    # Base filter conditions
    # IMPORTANT: Filter by BOTH ModelPick.sport_id AND Game.sport_id to prevent data bleed
    # between NFL (31) and NCAAF (41) or other sports with similar data structures
    base_conditions = [
        ModelPick.sport_id == sport_id,
        Game.sport_id == sport_id,  # Double-check game also belongs to this sport
        # ModelPick.is_active == True,  # Disabled - show all picks regardless of active status
        ModelPick.player_id.isnot(None),
        ModelPick.player_id.notin_(injured_subquery),  # Exclude injured players
        Market.stat_type.notin_(HIDDEN_STAT_TYPES),  # Hide blocks/steals from UI
        # Market.market_type == "player_prop",  # Disabled - player_id filter is sufficient
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
            # Only scheduled/pregame games (not in_progress, final, postponed, etc.)
            Game.status.in_(["scheduled", "pregame"]),
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
    
    if player_id:
        query = query.where(ModelPick.player_id == player_id)
    
    if side:
        query = query.where(ModelPick.side == side.lower())
    
    # Order by EV descending (best picks first)
    query = query.order_by(ModelPick.expected_value.desc())
    
    # Get total count before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    rows = result.all()
    
    # ==========================================================================
    # STALE FILTER: Apply additional freshness checks at runtime
    # ==========================================================================
    from app.services.prop_filters import is_fresh_prop, dedupe_response_items
    
    if fresh_only:
        filtered_rows = []
        for row in rows:
            pick, player, player_team, game, home_team, away_team, market = row
            if is_fresh_prop(pick, game):
                filtered_rows.append(row)
        
        if len(filtered_rows) < len(rows):
            logger.info(f"[player-props] Stale filter removed {len(rows) - len(filtered_rows)} props")
        rows = filtered_rows
    
    # ==========================================================================
    # DEDUPE: Remove duplicate (player, stat, line) combinations
    # ==========================================================================
    # Build a mapping from dedupe key to best row (by EV)
    seen_props: dict = {}
    for row in rows:
        pick, player, player_team, game, home_team, away_team, market = row
        # Skip invalid line values
        if pick.line_value is None or pick.line_value == 0:
            continue
        
        key = (player.id, market.stat_type, pick.line_value)
        ev = pick.expected_value or 0.0
        
        if key not in seen_props or ev > (seen_props[key][0].expected_value or 0.0):
            seen_props[key] = row
    
    deduped_rows = list(seen_props.values())
    if len(deduped_rows) < len(rows):
        logger.info(f"[player-props] Dedupe reduced {len(rows)} -> {len(deduped_rows)} props")
    rows = deduped_rows
    
    # PERFORMANCE FIX: Bulk fetch book lines instead of N+1 queries
    # Collect all unique (game_id, player_id, market_id, side) combinations
    line_keys = set()
    for row in rows:
        pick, player, player_team, game, home_team, away_team, market = row
        if pick.line_value is not None and pick.line_value != 0:
            line_keys.add((game.id, player.id, market.id, pick.side))
    
    # Bulk fetch all relevant lines in a single query
    book_lines_map: dict[tuple, list] = {}
    if line_keys:
        # Build OR conditions for all key combinations
        from sqlalchemy import or_, tuple_
        line_conditions = [
            and_(
                Line.game_id == gid,
                Line.player_id == pid,
                Line.market_id == mid,
                Line.side == side,
                Line.is_current == True,
            )
            for gid, pid, mid, side in line_keys
        ]
        
        lines_result = await db.execute(
            select(Line).where(or_(*line_conditions))
        )
        all_lines = lines_result.scalars().all()
        
        # Group lines by key
        for line in all_lines:
            key = (line.game_id, line.player_id, line.market_id, line.side)
            if key not in book_lines_map:
                book_lines_map[key] = []
            book_lines_map[key].append(line)
    
    # ==========================================================================
    # OPENING LINES: Fetch earliest line per prop for line movement tracking
    # ==========================================================================
    opening_lines_map: dict[tuple, Line] = {}
    if line_keys:
        # Subquery to find MIN fetched_at per (game_id, player_id, market_id, side)
        from sqlalchemy import func as sqlfunc
        earliest_subq = (
            select(
                Line.game_id,
                Line.player_id,
                Line.market_id,
                Line.side,
                sqlfunc.min(Line.fetched_at).label("earliest_fetch"),
            )
            .where(
                or_(*[
                    and_(
                        Line.game_id == gid,
                        Line.player_id == pid,
                        Line.market_id == mid,
                        Line.side == side,
                    )
                    for gid, pid, mid, side in line_keys
                ])
            )
            .group_by(Line.game_id, Line.player_id, Line.market_id, Line.side)
            .subquery()
        )
        
        # Join to get the actual opening line records
        opening_lines_result = await db.execute(
            select(Line)
            .join(
                earliest_subq,
                and_(
                    Line.game_id == earliest_subq.c.game_id,
                    Line.player_id == earliest_subq.c.player_id,
                    Line.market_id == earliest_subq.c.market_id,
                    Line.side == earliest_subq.c.side,
                    Line.fetched_at == earliest_subq.c.earliest_fetch,
                )
            )
        )
        opening_lines = opening_lines_result.scalars().all()
        
        # Map by key
        for line in opening_lines:
            key = (line.game_id, line.player_id, line.market_id, line.side)
            # Keep first (should be unique after join, but safety)
            if key not in opening_lines_map:
                opening_lines_map[key] = line
    
    # Import Kelly calculation once outside loop
    from app.services.parlay_service import calculate_kelly_fraction
    
    # Build response
    picks = []
    skipped_count = 0
    for row in rows:
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
        
        # Get book lines from pre-fetched cache (no N+1 query!)
        line_key = (game.id, player.id, market.id, pick.side)
        cached_lines = book_lines_map.get(line_key, [])
        
        # Process book lines
        book_lines = []
        best_ev = float("-inf")
        best_book = None
        line_values = []
        
        for line in cached_lines:
            ev = calculate_ev_for_odds(pick.model_probability, int(line.odds))
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
        
        line_variance = None
        if len(line_values) >= 2:
            line_variance = round(max(line_values) - min(line_values), 1)
        
        # Calculate Kelly sizing for this pick
        kelly = calculate_kelly_fraction(
            win_prob=pick.model_probability,
            american_odds=int(pick.odds),
        )
        
        # Calculate line movement from opening line
        opening_line_data = opening_lines_map.get(line_key)
        opening_line = None
        opening_odds = None
        line_movement = None
        odds_movement = None
        movement_direction = None
        
        if opening_line_data:
            opening_line = opening_line_data.line_value
            opening_odds = int(opening_line_data.odds) if opening_line_data.odds else None
            
            # Line movement = current - opening (positive = line moved up)
            if opening_line is not None and pick.line_value is not None:
                line_movement = round(pick.line_value - opening_line, 1)
            
            # Odds movement = current - opening (negative = sharpened/got worse for bettor)
            if opening_odds is not None:
                odds_movement = int(pick.odds) - opening_odds
            
            # Determine movement direction
            # "sharp_up" = line moved up against public (sharps bet over)
            # "sharp_down" = line moved down against public (sharps bet under)
            # "steam" = significant odds movement but line stable
            # "reverse" = line moved opposite to expected direction
            # "stable" = no significant movement
            if line_movement is not None:
                if abs(line_movement) < 0.5:
                    movement_direction = "stable"
                elif line_movement > 0 and pick.side == "over":
                    movement_direction = "sharp_up"  # Line moved up, betting over looks worse (sharps on over)
                elif line_movement < 0 and pick.side == "under":
                    movement_direction = "sharp_down"  # Line moved down, betting under looks worse (sharps on under)
                elif line_movement > 0 and pick.side == "under":
                    movement_direction = "reverse"  # Line moved up but we're betting under - good for us
                elif line_movement < 0 and pick.side == "over":
                    movement_direction = "reverse"  # Line moved down but we're betting over - good for us
                else:
                    movement_direction = "steam" if abs(odds_movement or 0) > 10 else "stable"
        
        # Get sport_key for reliable frontend label mapping
        from app.core.constants import SPORT_ID_TO_KEY
        pick_sport_key = SPORT_ID_TO_KEY.get(pick.sport_id, f"unknown_{pick.sport_id}")
        
        picks.append(PlayerPropPick(
            pick_id=pick.id,
            sport_id=pick.sport_id,  # Include actual sport_id from database
            sport_key=pick_sport_key,  # Include sport_key for reliable label mapping
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
            # Line movement tracking
            opening_line=opening_line,
            opening_odds=opening_odds,
            line_movement=line_movement,
            odds_movement=odds_movement,
            movement_direction=movement_direction,
        ))
    
    # Dedupe props - merge book_lines for same player/stat/line combos
    picks = dedupe_player_props(picks)
    
    # Filter by Kelly risk levels (computed field, filter in-memory)
    if risk_levels:
        allowed_levels = set(risk_levels.upper().split(","))
        picks = [p for p in picks if p.kelly_risk_level in allowed_levels]
        logger.info(f"[player-props] risk_levels filter applied: {allowed_levels}, {len(picks)} picks remaining")
    
    # Debug logging to track filtered/skipped picks
    # Include sport_key for debugging NFL/NCAAF bleed issues
    from app.core.constants import SPORT_ID_TO_KEY
    sport_key_debug = SPORT_ID_TO_KEY.get(sport_id, "UNKNOWN")
    logger.info(
        f"[player-props] sport_id={sport_id} ({sport_key_debug}), fresh_only={fresh_only}: "
        f"returning {len(picks)} picks, skipped {skipped_count} with invalid line_value, total={total}"
    )
    
    # Extra validation: log warning if any picks have mismatched sport_id
    mismatched = [p for p in picks if hasattr(p, 'sport_id') and p.sport_id != sport_id]
    if mismatched:
        logger.warning(
            f"[SPORT_ID_MISMATCH] sport_id={sport_id} request returned {len(mismatched)} picks "
            f"with different sport_ids: {set(getattr(p, 'sport_id', None) for p in mismatched)}"
        )
    
    return PlayerPropPickList(
        items=picks,
        total=len(picks),  # Update total to reflect risk_levels filter
        filters={
            "sport_id": sport_id,
            "stat_type": stat_type,
            "min_confidence": min_confidence,
            "min_ev": min_ev,
            "risk_levels": risk_levels,
            "game_id": game_id,
        },
    )


# =============================================================================
# Game Line Picks Endpoints
# =============================================================================

@router.get("/sports/{sport_id}/picks/game-lines", response_model=GameLinePickList, tags=["public"], dependencies=[Depends(picks_rate_limit)])
async def list_game_line_picks(
    sport_id: int,
    market_type: Optional[str] = Query(None, description="Filter by market type (spread, total, moneyline)"),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="Minimum confidence score (0-1)"),
    min_ev: float = Query(0.0, description="Minimum expected value (e.g., 0.03 for 3%)"),
    game_id: Optional[int] = Query(None, description="Filter by specific game"),
    fresh_only: bool = Query(True, description="Filter out stale picks (games started, old picks). Set to false to show all."),
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
    # This ensures picks show for today's US schedule even after midnight UTC
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
    
    # Base filter conditions
    # IMPORTANT: Filter by BOTH ModelPick.sport_id AND Game.sport_id to prevent data bleed
    base_conditions = [
        ModelPick.sport_id == sport_id,
        Game.sport_id == sport_id,  # Double-check game also belongs to this sport
        # ModelPick.is_active == True,  # Disabled - show all picks regardless of active status
        ModelPick.player_id.is_(None),  # Game lines only (no player)
        # Market.market_type.in_(["spread", "total", "moneyline"]),  # Disabled - player_id filter is sufficient
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
            # Only scheduled/pregame games (not in_progress, final, postponed, etc.)
            Game.status.in_(["scheduled", "pregame"]),
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
        valid_types = ["spread", "total", "moneyline"]
        if market_type.lower() not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid market_type. Must be one of: {valid_types}",
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
# Debug Endpoint
# =============================================================================

@router.get("/sports/{sport_id}/picks/debug", tags=["public"])
async def debug_picks(
    sport_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Enhanced debug endpoint to diagnose pick visibility issues."""
    # Get picks
    result = await db.execute(
        select(ModelPick)
        .where(ModelPick.sport_id == sport_id)
        .limit(limit)
    )
    picks = result.scalars().all()
    
    # Get related data for each pick
    picks_data = []
    for p in picks:
        # Check if player exists
        player_exists = None
        player_name = None
        if p.player_id:
            player_result = await db.execute(
                select(Player.id, Player.name).where(Player.id == p.player_id)
            )
            player = player_result.first()
            player_exists = player is not None
            player_name = player[1] if player else None
        
        # Check game start_time
        game_result = await db.execute(
            select(Game.start_time, Game.status).where(Game.id == p.game_id)
        )
        game = game_result.first()
        
        # Check if player is injured
        injury_status = None
        if p.player_id:
            injury_result = await db.execute(
                select(Injury.status).where(Injury.player_id == p.player_id)
            )
            injury = injury_result.first()
            injury_status = injury[0] if injury else None
        
        picks_data.append({
            "id": p.id,
            "player_id": p.player_id,
            "player_name": player_name,
            "player_exists": player_exists,
            "injury_status": injury_status,
            "game_id": p.game_id,
            "game_start_time": game[0].isoformat() if game and game[0] else None,
            "game_status": game[1] if game else None,
            "market_id": p.market_id,
            "is_active": p.is_active,
            "side": p.side,
            "line_value": p.line_value,
        })
    
    # Get today's date range info
    now_et = datetime.now(EASTERN_TZ)
    today_start_et = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
    today_utc = today_start_et.astimezone(timezone.utc).replace(tzinfo=None)
    tomorrow_utc = today_utc + timedelta(days=1)
    week_later_utc = today_utc + timedelta(days=7)
    
    return {
        "debug_info": {
            "now_et": now_et.isoformat(),
            "today_utc": today_utc.isoformat(),
            "tomorrow_utc": tomorrow_utc.isoformat(),
            "week_later_utc": week_later_utc.isoformat(),
            "filter_range": f"{today_utc.isoformat()} to {week_later_utc.isoformat()}",
        },
        "total": len(picks_data),
        "picks": picks_data,
    }


# =============================================================================
# 100% Hit Rate Props Endpoint
# =============================================================================

@router.get("/sports/{sport_id}/picks/100pct-hits", tags=["public"])
async def list_100_percent_props(
    sport_id: int,
    window: str = Query("last_5", description="Time window: season, last_10, last_5"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    min_hit_rate: float = Query(0.70, ge=0.0, le=1.0, description="Minimum hit rate fallback (0-1, default 0.70 = 70%)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get player props with high hit rates over specified time window.
    
    First returns props with 100% hit rate. If none found, falls back to 
    showing props with hit_rate >= min_hit_rate, sorted by hit rate descending.
    Great for high-floor parlay legs.
    
    Args:
        sport_id: Sport database ID
        window: Time window - "season", "last_10", "last_5"
        limit: Maximum results to return
        min_hit_rate: Minimum hit rate for fallback (0.0-1.0, default 0.70)
    
    Returns:
        List of high hit rate props with hit rate stats and model outputs
    """
    from app.services.parlay_service import get_100_percent_props
    from app.schemas.public import HundredPercentPropList
    
    logger.info(f"[100pct-hits] Request: sport_id={sport_id}, window={window}, limit={limit}")
    
    # Validate sport exists
    sport = await db.get(Sport, sport_id)
    if not sport:
        logger.warning(f"[100pct-hits] Sport {sport_id} not found")
        raise HTTPException(status_code=404, detail=f"Sport {sport_id} not found")
    
    # Validate window
    valid_windows = ["season", "last_10", "last_5"]
    if window not in valid_windows:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid window: {window}. Valid options: {valid_windows}",
        )
    
    # Wrap in try/except to fail gracefully instead of crashing
    try:
        props = await get_100_percent_props(db, sport_id, window, limit, min_hit_rate)
        
        logger.info(f"[100pct-hits] Returning {len(props)} props for sport {sport_id}")
        
        # ALWAYS return a valid JSON response with items array
        response = HundredPercentPropList(
            items=props if props else [],
            total=len(props) if props else 0,
            window=window,
        )
        return response
    except Exception as e:
        logger.error(f"[100pct-hits] Error for sport {sport_id}: {e}", exc_info=True)
        # Return empty response instead of 500 error
        return HundredPercentPropList(
            items=[],
            total=0,
            window=window,
        )


# Convenience endpoint alias
@router.get("/hitrate/100", tags=["public"])
async def hitrate_100_alias(
    sport: str = Query(..., description="Sport key (nba, ncaab, nfl) or sport_id"),
    window: str = Query("last_5", description="Time window: season, last_10, last_5"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    min_hit_rate: float = Query(0.70, ge=0.0, le=1.0, description="Minimum hit rate fallback (0-1, default 0.70 = 70%)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get player props with high hit rates (alias endpoint).
    
    This is a convenience alias for /sports/{sport_id}/picks/100pct-hits.
    Returns 100% hit rate props first, then falls back to high hit rate props.
    
    Accepts sport as a key (nba, ncaab, nfl) or numeric sport_id.
    """
    from app.services.parlay_service import get_100_percent_props
    from app.schemas.public import HundredPercentPropList
    
    # Resolve sport key to ID
    sport_mapping = {
        "nba": "basketball_nba",
        "ncaab": "basketball_ncaab",
        "nfl": "americanfootball_nfl",
        "mlb": "baseball_mlb",
        "atp": "tennis_atp",
        "wta": "tennis_wta",
        "tennis": "tennis_atp",  # Default to ATP
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
    
    # Wrap in try/except to fail gracefully instead of crashing
    try:
        props = await get_100_percent_props(db, sport_obj.id, window, limit, min_hit_rate)
        
        return HundredPercentPropList(
            items=props,
            total=len(props),
            window=window,
        )
    except Exception as e:
        logger.error(f"100% hit rate alias error for sport {sport}: {e}", exc_info=True)
        # Return empty response instead of 500 error
        return HundredPercentPropList(
            items=[],
            total=0,
            window=window,
        )


# =============================================================================
# Parlay Builder Endpoint
# =============================================================================

@router.get("/sports/{sport_id}/parlays/builder", tags=["public"], dependencies=[Depends(parlays_rate_limit)])
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
    from app.schemas.public import ParlayBuilderResponse
    
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
    
    # Wrap in try/except to ensure proper response even on errors
    # This prevents CORS issues when the endpoint crashes
    try:
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
    except Exception as e:
        logger.error(f"Parlay builder error for sport {sport_id}: {e}", exc_info=True)
        # Return empty response instead of 500 error to prevent CORS issues
        return ParlayBuilderResponse(
            parlays=[],
            total_candidates=0,
            leg_count=leg_count,
            filters_applied={
                "min_leg_grade": min_leg_grade.upper(),
                "include_100_pct": include_100_pct,
                "sport_id": sport_id,
            },
        )


# =============================================================================
# Auto-Generate Optimal Slips Endpoint
# =============================================================================

@router.get("/sports/{sport_id}/parlays/auto-generate", tags=["public"], dependencies=[Depends(parlays_rate_limit)])
async def auto_generate_slips(
    sport_id: int,
    platform: str = Query("prizepicks", description="Platform: prizepicks, fliff, underdog, sportsbook"),
    leg_count: int = Query(4, ge=2, le=6, description="Legs per slip (2-6)"),
    slip_count: int = Query(3, ge=1, le=5, description="Number of slips to generate (1-5)"),
    min_leg_ev: float = Query(0.03, ge=0.0, le=0.20, description="Min EV per leg (0.03 = 3%)"),
    min_confidence: float = Query(0.55, ge=0.40, le=0.80, description="Min model confidence per leg"),
    allow_correlation: bool = Query(False, description="Allow correlated legs within slips"),
    db: AsyncSession = Depends(get_db),
):
    """
    Auto-generate N optimal non-overlapping parlays for tonight.
    
    This is a "one-click" endpoint that generates the best slips for a DFS platform.
    Each slip uses completely different legs (no shared picks), so you can fire
    multiple slips without redundancy.
    
    Example: "Generate 3 best 4-leg slips for PrizePicks tonight"
    
    The response includes:
    - `slips`: List of non-overlapping optimal parlays
    - `slate_quality`: "STRONG", "GOOD", "THIN", or "PASS"
    - `avg_slip_ev`: Average EV across all slips
    - `total_suggested_units`: Total Kelly stake suggestion
    
    Slate quality meaning:
    - STRONG: Full slate with avg EV >= 5%
    - GOOD: Full slate with avg EV >= 2%
    - THIN: Partial slate (couldn't generate all requested slips)
    - PASS: No valid slips - consider passing on tonight's slate
    """
    from app.services.parlay_service import auto_generate_slips as generate_slips
    from app.schemas.public import AutoGenerateSlipsResponse
    
    # Validate sport exists
    sport = await db.get(Sport, sport_id)
    if not sport:
        raise HTTPException(status_code=404, detail=f"Sport {sport_id} not found")
    
    # Validate platform
    valid_platforms = ["prizepicks", "fliff", "underdog", "sportsbook"]
    if platform.lower() not in valid_platforms:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform: {platform}. Valid options: {valid_platforms}",
        )
    
    try:
        result = await generate_slips(
            db,
            sport_id=sport_id,
            platform=platform.lower(),
            leg_count=leg_count,
            slip_count=slip_count,
            min_leg_ev=min_leg_ev,
            min_confidence=min_confidence,
            allow_correlation=allow_correlation,
        )
        
        return AutoGenerateSlipsResponse(
            slips=result["slips"],
            slip_count=result["slip_count"],
            leg_count=result["leg_count"],
            platform=result["platform"],
            total_candidates=result["total_candidates"],
            filters=result["filters"],
            avg_slip_ev=result["avg_slip_ev"],
            avg_slip_probability=result["avg_slip_probability"],
            total_suggested_units=result["total_suggested_units"],
            slate_quality=result["slate_quality"],
        )
    
    except Exception as e:
        logger.error(f"Auto-generate error for sport {sport_id}: {e}", exc_info=True)
        from app.schemas.public import AutoGenerateSlipsResponse
        return AutoGenerateSlipsResponse(
            slips=[],
            slip_count=0,
            leg_count=leg_count,
            platform=platform.lower(),
            total_candidates=0,
            filters={
                "min_leg_ev": min_leg_ev,
                "min_confidence": min_confidence,
                "allow_correlation": allow_correlation,
                "sport_id": sport_id,
            },
            avg_slip_ev=0.0,
            avg_slip_probability=0.0,
            total_suggested_units=0.0,
            slate_quality="PASS",
        )


# =============================================================================
# Real-Time Parlay Quote Endpoint
# =============================================================================

@router.post("/parlays/quote", tags=["public"], dependencies=[Depends(parlays_rate_limit)])
async def quote_parlay(
    request: "QuoteRequest",
    db: AsyncSession = Depends(get_db),
):
    """
    Get real-time odds quote for parlay legs.
    
    This endpoint fetches the current market odds for each leg and calculates
    updated parlay pricing. Use this to:
    
    1. **Track odds movement** - See if odds changed since you built the parlay
    2. **Update parlay price** - Get accurate payout based on current odds
    3. **Verify freshness** - Know which legs have stale odds
    
    Each leg in the request should include:
    - `game_id`: Required game identifier
    - `player_id`: Player ID for player props (null for game lines)
    - `stat_type`: Stat type for player props (PTS, REB, AST, etc.)
    - `line_value`: The betting line (24.5, -3.5, etc.)
    - `side`: "over", "under", "home", "away"
    - `model_odds`: Original odds from model pick (optional, for movement detection)
    - `model_prob`: Model probability (optional, for EV calculation)
    
    Returns:
    - `legs`: Each leg with current odds, edge, and movement info
    - `parlay_odds`: Combined parlay odds (American)
    - `parlay_ev`: Expected value based on model probabilities
    - `has_movement`: True if any leg odds changed
    - `stale_legs`: Count of legs with potentially stale odds
    
    Example request:
    ```json
    {
        "legs": [
            {
                "game_id": 123,
                "player_id": 456,
                "stat_type": "PTS",
                "line_value": 24.5,
                "side": "over",
                "model_odds": -115,
                "model_prob": 0.58
            },
            {
                "game_id": 124,
                "player_id": 789,
                "stat_type": "REB",
                "line_value": 9.5,
                "side": "over",
                "model_odds": -110,
                "model_prob": 0.55
            }
        ]
    }
    ```
    """
    from app.services.live_odds_service import quote_parlay_legs
    from app.schemas.public import QuoteRequest, QuoteResponse
    
    try:
        # Convert request to dict format for service
        legs_data = [
            {
                "game_id": leg.game_id,
                "player_id": leg.player_id,
                "stat_type": leg.stat_type,
                "line_value": leg.line_value,
                "side": leg.side,
                "model_odds": leg.model_odds,
                "model_prob": leg.model_prob,
            }
            for leg in request.legs
        ]
        
        result = await quote_parlay_legs(
            db,
            legs=legs_data,
            use_cache=request.use_cache,
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Quote parlay error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to quote parlay: {str(e)[:200]}")


@router.get("/parlays/odds-health", tags=["public"])
async def get_odds_health(
    sport_id: Optional[int] = Query(None, description="Optional sport ID filter"),
    db: AsyncSession = Depends(get_db),
):
    """
    Check odds data freshness and health.
    
    Use this to determine if the odds data is fresh enough for live betting.
    Shows a status banner in the UI when odds may be stale.
    
    Status levels:
    - `healthy`: Most odds updated recently (>90% fresh)
    - `degraded`: Some stale odds (50-90% fresh)
    - `stale`: Mostly stale odds (<50% fresh)
    - `no_data`: No odds data available
    
    Returns:
    - `status`: Health status string
    - `freshness_pct`: Percentage of fresh lines
    - `newest_update`: Most recent odds update time
    - `stale_threshold_minutes`: What qualifies as stale
    """
    from app.services.live_odds_service import check_odds_freshness
    from app.schemas.public import OddsFreshnessResponse
    
    try:
        result = await check_odds_freshness(db, sport_id=sport_id)
        return result
        
    except Exception as e:
        logger.error(f"Odds health check error: {e}", exc_info=True)
        return {
            "status": "unknown",
            "total_lines": 0,
            "fresh_lines": 0,
            "stale_lines": 0,
            "freshness_pct": 0,
            "oldest_update": None,
            "newest_update": None,
            "stale_threshold_minutes": 5,
            "checked_at": datetime.utcnow().isoformat(),
        }


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
    
    VALID_SPORTS = ["basketball_nba", "basketball_ncaab", "americanfootball_nfl", "baseball_mlb", "tennis_atp", "tennis_wta"]
    
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
