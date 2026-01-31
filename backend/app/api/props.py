"""Player Props API endpoints."""

from datetime import datetime, timezone, timedelta
from typing import Optional, List
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from app.core.database import get_db
from app.models import Line, Game, Market, Player, Sport, Team, ModelPick, Injury
from app.models.injury import EXCLUDED_INJURY_STATUSES
from app.schemas.line import LineList, LineRead, LineComparison, BookmakerLine

router = APIRouter()

EASTERN_TZ = ZoneInfo("America/New_York")


# =============================================================================
# Search Response Schema
# =============================================================================

class PropSearchResult(BaseModel):
    """Single prop search result with all details."""
    
    # Prop identification
    line_id: int
    pick_id: Optional[int] = None
    
    # Player info
    player_id: int
    player_name: str
    team: Optional[str] = None
    team_abbr: Optional[str] = None
    position: Optional[str] = None
    
    # Game info
    game_id: int
    opponent: Optional[str] = None
    opponent_abbr: Optional[str] = None
    game_start_time: datetime
    
    # Prop details
    stat_type: str
    line: float
    side: str
    odds: int
    sportsbook: str
    
    # Model analysis (if pick exists)
    model_probability: Optional[float] = None
    implied_probability: Optional[float] = None
    expected_value: Optional[float] = None
    edge: Optional[float] = None
    confidence_score: Optional[float] = None
    
    # Hit rates
    hit_rate_season: Optional[float] = None
    hit_rate_10g: Optional[float] = None
    hit_rate_5g: Optional[float] = None
    is_100_pct_5g: bool = False
    
    # Injury status
    injury_status: Optional[str] = None
    is_injured: bool = False
    
    # Kelly sizing
    kelly_units: Optional[float] = None
    kelly_risk_level: Optional[str] = None


class PropSearchResponse(BaseModel):
    """Paginated prop search response."""
    items: List[PropSearchResult]
    total: int
    page: int
    per_page: int
    filters_applied: dict


# =============================================================================
# Props Search Endpoint
# =============================================================================

