"""ETL for syncing player rosters and team assignments from roster APIs."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Sport, Team, Player
from app.services.roster_provider import RosterProvider, RosterPlayerData, TeamData

logger = logging.getLogger(__name__)


# =============================================================================
# Sport Key Mappings
# =============================================================================

SPORT_KEY_TO_LEAGUE = {
    "basketball_nba": "NBA",
    "americanfootball_nfl": "NFL",
    "baseball_mlb": "MLB",
    "icehockey_nhl": "NHL",
}


# =============================================================================
# Team Name Matching
# =============================================================================

def normalize_team_name(name: str) -> str:
    """Normalize team name for matching."""
    return name.lower().strip()


async def find_team_by_name(
    db: AsyncSession,
    sport_id: int,
    team_name: str,
) -> Optional[Team]:
    """
    Find a team by name using fuzzy matching.
    
    Args:
        db: Database session
        sport_id: Sport ID to filter by
        team_name: Team name to search for
    
    Returns:
        Team if found, None otherwise
    """
    normalized = normalize_team_name(team_name)
    
    # Try exact match first
    result = await db.execute(
        select(Team).where(
            Team.sport_id == sport_id,
            Team.name.ilike(team_name),
        )
    )
    team = result.scalar_one_or_none()
    if team:
        return team
    
    # Try partial match
    result = await db.execute(
        select(Team).where(
            Team.sport_id == sport_id,
            Team.name.ilike(f"%{team_name}%"),
        )
    )
    team = result.scalar_one_or_none()
    if team:
        return team
    
    # Try matching by city or mascot
    words = team_name.split()
    for word in words:
        if len(word) >= 3:  # Skip short words
            result = await db.execute(
                select(Team).where(
                    Team.sport_id == sport_id,
                    Team.name.ilike(f"%{word}%"),
                )
            )
            team = result.scalar_one_or_none()
            if team:
                return team
    
    return None


# =============================================================================
# Player Name Matching
# =============================================================================

def normalize_player_name(name: str) -> str:
    """Normalize player name for matching."""
    # Remove common suffixes and normalize
    name = name.lower().strip()
    suffixes = [" jr.", " jr", " sr.", " sr", " iii", " ii", " iv"]
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    return name


async def find_player_by_name(
    db: AsyncSession,
    sport_id: int,
    player_name: str,
) -> Optional[Player]:
    """
    Find a player by name using fuzzy matching.
    
    Args:
        db: Database session
        sport_id: Sport ID to filter by
        player_name: Player name to search for
    
    Returns:
        Player if found, None otherwise
    """
    # Try exact match first
    result = await db.execute(
        select(Player).where(
            Player.sport_id == sport_id,
            Player.name.ilike(player_name),
        )
    )
    player = result.scalar_one_or_none()
    if player:
        return player
    
    # Try normalized match
    normalized = normalize_player_name(player_name)
    result = await db.execute(
        select(Player).where(
            Player.sport_id == sport_id,
        )
    )
    players = result.scalars().all()
    
    for p in players:
        if normalize_player_name(p.name) == normalized:
            return p
    
    # Try partial match (last name)
    name_parts = player_name.split()
    if len(name_parts) >= 2:
        last_name = name_parts[-1]
        result = await db.execute(
            select(Player).where(
                Player.sport_id == sport_id,
                Player.name.ilike(f"%{last_name}%"),
            )
        )
        candidates = result.scalars().all()
        
        # If we have candidates, try to match first name too
        first_name = name_parts[0]
        for candidate in candidates:
            if first_name.lower() in candidate.name.lower():
                return candidate
    
    return None


# =============================================================================
# Main ETL Functions
# =============================================================================

async def sync_rosters(
    db: AsyncSession,
    sport_key: str = "basketball_nba",
    use_stubs: bool = False,
) -> dict[str, Any]:
    """
    Sync player-team assignments from roster API.
    
    This function:
    1. Fetches current team rosters from the roster API
    2. Matches players in our database to roster data
    3. Updates team_id for players whose team has changed
    
    Args:
        db: Database session
        sport_key: Sport identifier (default: NBA)
        use_stubs: Use stub data instead of real API calls
    
    Returns:
        Dictionary with sync statistics
    """
    stats = {
        "sport": None,
        "teams_fetched": 0,
        "players_fetched": 0,
        "players_updated": 0,
        "players_not_found": 0,
        "errors": [],
    }
    
    try:
        # Get sport
        league_code = SPORT_KEY_TO_LEAGUE.get(sport_key)
        if not league_code:
            logger.warning(f"Unknown sport key: {sport_key}")
            stats["errors"].append(f"Unknown sport key: {sport_key}")
            return stats
        
        result = await db.execute(
            select(Sport).where(Sport.league_code == league_code)
        )
        sport = result.scalar_one_or_none()
        
        if not sport:
            logger.warning(f"Sport not found: {league_code}")
            stats["errors"].append(f"Sport not found: {league_code}")
            return stats
        
        stats["sport"] = sport.league_code
        
        async with RosterProvider(use_stubs=use_stubs) as provider:
            # Fetch teams
            teams_data = await provider.fetch_teams()
            stats["teams_fetched"] = len(teams_data)
            logger.info(f"Fetched {len(teams_data)} teams")
            
            # Build team lookup by name
            team_lookup: dict[str, TeamData] = {}
            for team in teams_data:
                team_lookup[normalize_team_name(team.full_name)] = team
                team_lookup[normalize_team_name(team.name)] = team
            
            # Fetch all players
            all_roster_players: list[RosterPlayerData] = []
            for team in teams_data:
                players = await provider.fetch_all_players_for_team(team.external_team_id)
                all_roster_players.extend(players)
            
            stats["players_fetched"] = len(all_roster_players)
            logger.info(f"Fetched {len(all_roster_players)} players from rosters")
            
            # Build roster lookup by player name
            roster_lookup: dict[str, RosterPlayerData] = {}
            for rp in all_roster_players:
                roster_lookup[normalize_player_name(rp.full_name)] = rp
            
            # Get all players in our database for this sport
            result = await db.execute(
                select(Player).where(Player.sport_id == sport.id)
            )
            db_players = result.scalars().all()
            
            # Update player team assignments
            for player in db_players:
                normalized_name = normalize_player_name(player.name)
                
                if normalized_name in roster_lookup:
                    roster_player = roster_lookup[normalized_name]
                    
                    # Find the team in our database
                    team = await find_team_by_name(
                        db, sport.id, roster_player.team_name
                    )
                    
                    if team and player.team_id != team.id:
                        old_team_id = player.team_id
                        player.team_id = team.id
                        
                        # Also update position if available
                        if roster_player.position and not player.position:
                            player.position = roster_player.position
                        
                        stats["players_updated"] += 1
                        logger.info(
                            f"Updated {player.name}: team_id {old_team_id} -> {team.id} ({roster_player.team_name})"
                        )
                else:
                    stats["players_not_found"] += 1
                    logger.debug(f"Player not found in roster: {player.name}")
        
        await db.commit()
        logger.info(f"Roster sync completed: {stats}")
        return stats
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Roster sync failed: {e}")
        stats["errors"].append(str(e))
        raise


async def update_player_team(
    db: AsyncSession,
    player_name: str,
    team_name: str,
    sport_key: str = "basketball_nba",
) -> bool:
    """
    Update a single player's team assignment.
    
    Useful for manual corrections or specific updates.
    
    Args:
        db: Database session
        player_name: Player name to update
        team_name: New team name
        sport_key: Sport identifier
    
    Returns:
        True if updated successfully, False otherwise
    """
    league_code = SPORT_KEY_TO_LEAGUE.get(sport_key)
    if not league_code:
        logger.warning(f"Unknown sport key: {sport_key}")
        return False
    
    result = await db.execute(
        select(Sport).where(Sport.league_code == league_code)
    )
    sport = result.scalar_one_or_none()
    
    if not sport:
        logger.warning(f"Sport not found: {league_code}")
        return False
    
    # Find player
    player = await find_player_by_name(db, sport.id, player_name)
    if not player:
        logger.warning(f"Player not found: {player_name}")
        return False
    
    # Find team
    team = await find_team_by_name(db, sport.id, team_name)
    if not team:
        logger.warning(f"Team not found: {team_name}")
        return False
    
    # Update
    old_team_id = player.team_id
    player.team_id = team.id
    await db.commit()
    
    logger.info(f"Updated {player_name}: team_id {old_team_id} -> {team.id} ({team_name})")
    return True


async def sync_player_team_from_roster_api(
    db: AsyncSession,
    player_name: str,
    sport_key: str = "basketball_nba",
    use_stubs: bool = False,
) -> Optional[str]:
    """
    Look up a player's current team from the roster API and update the database.
    
    Args:
        db: Database session
        player_name: Player name to look up
        sport_key: Sport identifier
        use_stubs: Use stub data
    
    Returns:
        Team name if found and updated, None otherwise
    """
    league_code = SPORT_KEY_TO_LEAGUE.get(sport_key)
    if not league_code:
        return None
    
    result = await db.execute(
        select(Sport).where(Sport.league_code == league_code)
    )
    sport = result.scalar_one_or_none()
    if not sport:
        return None
    
    async with RosterProvider(use_stubs=use_stubs) as provider:
        roster_player = await provider.fetch_player_by_name(player_name)
        
        if not roster_player:
            logger.warning(f"Player not found in roster API: {player_name}")
            return None
        
        # Find or create team
        team = await find_team_by_name(db, sport.id, roster_player.team_name)
        if not team:
            logger.warning(f"Team not found in database: {roster_player.team_name}")
            return None
        
        # Find player in our database
        player = await find_player_by_name(db, sport.id, player_name)
        if not player:
            logger.warning(f"Player not found in database: {player_name}")
            return None
        
        # Update
        if player.team_id != team.id:
            player.team_id = team.id
            if roster_player.position and not player.position:
                player.position = roster_player.position
            await db.commit()
            logger.info(f"Updated {player_name} team to {roster_player.team_name}")
        
        return roster_player.team_name
