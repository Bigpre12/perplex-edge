"""ETL for syncing injury data from injury providers."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Sport, Player, Team, Injury
from app.services.injury_provider import InjuryProvider, InjuryData, LineupData

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
    "tennis_atp": "ATP",
    "tennis_wta": "WTA",
}


# =============================================================================
# Player Lookup Helpers
# =============================================================================

async def find_player_by_external_id(
    db: AsyncSession,
    sport_id: int,
    external_player_id: str,
) -> Optional[Player]:
    """Find player by external ID."""
    result = await db.execute(
        select(Player).where(
            and_(
                Player.sport_id == sport_id,
                Player.external_player_id == external_player_id,
            )
        )
    )
    return result.scalar_one_or_none()


async def find_player_by_name(
    db: AsyncSession,
    sport_id: int,
    player_name: str,
) -> Optional[Player]:
    """Find player by exact name match."""
    result = await db.execute(
        select(Player).where(
            and_(
                Player.sport_id == sport_id,
                Player.name == player_name,
            )
        )
    )
    return result.scalar_one_or_none()


async def find_player_by_name_fuzzy(
    db: AsyncSession,
    sport_id: int,
    player_name: str,
) -> Optional[Player]:
    """
    Find player by fuzzy name match.
    
    Tries several variations:
    - Exact match
    - Case-insensitive match
    - Contains match
    """
    # Try exact match first
    player = await find_player_by_name(db, sport_id, player_name)
    if player:
        return player
    
    # Try case-insensitive match
    result = await db.execute(
        select(Player).where(
            and_(
                Player.sport_id == sport_id,
                Player.name.ilike(player_name),
            )
        )
    )
    player = result.scalar_one_or_none()
    if player:
        return player
    
    # Try contains match (e.g., "LeBron James" matches "LeBron")
    result = await db.execute(
        select(Player).where(
            and_(
                Player.sport_id == sport_id,
                Player.name.ilike(f"%{player_name}%"),
            )
        )
    )
    players = list(result.scalars().all())
    
    # Return first match if only one
    if len(players) == 1:
        return players[0]
    
    return None


async def find_or_create_player(
    db: AsyncSession,
    sport_id: int,
    external_player_id: str,
    player_name: str,
    team_name: Optional[str] = None,
) -> tuple[Player, bool]:
    """
    Find or create a player.
    
    Returns:
        Tuple of (Player, created) where created is True if new record
    """
    # Try external ID first
    player = await find_player_by_external_id(db, sport_id, external_player_id)
    if player:
        return player, False
    
    # Try name match
    player = await find_player_by_name_fuzzy(db, sport_id, player_name)
    if player:
        # Update external ID if missing
        if not player.external_player_id or player.external_player_id != external_player_id:
            player.external_player_id = external_player_id
        return player, False
    
    # Find team if provided
    team_id = None
    if team_name:
        result = await db.execute(
            select(Team).where(
                and_(
                    Team.sport_id == sport_id,
                    Team.name.ilike(f"%{team_name}%"),
                )
            )
        )
        team = result.scalar_one_or_none()
        if team:
            team_id = team.id
    
    # Create new player
    player = Player(
        sport_id=sport_id,
        external_player_id=external_player_id,
        name=player_name,
        team_id=team_id,
    )
    db.add(player)
    await db.flush()
    logger.info(f"Created player from injury data: {player_name}")
    
    return player, True


# =============================================================================
# Injury Upsert
# =============================================================================

async def upsert_injury(
    db: AsyncSession,
    sport_id: int,
    player_id: int,
    status: str,
    status_detail: Optional[str] = None,
    probability: Optional[float] = None,
    is_starter: Optional[bool] = None,
    source: Optional[str] = None,
    updated_at: Optional[datetime] = None,
) -> tuple[Injury, bool]:
    """
    Upsert an injury record.
    
    Uses (sport_id, player_id) as the unique key.
    
    Returns:
        Tuple of (Injury, created) where created is True if new record
    """
    # Convert to naive datetime for PostgreSQL
    if updated_at is None:
        updated_at = datetime.now(timezone.utc)
    elif updated_at.tzinfo is not None:
        updated_at = updated_at.replace(tzinfo=None)
    
    # Check for existing injury
    result = await db.execute(
        select(Injury).where(
            and_(
                Injury.sport_id == sport_id,
                Injury.player_id == player_id,
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update existing record
        existing.status = status
        existing.status_detail = status_detail
        existing.probability = probability
        if is_starter is not None:
            existing.is_starter_flag = is_starter
        existing.source = source
        existing.updated_at = updated_at
        return existing, False
    
    # Create new injury record
    injury = Injury(
        sport_id=sport_id,
        player_id=player_id,
        status=status,
        status_detail=status_detail,
        probability=probability,
        is_starter_flag=is_starter,
        source=source,
        updated_at=updated_at,
    )
    db.add(injury)
    return injury, True


async def update_starter_flag(
    db: AsyncSession,
    sport_id: int,
    player_id: int,
    is_starter: bool,
    updated_at: Optional[datetime] = None,
) -> bool:
    """
    Update the is_starter_flag on an existing injury record.
    
    Returns:
        True if an injury record was updated, False otherwise
    """
    result = await db.execute(
        select(Injury).where(
            and_(
                Injury.sport_id == sport_id,
                Injury.player_id == player_id,
            )
        )
    )
    injury = result.scalar_one_or_none()
    
    if injury:
        injury.is_starter_flag = is_starter
        # Convert to naive datetime
        if updated_at is None:
            injury.updated_at = datetime.now(timezone.utc)
        elif updated_at.tzinfo is not None:
            injury.updated_at = updated_at.replace(tzinfo=None)
        else:
            injury.updated_at = updated_at
        return True
    
    return False


# =============================================================================
# Main ETL Function
# =============================================================================

async def sync_injuries(
    db: AsyncSession,
    sport_key: str,
    include_lineups: bool = True,
    use_stubs: bool = False,
) -> dict[str, Any]:
    """
    Sync injury data for a sport.
    
    This function is idempotent:
    - Injuries are upserted by (sport_id, player_id)
    - Existing injuries are updated with latest status
    
    Args:
        db: Database session
        sport_key: Sport identifier (e.g., 'basketball_nba')
        include_lineups: Also fetch lineups to update starter flags
        use_stubs: Use stub data instead of real API calls
    
    Returns:
        Dictionary with sync statistics
    """
    stats = {
        "sport": None,
        "injuries_created": 0,
        "injuries_updated": 0,
        "players_created": 0,
        "players_not_found": 0,
        "starters_updated": 0,
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
        
        async with InjuryProvider(use_stubs=use_stubs) as provider:
            # Fetch injuries
            injuries_data = await provider.fetch_injuries(sport_key)
            logger.info(f"Fetched {len(injuries_data)} injuries for {sport_key}")
            
            for injury_data in injuries_data:
                try:
                    # Find or create player
                    player, player_created = await find_or_create_player(
                        db,
                        sport.id,
                        injury_data.player_external_id,
                        injury_data.player_name,
                        injury_data.team_name,
                    )
                    
                    if player_created:
                        stats["players_created"] += 1
                    
                    # Upsert injury
                    injury, created = await upsert_injury(
                        db,
                        sport.id,
                        player.id,
                        status=injury_data.status,
                        status_detail=injury_data.injury_detail,
                        probability=injury_data.probability,
                        is_starter=injury_data.is_starter,
                        source=injury_data.source,
                        updated_at=injury_data.updated_at,
                    )
                    
                    if created:
                        stats["injuries_created"] += 1
                    else:
                        stats["injuries_updated"] += 1
                
                except Exception as e:
                    logger.error(f"Error processing injury for {injury_data.player_name}: {e}")
                    stats["errors"].append(f"{injury_data.player_name}: {str(e)}")
            
            # Fetch and process lineups if requested
            if include_lineups:
                try:
                    lineups_data = await provider.fetch_lineups(sport_key)
                    logger.info(f"Fetched lineups for {sport_key}")
                    
                    for lineup in lineups_data:
                        # Find player
                        player = await find_player_by_external_id(
                            db, sport.id, lineup.player_external_id
                        )
                        
                        if not player:
                            player = await find_player_by_name_fuzzy(
                                db, sport.id, lineup.player_name
                            )
                        
                        if player:
                            updated = await update_starter_flag(
                                db,
                                sport.id,
                                player.id,
                                lineup.is_starter,
                                lineup.updated_at,
                            )
                            if updated:
                                stats["starters_updated"] += 1
                
                except Exception as e:
                    logger.error(f"Error processing lineups: {e}")
                    stats["errors"].append(f"Lineups: {str(e)}")
        
        # Commit transaction
        await db.commit()
        logger.info(f"Injury sync completed for {sport_key}: {stats}")
        return stats
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Injury ETL failed for {sport_key}: {e}")
        raise


# =============================================================================
# Convenience Functions
# =============================================================================

async def sync_all_injuries(
    db: AsyncSession,
    include_lineups: bool = True,
    use_stubs: bool = False,
) -> dict[str, Any]:
    """
    Sync injuries for all configured sports.
    
    Returns:
        Dictionary mapping sport_key to sync results
    """
    results = {}
    
    for sport_key in SPORT_KEY_TO_LEAGUE.keys():
        try:
            results[sport_key] = await sync_injuries(
                db,
                sport_key,
                include_lineups=include_lineups,
                use_stubs=use_stubs,
            )
        except Exception as e:
            logger.error(f"Failed to sync injuries for {sport_key}: {e}")
            results[sport_key] = {"error": str(e)}
    
    return results


async def clear_old_injuries(
    db: AsyncSession,
    sport_id: int,
    older_than_days: int = 7,
) -> int:
    """
    Clear injury records that haven't been updated in N days.
    
    This helps remove stale injury records for players who have recovered.
    
    Args:
        db: Database session
        sport_id: Sport ID to filter by
        older_than_days: Clear injuries not updated in this many days
    
    Returns:
        Number of records deleted
    """
    from datetime import timedelta
    from sqlalchemy import delete
    
    # Use naive datetime for TIMESTAMP WITHOUT TIME ZONE column comparison
    cutoff = (datetime.now(timezone.utc) - timedelta(days=older_than_days)).replace(tzinfo=None)
    
    result = await db.execute(
        delete(Injury).where(
            and_(
                Injury.sport_id == sport_id,
                Injury.updated_at < cutoff,
            )
        )
    )
    
    await db.commit()
    deleted = result.rowcount
    
    logger.info(f"Cleared {deleted} old injury records for sport {sport_id}")
    return deleted


# =============================================================================
# ESPN Injury Sync (no API key required)
# =============================================================================

async def sync_espn_injuries_to_db(
    db: AsyncSession,
    sport_key: str = "basketball_nba",
) -> dict:
    """
    Fetch injuries from ESPN and save to Injury table.
    
    This uses the free ESPN API (no key required) and saves data directly
    to the Injury table so the injury filter works correctly.
    
    Args:
        db: Database session
        sport_key: Sport key (e.g., "basketball_nba")
    
    Returns:
        Dict with sync stats (created, updated, not_found)
    """
    from app.data.providers.espn import ESPNProvider
    
    logger.info(f"Starting ESPN injury sync for {sport_key}")
    
    # Get sport_id from league code
    league_code = SPORT_KEY_TO_LEAGUE.get(sport_key)
    if not league_code:
        return {"error": f"Unknown sport key: {sport_key}"}
    
    result = await db.execute(
        select(Sport).where(Sport.league_code == league_code)
    )
    sport = result.scalar_one_or_none()
    if not sport:
        return {"error": f"Sport not found for league: {league_code}"}
    
    # Fetch from ESPN
    try:
        async with ESPNProvider() as provider:
            injuries_data = await provider.fetch_injuries(sport_key)
    except Exception as e:
        logger.error(f"Failed to fetch ESPN injuries: {e}")
        return {"error": f"ESPN fetch failed: {str(e)}"}
    
    if not injuries_data:
        return {"error": "No injury data returned from ESPN"}
    
    # Process each team's injuries
    stats = {"created": 0, "updated": 0, "not_found": 0, "skipped": 0}
    now = datetime.utcnow()
    
    for team_entry in injuries_data:
        team_name = team_entry.get("displayName", "Unknown")
        team_injuries = team_entry.get("injuries", [])
        
        for injury_entry in team_injuries:
            # Get player info from the injury entry
            athlete = injury_entry.get("athlete", {})
            player_name = athlete.get("displayName")
            
            if not player_name:
                stats["skipped"] += 1
                continue
            
            # Try to find player by exact name first
            player_result = await db.execute(
                select(Player).where(
                    and_(
                        Player.sport_id == sport.id,
                        Player.name == player_name,
                    )
                )
            )
            player = player_result.scalars().first()
            
            if not player:
                # Try case-insensitive match (use first() to handle multiple matches)
                player_result = await db.execute(
                    select(Player).where(
                        and_(
                            Player.sport_id == sport.id,
                            Player.name.ilike(player_name),
                        )
                    )
                )
                player = player_result.scalars().first()
            
            if not player:
                logger.debug(f"Player not found: {player_name}")
                stats["not_found"] += 1
                continue
            
            # Extract injury details
            status = injury_entry.get("status", "Unknown").upper()
            # Normalize status
            if status in ["O", "OUT"]:
                status = "OUT"
            elif status in ["D", "DOUBTFUL"]:
                status = "DOUBTFUL"
            elif status in ["Q", "QUESTIONABLE"]:
                status = "QUESTIONABLE"
            elif status in ["P", "PROBABLE"]:
                status = "PROBABLE"
            elif status in ["GTD", "GAME TIME DECISION", "DAY-TO-DAY"]:
                status = "GTD"
            
            detail = injury_entry.get("longComment") or injury_entry.get("shortComment") or injury_entry.get("description")
            
            # Check for existing injury record
            existing_result = await db.execute(
                select(Injury).where(Injury.player_id == player.id)
            )
            existing = existing_result.scalar_one_or_none()
            
            if existing:
                # Update existing
                existing.status = status
                existing.status_detail = detail[:500] if detail else None
                existing.updated_at = now
                existing.source = "espn"
                stats["updated"] += 1
            else:
                # Create new
                new_injury = Injury(
                    sport_id=sport.id,
                    player_id=player.id,
                    status=status,
                    status_detail=detail[:500] if detail else None,
                    source="espn",
                    updated_at=now,
                )
                db.add(new_injury)
                stats["created"] += 1
    
    await db.commit()
    
    logger.info(
        f"ESPN injury sync completed for {sport_key}: "
        f"created={stats['created']}, updated={stats['updated']}, "
        f"not_found={stats['not_found']}, skipped={stats['skipped']}"
    )
    
    return stats