@router.get("/search", response_model=PropSearchResponse)
async def search_props(
    # Text filters
    player: Optional[str] = Query(None, description="Search by player name (partial match)"),
    team: Optional[str] = Query(None, description="Filter by team name or abbreviation"),
    
    # Prop filters
    stat_type: Optional[str] = Query(None, description="Filter by stat type (PTS, REB, AST, 3PM, PRA)"),
    side: Optional[str] = Query(None, description="Filter by side (over, under)"),
    sportsbook: Optional[str] = Query(None, description="Filter by sportsbook"),
    sport: Optional[str] = Query(None, description="Filter by sport key (basketball_nba, basketball_ncaab)"),
    
    # Model filters
    min_edge: Optional[float] = Query(None, description="Minimum edge percentage (e.g., 0.03 for 3%)"),
    min_ev: Optional[float] = Query(None, description="Minimum expected value"),
    min_confidence: Optional[float] = Query(None, ge=0, le=1, description="Minimum confidence score (0-1)"),
    
    # Hit rate filters
    min_hit_rate_5g: Optional[float] = Query(None, ge=0, le=1, description="Minimum hit rate over last 5 games"),
    only_100_pct: bool = Query(False, description="Only show 100% hit rate props"),
    
    # Status filters
    include_injured: bool = Query(False, description="Include injured players"),
    fresh_only: bool = Query(True, description="Only show props for games not yet started"),
    
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=200, description="Results per page"),
    
    # Sorting
    sort_by: str = Query("ev", description="Sort by: ev, edge, odds, hit_rate, line, game_time"),
    sort_desc: bool = Query(True, description="Sort descending"),
    
    db: AsyncSession = Depends(get_db),
):
    """
    Comprehensive prop search with filtering, sorting, and model analysis.
    
    Returns props with:
    - Player and game details
    - Model probability and EV
    - Hit rates (season, 10g, 5g)
    - Injury status
    - Kelly sizing recommendation
    
    Filter by:
    - Player name, team, sport
    - Stat type, side, sportsbook
    - Minimum edge, EV, confidence
    - Hit rate thresholds
    - Injury status
    """
    from app.services.parlay_service import calculate_kelly_fraction
    
    # Aliases for joins
    PlayerTeam = aliased(Team)
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)
    
    # Current time for freshness filtering
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Build base query
    query = (
        select(Line, Player, PlayerTeam, Game, HomeTeam, AwayTeam, Market, ModelPick)
        .join(Player, Line.player_id == Player.id)
        .outerjoin(PlayerTeam, Player.team_id == PlayerTeam.id)
        .join(Game, Line.game_id == Game.id)
        .join(HomeTeam, Game.home_team_id == HomeTeam.id)
        .join(AwayTeam, Game.away_team_id == AwayTeam.id)
        .join(Market, Line.market_id == Market.id)
        .outerjoin(
            ModelPick,
            and_(
                ModelPick.game_id == Line.game_id,
                ModelPick.player_id == Line.player_id,
                ModelPick.market_id == Line.market_id,
                ModelPick.side == Line.side,
                ModelPick.is_active == True,
            )
        )
        .where(
            Line.is_current == True,
            Line.player_id.isnot(None),
        )
    )
    
    # Apply filters
    if player:
        query = query.where(Player.name.ilike(f"%{player}%"))
    
    if team:
        query = query.where(
            or_(
                PlayerTeam.name.ilike(f"%{team}%"),
                PlayerTeam.abbreviation.ilike(f"%{team}%"),
            )
        )
    
    if stat_type:
        query = query.where(Market.stat_type == stat_type.upper())
    
    if side:
        query = query.where(Line.side == side.lower())
    
    if sportsbook:
        query = query.where(Line.sportsbook.ilike(f"%{sportsbook}%"))
    
    if sport:
        sport_result = await db.execute(
            select(Sport).where(Sport.key == sport)
        )
        sport_obj = sport_result.scalar_one_or_none()
        if sport_obj:
            query = query.where(Game.sport_id == sport_obj.id)
    
    if min_edge is not None:
        query = query.where(ModelPick.expected_value >= min_edge)
    
    if min_ev is not None:
        query = query.where(ModelPick.expected_value >= min_ev)
    
    if min_confidence is not None:
        query = query.where(ModelPick.confidence_score >= min_confidence)
    
    if min_hit_rate_5g is not None:
        query = query.where(ModelPick.hit_rate_5g >= min_hit_rate_5g)
    
    if only_100_pct:
        # 100% hit rate over 5 games means hit_rate_5g = 1.0 and games_5g >= 3
        query = query.where(ModelPick.hit_rate_5g >= 0.999)
    
    if fresh_only:
        query = query.where(Game.start_time > now)
    
    # Exclude injured players unless requested
    if not include_injured:
        injured_subquery = (
            select(Injury.player_id)
            .where(Injury.status.in_(EXCLUDED_INJURY_STATUSES))
            .scalar_subquery()
        )
        query = query.where(Player.id.notin_(injured_subquery))
    
    # Get total count
    count_subquery = query.with_only_columns(func.count()).order_by(None)
    total_result = await db.execute(count_subquery)
    total = total_result.scalar() or 0
    
    # Apply sorting
    if sort_by == "ev":
        order_col = ModelPick.expected_value
    elif sort_by == "edge":
        order_col = ModelPick.expected_value
    elif sort_by == "odds":
        order_col = Line.odds
    elif sort_by == "hit_rate":
        order_col = ModelPick.hit_rate_5g
    elif sort_by == "line":
        order_col = Line.line_value
    elif sort_by == "game_time":
        order_col = Game.start_time
    else:
        order_col = ModelPick.expected_value
    
    if sort_desc:
        query = query.order_by(order_col.desc().nullslast())
    else:
        query = query.order_by(order_col.asc().nullsfirst())
    
    # Apply pagination
    offset = (page - 1) * per_page
    query = query.limit(per_page).offset(offset)
    
    # Execute query
    result = await db.execute(query)
    rows = result.all()
    
    # Build injury status lookup
    player_ids = [row[1].id for row in rows]
    injury_result = await db.execute(
        select(Injury)
        .where(Injury.player_id.in_(player_ids))
    )
    injury_map = {inj.player_id: inj for inj in injury_result.scalars().all()}
    
    # Build response
    items = []
    for line, player, player_team, game, home_team, away_team, market, pick in rows:
        # Determine opponent
        if player_team and player_team.id == home_team.id:
            opponent = away_team.name
            opponent_abbr = away_team.abbreviation
        elif player_team and player_team.id == away_team.id:
            opponent = home_team.name
            opponent_abbr = home_team.abbreviation
        else:
            opponent = f"{away_team.abbreviation} @ {home_team.abbreviation}"
            opponent_abbr = None
        
        # Get injury status
        injury = injury_map.get(player.id)
        injury_status = injury.status if injury else None
        is_injured = injury_status in ["OUT", "DOUBTFUL", "GTD", "DAY_TO_DAY"] if injury_status else False
        
        # Calculate Kelly if we have a pick
        kelly_units = None
        kelly_risk_level = None
        if pick and pick.model_probability:
            kelly = calculate_kelly_fraction(
                win_prob=pick.model_probability,
                american_odds=int(line.odds),
            )
            kelly_units = kelly["suggested_units"]
            kelly_risk_level = kelly["risk_level"]
        
        # Calculate edge
        edge = None
        if pick:
            edge = pick.expected_value
        
        items.append(PropSearchResult(
            line_id=line.id,
            pick_id=pick.id if pick else None,
            player_id=player.id,
            player_name=player.name,
            team=player_team.name if player_team else None,
            team_abbr=player_team.abbreviation if player_team else None,
            position=player.position,
            game_id=game.id,
            opponent=opponent,
            opponent_abbr=opponent_abbr,
            game_start_time=game.start_time,
            stat_type=market.stat_type or "",
            line=line.line_value if line.line_value is not None else 0.0,  # Explicit null check
            side=line.side,
            odds=int(line.odds),
            sportsbook=line.sportsbook,
            model_probability=pick.model_probability if pick else None,
            implied_probability=pick.implied_probability if pick else None,
            expected_value=pick.expected_value if pick else None,
            edge=edge,
            confidence_score=pick.confidence_score if pick else None,
            hit_rate_season=pick.hit_rate_30d if pick else None,
            hit_rate_10g=pick.hit_rate_10g if pick else None,
            hit_rate_5g=pick.hit_rate_5g if pick else None,
            is_100_pct_5g=(pick.hit_rate_5g is not None and pick.hit_rate_5g >= 0.999) if pick else False,
            injury_status=injury_status,
            is_injured=is_injured,
            kelly_units=kelly_units,
            kelly_risk_level=kelly_risk_level,
        ))
    
    return PropSearchResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        filters_applied={
            "player": player,
            "team": team,
            "stat_type": stat_type,
            "side": side,
            "sportsbook": sportsbook,
            "sport": sport,
            "min_edge": min_edge,
            "min_ev": min_ev,
            "min_confidence": min_confidence,
            "min_hit_rate_5g": min_hit_rate_5g,
            "only_100_pct": only_100_pct,
            "include_injured": include_injured,
            "fresh_only": fresh_only,
            "sort_by": sort_by,
            "sort_desc": sort_desc,
        },
    )


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
