"""Seasons API routes for accessing season, team, player, and game data."""

import logging
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import (
    Season, SeasonRoster, Sport, Team, Player, Game, PlayerGameStats,
)
from app.schemas.season import (
    SeasonRead, SeasonList,
    TeamInfo, PlayerInfo, RosterPlayerOut,
    GameOut, GamePlayerStats, GamePlayerOut,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# =============================================================================
# Season Endpoints
# =============================================================================

@router.get("/seasons", response_model=SeasonList, tags=["seasons"])
async def list_seasons(
    sport_id: int = Query(..., description="Sport ID (e.g., 30=NBA, 31=NFL)"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all seasons for a sport.
    
    Returns seasons ordered by year descending (most recent first).
    """
    # Build query
    query = (
        select(Season)
        .where(Season.sport_id == sport_id)
        .order_by(Season.season_year.desc())
    )
    
    # Execute
    result = await db.execute(query)
    seasons = result.scalars().all()
    
    return SeasonList(
        items=[SeasonRead.model_validate(s) for s in seasons],
        total=len(seasons),
    )

@router.get("/seasons/current", response_model=Optional[SeasonRead], tags=["seasons"])
async def get_current_season(
    sport_id: int = Query(..., description="Sport ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the current active season for a sport.
    
    Returns the season marked as is_current=True, or None if no current season.
    """
    query = (
        select(Season)
        .where(and_(
            Season.sport_id == sport_id,
            Season.is_current == True,
        ))
    )
    
    result = await db.execute(query)
    season = result.scalar_one_or_none()
    
    if not season:
        return None
    
    return SeasonRead.model_validate(season)

# =============================================================================
# Team Endpoints
# =============================================================================

@router.get("/sports/{sport_id}/teams", response_model=List[TeamInfo], tags=["seasons"])
async def list_teams_for_season(
    sport_id: int,
    season_year: Optional[int] = Query(None,
        description="Season year (e.g.,
        2026). If not provided,
        returns all teams."),
    db: AsyncSession = Depends(get_db),
):
    """
    List teams for a sport, optionally filtered by season.
    
    If season_year is provided, returns only teams that have roster entries
    for that season. Otherwise, returns all teams for the sport.
    """
    if season_year:
        # Get teams that have roster entries for this season
        query = (
            select(Team)
            .distinct()
            .join(SeasonRoster, SeasonRoster.team_id == Team.id)
            .join(Season, Season.id == SeasonRoster.season_id)
            .where(and_(
                Team.sport_id == sport_id,
                Season.season_year == season_year,
            ))
            .order_by(Team.name)
        )
    else:
        # Get all teams for the sport
        query = (
            select(Team)
            .where(Team.sport_id == sport_id)
            .order_by(Team.name)
        )
    
    result = await db.execute(query)
    teams = result.scalars().all()
    
    return [TeamInfo.model_validate(t) for t in teams]

# =============================================================================
# Roster Endpoints
# =============================================================================

@router.get(
    "/sports/{sport_id}/teams/{team_id}/roster",
    response_model=List[RosterPlayerOut],
    tags=["seasons"],
)
async def list_team_roster(
    sport_id: int,
    team_id: int,
    season_year: int = Query(..., description="Season year (e.g., 2026)"),
    active_only: bool = Query(True, description="Only return active players"),
    db: AsyncSession = Depends(get_db),
):
    """
    List players on a team's roster for a specific season.
    
    Returns player info with jersey number and position for the season.
    """
    # Verify team exists and belongs to sport
    team = await db.get(Team, team_id)
    if not team or team.sport_id != sport_id:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Build query
    conditions = [
        SeasonRoster.team_id == team_id,
        Season.season_year == season_year,
    ]
    if active_only:
        conditions.append(SeasonRoster.is_active == True)
    
    query = (
        select(SeasonRoster, Player)
        .join(Season, Season.id == SeasonRoster.season_id)
        .join(Player, Player.id == SeasonRoster.player_id)
        .where(and_(*conditions))
        .order_by(Player.name)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        RosterPlayerOut(
            id=player.id,
            name=player.name,
            position=roster.position or player.position,
            jersey_number=roster.jersey_number,
            is_active=roster.is_active,
        )
        for roster, player in rows
    ]

# =============================================================================
# Game Endpoints
# =============================================================================

@router.get(
    "/sports/{sport_id}/games",
    response_model=List[GameOut],
    tags=["seasons"],
)
async def list_games_for_date(
    sport_id: int,
    game_date: date = Query(..., alias="date", description="Game date (YYYY-MM-DD)"),
    season_year: Optional[int] = Query(None, description="Season year filter"),
    db: AsyncSession = Depends(get_db),
):
    """
    List games for a sport on a specific date.
    
    Optionally filter by season_year to only get games from that season.
    """
    from datetime import datetime, timezone, timedelta
    
    # Calculate date range (full day in UTC)
    start_of_day = datetime.combine(game_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_of_day = start_of_day + timedelta(days=1)
    
    # Build conditions
    conditions = [
        Game.sport_id == sport_id,
        Game.start_time >= start_of_day,
        Game.start_time < end_of_day,
    ]
    
    if season_year:
        # Join with season to filter by year
        query = (
            select(Game)
            .options(
                selectinload(Game.home_team),
                selectinload(Game.away_team),
            )
            .join(Season, Season.id == Game.season_id)
            .where(and_(*conditions, Season.season_year == season_year))
            .order_by(Game.start_time)
        )
    else:
        query = (
            select(Game)
            .options(
                selectinload(Game.home_team),
                selectinload(Game.away_team),
            )
            .where(and_(*conditions))
            .order_by(Game.start_time)
        )
    
    result = await db.execute(query)
    games = result.scalars().all()
    
    return [
        GameOut(
            id=g.id,
            sport_id=g.sport_id,
            season_id=g.season_id,
            home_team=TeamInfo.model_validate(g.home_team),
            away_team=TeamInfo.model_validate(g.away_team),
            start_time=g.start_time,
            status=g.status,
        )
        for g in games
    ]

# =============================================================================
# Game Stats Endpoints
# =============================================================================

@router.get(
    "/games/{game_id}/stats",
    response_model=List[GamePlayerOut],
    tags=["seasons"],
)
async def list_game_player_stats(
    game_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all player stats for a game.
    
    Returns players with their stats for the specified game.
    Stats fields vary by sport (basketball has points/rebounds/assists,
    football has passing/rushing yards, etc.)
    """
    # Verify game exists
    game = await db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Get all player game stats
    query = (
        select(PlayerGameStats, Player, Team)
        .join(Player, Player.id == PlayerGameStats.player_id)
        .join(Team, Team.id == Player.team_id)
        .where(PlayerGameStats.game_id == game_id)
        .order_by(Player.name)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    # Group stats by player
    player_stats: dict = {}
    for stats, player, team in rows:
        if player.id not in player_stats:
            player_stats[player.id] = {
                "player": player,
                "team": team,
                "stats": {},
            }
        # Add this stat type
        player_stats[player.id]["stats"][stats.stat_type] = stats.value
        if stats.minutes:
            player_stats[player.id]["stats"]["minutes"] = stats.minutes
    
    # Convert to response format
    results = []
    for data in player_stats.values():
        stats = data["stats"]
        results.append(
            GamePlayerOut(
                player=PlayerInfo(
                    id=data["player"].id,
                    sport_id=data["player"].sport_id,
                    team_id=data["player"].team_id,
                    name=data["player"].name,
                    position=data["player"].position,
                ),
                team=TeamInfo(
                    id=data["team"].id,
                    sport_id=data["team"].sport_id,
                    name=data["team"].name,
                    abbreviation=data["team"].abbreviation,
                ),
                stats=GamePlayerStats(
                    minutes=stats.get("minutes"),
                    points=stats.get("points") or stats.get("PTS"),
                    rebounds=stats.get("rebounds") or stats.get("REB"),
                    assists=stats.get("assists") or stats.get("AST"),
                    steals=stats.get("steals") or stats.get("STL"),
                    blocks=stats.get("blocks") or stats.get("BLK"),
                    turnovers=stats.get("turnovers") or stats.get("TO"),
                    three_pointers_made=stats.get("three_pointers_made") or stats.get("3PM"),
                    passing_yards=stats.get("passing_yards") or stats.get("PASS_YDS"),
                    passing_touchdowns=stats.get("passing_touchdowns") or stats.get("PASS_TD"),
                    rushing_yards=stats.get("rushing_yards") or stats.get("RUSH_YDS"),
                    rushing_touchdowns=stats.get("rushing_touchdowns") or stats.get("RUSH_TD"),
                    receiving_yards=stats.get("receiving_yards") or stats.get("REC_YDS"),
                    receptions=stats.get("receptions") or stats.get("REC"),
                    goals=stats.get("goals"),
                    assists_hockey=stats.get("assists_hockey"),
                    shots=stats.get("shots"),
                    saves=stats.get("saves"),
                    hits=stats.get("hits"),
                    runs=stats.get("runs"),
                    rbis=stats.get("rbis") or stats.get("RBI"),
                    strikeouts=stats.get("strikeouts") or stats.get("K"),
                    innings_pitched=stats.get("innings_pitched") or stats.get("IP"),
                ),
            )
        )
    
    return results

# =============================================================================
# Player Endpoints
# =============================================================================

@router.get(
    "/sports/{sport_id}/players",
    response_model=List[PlayerInfo],
    tags=["seasons"],
)
async def list_players_for_sport(
    sport_id: int,
    team_id: Optional[int] = Query(None, description="Filter by team"),
    season_year: Optional[int] = Query(None, description="Filter by season roster"),
    limit: int = Query(100, ge=1, le=200, description="Max results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
):
    """
    List players for a sport, optionally filtered by team and/or season.
    """
    if season_year:
        # Filter by season roster
        conditions = [
            Player.sport_id == sport_id,
            Season.season_year == season_year,
        ]
        if team_id:
            conditions.append(SeasonRoster.team_id == team_id)
        
        query = (
            select(Player)
            .distinct()
            .join(SeasonRoster, SeasonRoster.player_id == Player.id)
            .join(Season, Season.id == SeasonRoster.season_id)
            .where(and_(*conditions))
            .order_by(Player.name)
            .offset(offset)
            .limit(limit)
        )
    else:
        # No season filter
        conditions = [Player.sport_id == sport_id]
        if team_id:
            conditions.append(Player.team_id == team_id)
        
        query = (
            select(Player)
            .where(and_(*conditions))
            .order_by(Player.name)
            .offset(offset)
            .limit(limit)
        )
    
    result = await db.execute(query)
    players = result.scalars().all()
    
    return [PlayerInfo.model_validate(p) for p in players]
