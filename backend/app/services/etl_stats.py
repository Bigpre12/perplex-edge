"""ETL for syncing player statistics from stats providers."""

import logging
from datetime import datetime, date, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Sport, Player, Game, Line, PlayerGameStats
from app.services.stats_provider import StatsProvider, GameLog

logger = logging.getLogger(__name__)


# =============================================================================
# Sport Key Mappings
# =============================================================================

SPORT_KEY_TO_LEAGUE = {
    "basketball_nba": "NBA",
    "americanfootball_nfl": "NFL",
    "baseball_mlb": "MLB",
    "icehockey_nhl": "NHL",
    "basketball_ncaab": "NCAAB",
    "americanfootball_ncaaf": "NCAAF",
}


# =============================================================================
# Query Helpers
# =============================================================================

async def get_players_with_lines_today(
    db: AsyncSession,
    sport_id: int,
    target_date: Optional[date] = None,
) -> list[Player]:
    """
    Get all players who have betting lines for games today.
    
    Args:
        db: Database session
        sport_id: Sport ID to filter by
        target_date: Date to check (defaults to today)
    
    Returns:
        List of Player objects with lines today
    """
    target_date = target_date or date.today()
    
    # Calculate start and end of day (naive datetime for PostgreSQL)
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = day_start + timedelta(days=1)
    
    # Query players with active lines on games today
    result = await db.execute(
        select(Player)
        .distinct()
        .join(Line, Line.player_id == Player.id)
        .join(Game, Game.id == Line.game_id)
        .where(
            and_(
                Player.sport_id == sport_id,
                Line.is_current == True,
                Line.player_id.isnot(None),
                Game.start_time >= day_start,
                Game.start_time < day_end,
            )
        )
    )
    
    return list(result.scalars().all())


async def get_all_active_players(
    db: AsyncSession,
    sport_id: int,
    days_back: int = 7,
) -> list[Player]:
    """
    Get all players who have had lines in the last N days.
    
    Args:
        db: Database session
        sport_id: Sport ID to filter by
        days_back: Number of days to look back
    
    Returns:
        List of active Player objects
    """
    # Use naive datetime for TIMESTAMP WITHOUT TIME ZONE column comparison
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days_back)).replace(tzinfo=None)
    
    result = await db.execute(
        select(Player)
        .distinct()
        .join(Line, Line.player_id == Player.id)
        .where(
            and_(
                Player.sport_id == sport_id,
                Line.player_id.isnot(None),
                Line.fetched_at >= cutoff,
            )
        )
    )
    
    return list(result.scalars().all())


# =============================================================================
# Stats Sync Helpers
# =============================================================================

