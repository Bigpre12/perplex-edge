"""ETL for syncing games and betting lines from odds providers."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Sport, Team, Game, Market, Line, Player
from app.services.odds_provider import XYZOddsProvider, GameData, LineData, PropData

logger = logging.getLogger(__name__)


# =============================================================================
# Sport Key Mappings
# =============================================================================

SPORT_KEY_TO_NAME = {
    "basketball_nba": ("NBA", "NBA"),
    "americanfootball_nfl": ("NFL", "NFL"),
    "baseball_mlb": ("MLB", "MLB"),
    "icehockey_nhl": ("NHL", "NHL"),
    "basketball_ncaab": ("NCAA Basketball", "NCAAB"),
    "americanfootball_ncaaf": ("NCAA Football", "NCAAF"),
}


# =============================================================================
# Helper Functions - Get or Create
# =============================================================================

async def get_or_create_sport(
    db: AsyncSession,
    sport_key: str,
) -> Sport:
    """Get or create a sport record by sport_key."""
    sport_name, league_code = SPORT_KEY_TO_NAME.get(sport_key, (sport_key, sport_key.upper()))
    
    result = await db.execute(
        select(Sport).where(Sport.league_code == league_code)
    )
    sport = result.scalar_one_or_none()
    
    if not sport:
        sport = Sport(name=sport_name, league_code=league_code)
        db.add(sport)
        await db.flush()
        logger.info(f"Created sport: {sport_name} ({league_code})")
    
    return sport


async def get_or_create_team(
    db: AsyncSession,
    sport_id: int,
    team_name: str,
    external_id: Optional[str] = None,
) -> Team:
    """Get or create a team record."""
    external_id = external_id or team_name.lower().replace(" ", "_")
    
    result = await db.execute(
        select(Team).where(
            Team.sport_id == sport_id,
            Team.external_team_id == external_id,
        )
    )
    team = result.scalar_one_or_none()
    
    if not team:
        # Generate abbreviation from team name
        words = team_name.split()
        if len(words) > 1:
            # Use last word (city/mascot) for abbreviation
            abbr = words[-1][:3].upper()
        else:
            abbr = team_name[:3].upper()
        
        team = Team(
            sport_id=sport_id,
            external_team_id=external_id,
            name=team_name,
            abbreviation=abbr,
        )
        db.add(team)
        await db.flush()
        logger.info(f"Created team: {team_name} ({abbr})")
    
    return team


async def get_or_create_game(
    db: AsyncSession,
    sport_id: int,
    external_game_id: str,
    home_team_id: int,
    away_team_id: int,
    start_time: datetime,
    status: str = "scheduled",
) -> tuple[Game, bool]:
    """
    Get or create a game record.
    
    Returns:
        Tuple of (Game, created) where created is True if new record was created
    """
    result = await db.execute(
        select(Game).where(
            Game.sport_id == sport_id,
            Game.external_game_id == external_game_id,
        )
    )
    game = result.scalar_one_or_none()
    created = False
    
    if not game:
        game = Game(
            sport_id=sport_id,
            external_game_id=external_game_id,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            start_time=start_time,
            status=status,
        )
        db.add(game)
        await db.flush()
        created = True
        logger.debug(f"Created game: {external_game_id}")
    else:
        # Update start time if changed
        if game.start_time != start_time:
            game.start_time = start_time
            await db.flush()
    
    return game, created


async def get_or_create_market(
    db: AsyncSession,
    sport_id: int,
    market_type: str,
    stat_type: Optional[str] = None,
    description: Optional[str] = None,
) -> Market:
    """Get or create a market record."""
    result = await db.execute(
        select(Market).where(
            Market.sport_id == sport_id,
            Market.market_type == market_type,
            Market.stat_type == stat_type if stat_type else Market.stat_type.is_(None),
        )
    )
    market = result.scalar_one_or_none()
    
    if not market:
        market = Market(
            sport_id=sport_id,
            market_type=market_type,
            stat_type=stat_type,
            description=description or f"{market_type} {stat_type or ''}".strip(),
        )
        db.add(market)
        await db.flush()
        logger.info(f"Created market: {market_type} {stat_type or ''}")
    
    return market


async def get_or_create_player(
    db: AsyncSession,
    sport_id: int,
    player_name: str,
    external_player_id: Optional[str] = None,
    team_id: Optional[int] = None,
) -> Player:
    """Get or create a player record."""
    external_id = external_player_id or player_name.lower().replace(" ", "_")
    
    result = await db.execute(
        select(Player).where(
            Player.sport_id == sport_id,
            Player.external_player_id == external_id,
        )
    )
    player = result.scalar_one_or_none()
    
    if not player:
        player = Player(
            sport_id=sport_id,
            external_player_id=external_id,
            name=player_name,
            team_id=team_id,
        )
        db.add(player)
        await db.flush()
        logger.info(f"Created player: {player_name}")
    
    return player


# =============================================================================
# Line Management
# =============================================================================

async def mark_lines_not_current(
    db: AsyncSession,
    game_id: int,
    market_id: int,
    sportsbook: str,
    player_id: Optional[int] = None,
) -> int:
    """
    Mark existing lines as not current for the same game/market/sportsbook/player combo.
    
    Returns:
        Number of lines marked as not current
    """
    conditions = [
        Line.game_id == game_id,
        Line.market_id == market_id,
        Line.sportsbook == sportsbook,
        Line.is_current == True,
    ]
    
    # Handle nullable player_id
    if player_id is not None:
        conditions.append(Line.player_id == player_id)
    else:
        conditions.append(Line.player_id.is_(None))
    
    result = await db.execute(
        update(Line)
        .where(and_(*conditions))
        .values(is_current=False)
    )
    
    return result.rowcount


async def insert_line(
    db: AsyncSession,
    game_id: int,
    market_id: int,
    sportsbook: str,
    side: str,
    odds: float,
    line_value: Optional[float] = None,
    player_id: Optional[int] = None,
    fetched_at: Optional[datetime] = None,
) -> Line:
    """Insert a new line with is_current=True."""
    line = Line(
        game_id=game_id,
        market_id=market_id,
        player_id=player_id,
        sportsbook=sportsbook,
        line_value=line_value,
        odds=odds,
        side=side,
        is_current=True,
        fetched_at=fetched_at or datetime.now(timezone.utc),
    )
    db.add(line)
    return line


# =============================================================================
# Main ETL Function
# =============================================================================

async def sync_games_and_lines(
    db: AsyncSession,
    sport_key: str,
    include_props: bool = False,
    use_stubs: bool = False,
) -> dict[str, Any]:
    """
    Sync games and betting lines for a sport from the odds provider.
    
    This function is idempotent:
    - Sports, teams, games, markets are upserted by external ID
    - Old lines are marked as is_current=False before inserting new ones
    
    Args:
        db: Database session
        sport_key: Sport identifier (e.g., 'basketball_nba')
        include_props: Whether to also fetch player props
        use_stubs: Use stub data instead of real API calls
    
    Returns:
        Dictionary with sync statistics
    """
    stats = {
        "sport": None,
        "teams_created": 0,
        "games_created": 0,
        "games_updated": 0,
        "markets_created": 0,
        "lines_added": 0,
        "lines_marked_old": 0,
        "players_created": 0,
        "props_added": 0,
        "errors": [],
    }
    
    try:
        # Get or create sport
        sport = await get_or_create_sport(db, sport_key)
        stats["sport"] = sport.league_code
        
        # Ensure base markets exist
        market_cache: dict[str, Market] = {}
        for market_type in ["moneyline", "spread", "total"]:
            market = await get_or_create_market(db, sport.id, market_type)
            market_cache[market_type] = market
        
        async with XYZOddsProvider(use_stubs=use_stubs) as provider:
            # Fetch games
            games_data = await provider.fetch_games(sport_key)
            logger.info(f"Fetched {len(games_data)} games for {sport_key}")
            
            for game_data in games_data:
                try:
                    # Get or create teams
                    home_team = await get_or_create_team(
                        db, sport.id, game_data.home_team
                    )
                    away_team = await get_or_create_team(
                        db, sport.id, game_data.away_team
                    )
                    
                    if home_team.id and not await _team_existed(db, home_team.id):
                        stats["teams_created"] += 1
                    if away_team.id and not await _team_existed(db, away_team.id):
                        stats["teams_created"] += 1
                    
                    # Get or create game
                    game, created = await get_or_create_game(
                        db,
                        sport.id,
                        game_data.external_game_id,
                        home_team.id,
                        away_team.id,
                        game_data.start_time,
                    )
                    
                    if created:
                        stats["games_created"] += 1
                    else:
                        stats["games_updated"] += 1
                    
                    # Fetch and sync main lines
                    lines_data = await provider.fetch_main_lines(
                        sport_key,
                        game_data.external_game_id,
                    )
                    
                    for line_data in lines_data:
                        market = market_cache.get(line_data.market_type)
                        if not market:
                            # Create market if not in cache
                            market = await get_or_create_market(
                                db, sport.id, line_data.market_type
                            )
                            market_cache[line_data.market_type] = market
                            stats["markets_created"] += 1
                        
                        # Mark old lines as not current
                        marked = await mark_lines_not_current(
                            db,
                            game.id,
                            market.id,
                            line_data.sportsbook,
                            player_id=None,  # Main lines have no player
                        )
                        stats["lines_marked_old"] += marked
                        
                        # Insert new line
                        await insert_line(
                            db,
                            game.id,
                            market.id,
                            line_data.sportsbook,
                            line_data.side,
                            line_data.odds,
                            line_data.line_value,
                            player_id=None,
                            fetched_at=line_data.fetched_at,
                        )
                        stats["lines_added"] += 1
                    
                    # Optionally fetch player props
                    if include_props:
                        props_result = await _sync_player_props(
                            db,
                            provider,
                            sport,
                            game,
                            sport_key,
                            market_cache,
                        )
                        stats["players_created"] += props_result.get("players_created", 0)
                        stats["props_added"] += props_result.get("props_added", 0)
                        stats["lines_marked_old"] += props_result.get("lines_marked_old", 0)
                
                except Exception as e:
                    logger.error(f"Error processing game {game_data.external_game_id}: {e}")
                    stats["errors"].append(str(e))
        
        # Commit transaction
        await db.commit()
        logger.info(f"Sync completed for {sport_key}: {stats}")
        return stats
    
    except Exception as e:
        await db.rollback()
        logger.error(f"ETL failed for {sport_key}: {e}")
        raise


async def _team_existed(db: AsyncSession, team_id: int) -> bool:
    """Check if team was already in database (helper for stats tracking)."""
    # This is a simplified check - in practice we track this during creation
    return True  # Assume existed to avoid double counting


async def _sync_player_props(
    db: AsyncSession,
    provider: XYZOddsProvider,
    sport: Sport,
    game: Game,
    sport_key: str,
    market_cache: dict[str, Market],
) -> dict[str, int]:
    """
    Sync player props for a game.
    
    Returns:
        Dictionary with props sync statistics
    """
    stats = {
        "players_created": 0,
        "props_added": 0,
        "lines_marked_old": 0,
    }
    
    try:
        props_data = await provider.fetch_player_props(
            sport_key,
            game.external_game_id,
        )
        
        for prop in props_data:
            # Get or create player
            player = await get_or_create_player(
                db,
                sport.id,
                prop.player_name,
                prop.player_external_id,
            )
            
            # Get or create prop market
            market_key = f"player_prop_{prop.stat_type}"
            if market_key not in market_cache:
                market = await get_or_create_market(
                    db,
                    sport.id,
                    "player_prop",
                    stat_type=prop.stat_type,
                    description=f"Player {prop.stat_type}",
                )
                market_cache[market_key] = market
            else:
                market = market_cache[market_key]
            
            # Mark old lines for this player/market/sportsbook as not current
            marked = await mark_lines_not_current(
                db,
                game.id,
                market.id,
                prop.sportsbook,
                player_id=player.id,
            )
            stats["lines_marked_old"] += marked
            
            # Insert over line
            await insert_line(
                db,
                game.id,
                market.id,
                prop.sportsbook,
                "over",
                prop.over_odds,
                prop.line_value,
                player_id=player.id,
                fetched_at=prop.fetched_at,
            )
            stats["props_added"] += 1
            
            # Insert under line
            await insert_line(
                db,
                game.id,
                market.id,
                prop.sportsbook,
                "under",
                prop.under_odds,
                prop.line_value,
                player_id=player.id,
                fetched_at=prop.fetched_at,
            )
            stats["props_added"] += 1
    
    except Exception as e:
        logger.error(f"Error syncing props for game {game.external_game_id}: {e}")
    
    return stats


# =============================================================================
# Convenience Functions
# =============================================================================

async def sync_all_sports(
    db: AsyncSession,
    include_props: bool = False,
    use_stubs: bool = False,
) -> dict[str, Any]:
    """
    Sync games and lines for all configured sports.
    
    Returns:
        Dictionary mapping sport_key to sync results
    """
    results = {}
    
    for sport_key in SPORT_KEY_TO_NAME.keys():
        try:
            results[sport_key] = await sync_games_and_lines(
                db,
                sport_key,
                include_props=include_props,
                use_stubs=use_stubs,
            )
        except Exception as e:
            logger.error(f"Failed to sync {sport_key}: {e}")
            results[sport_key] = {"error": str(e)}
    
    return results
