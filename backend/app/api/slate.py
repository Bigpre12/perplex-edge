"""Full Slate API endpoints for multi-sport prop review."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.database import get_db
from app.core.constants import SPORT_ID_TO_KEY
from app.config.sports import SPORT_ID_TO_KEY as SPORT_ID_TO_KEY_ENUM, SPORT_KEY_TO_ID
from app.models import Sport, Team, Game, Market, Player, ModelPick, Line, Injury
from app.models.injury import EXCLUDED_INJURY_STATUSES
from app.schemas.public import PlayerPropPick, BookLine
from app.services.prop_filters import dedupe_player_props
from app.services.parlay_service import calculate_kelly_fraction

router = APIRouter()
logger = logging.getLogger(__name__)

# Eastern timezone (handles DST automatically)
EASTERN_TZ = ZoneInfo("America/New_York")

# Sport IDs to include in full slate (active sports with player props)
SLATE_SPORT_IDS = [30, 32, 31, 41, 40, 53, 42, 43]  # NBA, NCAAB, NFL, NCAAF, MLB, NHL, ATP, WTA


# =============================================================================
# Schemas
# =============================================================================

class SportSlate(BaseModel):
    """Props for a single sport on a date."""
    sport_id: int
    sport_key: str
    sport_name: str
    date: str
    count: int
    props: list[PlayerPropPick]


class FullSlateResponse(BaseModel):
    """Full slate response with props grouped by sport."""
    date: str
    total_props: int
    sports: list[SportSlate]


# =============================================================================
# Helper Functions
# =============================================================================

def calculate_ev_for_odds(model_prob: float, odds: int) -> float:
    """Calculate EV for given model probability and American odds."""
    if odds < 0:
        profit = 100 / abs(odds)
    else:
        profit = odds / 100
    
    ev = (model_prob * profit) - ((1 - model_prob) * 1)
    return round(ev, 4)


async def get_props_for_sport(
    db: AsyncSession,
    sport_id: int,
    target_date: datetime,
    min_ev: float = 0.0,
    min_confidence: float = 0.0,
    limit: int = 50,
) -> list[PlayerPropPick]:
    """
    Fetch player props for a specific sport and date.
    
    Reuses the core query logic from the /picks/player-props endpoint.
    """
    # Verify sport exists
    sport = await db.get(Sport, sport_id)
    if not sport:
        return []
    
    # Calculate date boundaries for the target date
    target_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    target_end = target_start + timedelta(days=1)
    
    # Convert to UTC naive for DB comparison
    target_start_utc = target_start.astimezone(timezone.utc).replace(tzinfo=None)
    target_end_utc = target_end.astimezone(timezone.utc).replace(tzinfo=None)
    
    # Aliases for team joins
    PlayerTeam = aliased(Team)
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)
    
    # Subquery to find injured player IDs
    injured_subquery = (
        select(Injury.player_id)
        .where(Injury.status.in_(EXCLUDED_INJURY_STATUSES))
        .scalar_subquery()
    )
    
    # Base filter conditions for the target date
    base_conditions = [
        ModelPick.sport_id == sport_id,
        Game.sport_id == sport_id,
        ModelPick.player_id.isnot(None),
        ModelPick.player_id.notin_(injured_subquery),
        Game.start_time >= target_start_utc,
        Game.start_time < target_end_utc,
    ]
    
    # Build query
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
    
    # Apply EV and confidence filters
    if min_ev > 0:
        query = query.where(ModelPick.expected_value >= min_ev)
    
    if min_confidence > 0:
        query = query.where(ModelPick.confidence_score >= min_confidence)
    
    # Order by EV descending
    query = query.order_by(ModelPick.expected_value.desc()).limit(limit * 2)  # Fetch extra for deduping
    
    result = await db.execute(query)
    rows = result.all()
    
    if not rows:
        return []
    
    # Dedupe by (player, stat, line)
    seen_props: dict = {}
    for row in rows:
        pick, player, player_team, game, home_team, away_team, market = row
        
        if pick.line_value is None or pick.line_value == 0:
            continue
        
        key = (player.id, market.stat_type, pick.line_value)
        ev = pick.expected_value or 0.0
        
        if key not in seen_props or ev > (seen_props[key][0].expected_value or 0.0):
            seen_props[key] = row
    
    deduped_rows = list(seen_props.values())[:limit]
    
    # Bulk fetch book lines
    line_keys = set()
    for row in deduped_rows:
        pick, player, player_team, game, home_team, away_team, market = row
        if pick.line_value is not None and pick.line_value != 0:
            line_keys.add((game.id, player.id, market.id, pick.side))
    
    book_lines_map: dict[tuple, list] = {}
    if line_keys:
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
        
        for line in all_lines:
            key = (line.game_id, line.player_id, line.market_id, line.side)
            if key not in book_lines_map:
                book_lines_map[key] = []
            book_lines_map[key].append(line)
    
    # Build response
    picks = []
    for row in deduped_rows:
        pick, player, player_team, game, home_team, away_team, market = row
        
        if pick.line_value is None or pick.line_value == 0:
            continue
        
        # Handle player team
        if player_team is not None:
            team_name = player_team.name
            team_abbr = player_team.abbreviation
            if player_team.id == home_team.id:
                opponent_team = away_team.name
                opponent_abbr = away_team.abbreviation
            else:
                opponent_team = home_team.name
                opponent_abbr = home_team.abbreviation
        else:
            team_name = "Unknown"
            team_abbr = "UNK"
            opponent_team = f"{away_team.name} vs {home_team.name}"
            opponent_abbr = f"{away_team.abbreviation} vs {home_team.abbreviation}"
        
        # Get book lines from cache
        line_key = (game.id, player.id, market.id, pick.side)
        cached_lines = book_lines_map.get(line_key, [])
        
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
        
        # Calculate Kelly sizing
        kelly = calculate_kelly_fraction(
            win_prob=pick.model_probability,
            american_odds=int(pick.odds),
        )
        
        # Get sport_key
        pick_sport_key = SPORT_ID_TO_KEY.get(pick.sport_id, f"unknown_{pick.sport_id}")
        
        picks.append(PlayerPropPick(
            pick_id=pick.id,
            sport_id=pick.sport_id,
            sport_key=pick_sport_key,
            player_name=player.name,
            player_id=player.id,
            team=team_name,
            team_abbr=team_abbr,
            opponent_team=opponent_team,
            opponent_abbr=opponent_abbr,
            stat_type=market.stat_type or "",
            line=pick.line_value,
            side=pick.side,
            odds=int(pick.odds),
            sportsbook=None,  # Will be set from book_lines
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
            book_lines=book_lines if book_lines else None,
            best_book=best_book,
            line_variance=line_variance,
            kelly_units=kelly["suggested_units"],
            kelly_edge_pct=kelly["edge_pct"],
            kelly_risk_level=kelly["risk_level"],
            opening_line=None,
            opening_odds=None,
            line_movement=None,
            odds_movement=None,
            movement_direction=None,
        ))
    
    # Final dedupe
    picks = dedupe_player_props(picks)
    
    return picks


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/slate/full", response_model=FullSlateResponse, tags=["slate"])
async def get_full_slate(
    date: str = Query(..., description="ISO date, e.g. 2026-02-04"),
    min_ev: float = Query(0.0, description="Minimum expected value"),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="Minimum confidence score"),
    limit_per_sport: int = Query(50, ge=1, le=100, description="Max props per sport"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get full slate of player props across all sports for a specific date.
    
    Returns props grouped by sport with full details including:
    - Model probability and EV
    - Kelly sizing recommendations
    - Per-book line comparison
    - Hit rates
    
    Useful for reviewing tomorrow's entire slate across NBA, NFL, NCAAB, etc.
    """
    # Parse date
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=EASTERN_TZ)
    except ValueError:
        # Try alternate formats
        try:
            target_date = datetime.fromisoformat(date).replace(tzinfo=EASTERN_TZ)
        except ValueError:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Invalid date format: {date}. Use YYYY-MM-DD.")
    
    # Get all sports for name lookup
    sports_result = await db.execute(select(Sport))
    all_sports = {s.id: s for s in sports_result.scalars().all()}
    
    # Fetch props for each sport
    sports_slates: list[SportSlate] = []
    total_props = 0
    
    for sport_id in SLATE_SPORT_IDS:
        sport = all_sports.get(sport_id)
        if not sport:
            continue
        
        props = await get_props_for_sport(
            db=db,
            sport_id=sport_id,
            target_date=target_date,
            min_ev=min_ev,
            min_confidence=min_confidence,
            limit=limit_per_sport,
        )
        
        sport_key = SPORT_ID_TO_KEY.get(sport_id, f"unknown_{sport_id}")
        
        sports_slates.append(SportSlate(
            sport_id=sport_id,
            sport_key=sport_key,
            sport_name=sport.name,
            date=date,
            count=len(props),
            props=props,
        ))
        
        total_props += len(props)
        
        logger.info(f"[slate] Fetched {len(props)} props for sport_id={sport_id} ({sport.name}) on {date}")
    
    # Sort by prop count (sports with most props first)
    sports_slates.sort(key=lambda s: s.count, reverse=True)
    
    logger.info(f"[slate] Full slate for {date}: {total_props} total props across {len(sports_slates)} sports")
    
    return FullSlateResponse(
        date=date,
        total_props=total_props,
        sports=sports_slates,
    )