async def upsert_player_game_stat(
    db: AsyncSession,
    player_id: int,
    game_id: int,
    stat_type: str,
    value: float,
    minutes: Optional[float] = None,
) -> tuple[PlayerGameStats, bool]:
    """
    Upsert a player game stat record.
    
    Returns:
        Tuple of (PlayerGameStats, created) where created is True if new record
    """
    # Check if stat already exists
    result = await db.execute(
        select(PlayerGameStats).where(
            PlayerGameStats.player_id == player_id,
            PlayerGameStats.game_id == game_id,
            PlayerGameStats.stat_type == stat_type,
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update if value changed
        if existing.value != value:
            existing.value = value
            if minutes is not None:
                existing.minutes = minutes
        return existing, False
    
    # Create new stat
    stat = PlayerGameStats(
        player_id=player_id,
        game_id=game_id,
        stat_type=stat_type,
        value=value,
        minutes=minutes,
    )
    db.add(stat)
    return stat, True


async def find_game_by_external_id(
    db: AsyncSession,
    external_game_id: str,
) -> Optional[Game]:
    """Find a game by its external ID."""
    result = await db.execute(
        select(Game).where(Game.external_game_id == external_game_id)
    )
    return result.scalar_one_or_none()


async def find_game_by_date_approx(
    db: AsyncSession,
    sport_id: int,
    game_date: datetime,
    player_id: int,
) -> Optional[Game]:
    """
    Find a game by approximate date for a player.
    
    Used when we don't have an exact external_game_id match.
    """
    # Convert timezone-aware datetime to naive (UTC) for PostgreSQL
    if game_date.tzinfo is not None:
        game_date = game_date.replace(tzinfo=None)
    
    # Look for games within 1 day of the date
    day_start = game_date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    
    # Get player's team
    result = await db.execute(
        select(Player).where(Player.id == player_id)
    )
    player = result.scalar_one_or_none()
    
    if not player or not player.team_id:
        return None
    
    # Find game for player's team on that date
    result = await db.execute(
        select(Game).where(
            and_(
                Game.sport_id == sport_id,
                Game.start_time >= day_start,
                Game.start_time < day_end,
                (Game.home_team_id == player.team_id) | (Game.away_team_id == player.team_id),
            )
        )
    )
    return result.scalar_one_or_none()


# =============================================================================
# Main ETL Function
# =============================================================================

async def sync_recent_player_stats(
    db: AsyncSession,
    sport_key: str,
    games_back: int = 10,
    only_players_with_lines_today: bool = True,
    use_stubs: bool = False,
) -> dict[str, Any]:
    """
    Sync recent player statistics for a sport.
    
    This function is idempotent:
    - Stats are upserted by (player_id, game_id, stat_type)
    - Existing stats are updated if values changed
    
    Args:
        db: Database session
        sport_key: Sport identifier (e.g., 'basketball_nba')
        games_back: Number of recent games to fetch per player
        only_players_with_lines_today: If True, only sync players with lines today
        use_stubs: Use stub data instead of real API calls
    
    Returns:
        Dictionary with sync statistics
    """
    stats = {
        "sport": None,
        "players_processed": 0,
        "stats_created": 0,
        "stats_updated": 0,
        "stats_skipped": 0,
        "games_not_found": 0,
        "errors": [],
    }
    
    try:
        # Get sport
        league_code = SPORT_KEY_TO_LEAGUE.get(sport_key, sport_key.upper())
        result = await db.execute(
            select(Sport).where(Sport.league_code == league_code)
        )
        sport = result.scalar_one_or_none()
        
        if not sport:
            logger.warning(f"Sport not found: {league_code}")
            return {"error": f"Sport not found: {league_code}"}
        
        stats["sport"] = sport.league_code
        
        # Get players to process
        if only_players_with_lines_today:
            players = await get_players_with_lines_today(db, sport.id)
            logger.info(f"Found {len(players)} players with lines today for {sport_key}")
        else:
            players = await get_all_active_players(db, sport.id)
            logger.info(f"Found {len(players)} active players for {sport_key}")
        
        if not players:
            logger.info(f"No players to process for {sport_key}")
            return stats
        
        async with StatsProvider(use_stubs=use_stubs) as provider:
            for player in players:
                try:
                    # Fetch game logs
                    game_logs = await provider.fetch_player_game_logs(
                        player.external_player_id,
                        n_games=games_back,
                    )
                    
                    for log in game_logs:
                        # Try to find the game in our database
                        game = await find_game_by_external_id(db, log.external_game_id)
                        
                        if not game:
                            # Try to find by date
                            game = await find_game_by_date_approx(
                                db,
                                sport.id,
                                log.game_date,
                                player.id,
                            )
                        
                        if not game:
                            stats["games_not_found"] += 1
                            continue
                        
                        # Upsert each stat
                        for stat_type, value in log.stats.items():
                            stat, created = await upsert_player_game_stat(
                                db,
                                player.id,
                                game.id,
                                stat_type,
                                value,
                                minutes=log.minutes,
                            )
                            
                            if created:
                                stats["stats_created"] += 1
                            else:
                                stats["stats_updated"] += 1
                    
                    stats["players_processed"] += 1
                
                except Exception as e:
                    logger.error(f"Error processing player {player.name}: {e}")
                    stats["errors"].append(f"{player.name}: {str(e)}")
        
        # Commit transaction
        await db.commit()
        logger.info(f"Stats sync completed for {sport_key}: {stats}")
        return stats
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Stats ETL failed for {sport_key}: {e}")
        raise


# =============================================================================
# Alternative Sync Functions
# =============================================================================

async def sync_player_stats_by_days(
    db: AsyncSession,
    sport_key: str,
    days_back: int = 7,
    use_stubs: bool = False,
) -> dict[str, Any]:
    """
    Sync player stats for all players active in the last N days.
    
    Args:
        db: Database session
        sport_key: Sport identifier
        days_back: Number of days to look back for active players
        use_stubs: Use stub data
    
    Returns:
        Dictionary with sync statistics
    """
    # Calculate approximate games from days (assuming ~1 game every 2-3 days)
    games_back = max(5, days_back // 2)
    
    return await sync_recent_player_stats(
        db,
        sport_key,
        games_back=games_back,
        only_players_with_lines_today=False,
        use_stubs=use_stubs,
    )


async def sync_single_player_stats(
    db: AsyncSession,
    player_id: int,
    games_back: int = 10,
    use_stubs: bool = False,
) -> dict[str, Any]:
    """
    Sync stats for a single player.
    
    Args:
        db: Database session
        player_id: Internal player ID
        games_back: Number of games to fetch
        use_stubs: Use stub data
    
    Returns:
        Dictionary with sync statistics
    """
    stats = {
        "player_id": player_id,
        "stats_created": 0,
        "stats_updated": 0,
        "games_not_found": 0,
    }
    
    try:
        # Get player
        result = await db.execute(
            select(Player).where(Player.id == player_id)
        )
        player = result.scalar_one_or_none()
        
        if not player:
            return {"error": f"Player not found: {player_id}"}
        
        async with StatsProvider(use_stubs=use_stubs) as provider:
            game_logs = await provider.fetch_player_game_logs(
                player.external_player_id,
                n_games=games_back,
            )
            
            for log in game_logs:
                game = await find_game_by_external_id(db, log.external_game_id)
                
                if not game:
                    game = await find_game_by_date_approx(
                        db,
                        player.sport_id,
                        log.game_date,
                        player.id,
                    )
                
                if not game:
                    stats["games_not_found"] += 1
                    continue
                
                for stat_type, value in log.stats.items():
                    stat, created = await upsert_player_game_stat(
                        db,
                        player.id,
                        game.id,
                        stat_type,
                        value,
                        minutes=log.minutes,
                    )
                    
                    if created:
                        stats["stats_created"] += 1
                    else:
                        stats["stats_updated"] += 1
        
        await db.commit()
        return stats
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Stats sync failed for player {player_id}: {e}")
        raise
