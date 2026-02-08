"""Sync/ETL API endpoints for manual data refresh."""

from typing import Optional

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.etl.sync_service import SyncService
from app.etl.odds_api import SPORT_KEYS

router = APIRouter()

@router.post("/odds/{sport}")
async def sync_odds_for_sport(
    sport: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger odds sync for a specific sport.
    
    Available sports: NBA, NFL, MLB, NHL, NCAAB, NCAAF
    """
    sport_upper = sport.upper()
    if sport_upper not in SPORT_KEYS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {list(SPORT_KEYS.keys())}",
        )

    sync_service = SyncService(db)
    
    try:
        stats = await sync_service.sync_odds_for_sport(sport_upper)
        return {
            "status": "success",
            "sport": sport_upper,
            "stats": stats,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.post("/odds")
async def sync_all_odds(
    db: AsyncSession = Depends(get_db),
):
    """Trigger odds sync for all sports."""
    sync_service = SyncService(db)
    
    try:
        results = await sync_service.sync_all_sports()
        return {
            "status": "success",
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.get("/sports")
async def list_available_sports():
    """List available sports for syncing."""
    return {
        "sports": [
            {"code": code, "api_key": key}
            for code, key in SPORT_KEYS.items()
        ]
    }

@router.post("/rosters")
async def sync_rosters(
    sport: str = "NBA",
    use_stubs: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """
    Sync player rosters to update team assignments.
    
    Fetches current rosters from external API and updates player-team
    relationships in the database.
    
    Args:
        sport: Sport to sync (default: NBA)
        use_stubs: Use stub data instead of real API
    
    Returns:
        Sync statistics including players updated
    """
    from app.services.etl_rosters import sync_rosters as do_sync_rosters
    
    # Map sport code to sport_key
    sport_key_map = {
        "NBA": "basketball_nba",
        "NFL": "americanfootball_nfl",
        "MLB": "baseball_mlb",
        "NHL": "icehockey_nhl",
    }
    
    sport_upper = sport.upper()
    sport_key = sport_key_map.get(sport_upper)
    
    if not sport_key:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {list(sport_key_map.keys())}",
        )
    
    try:
        stats = await do_sync_rosters(db, sport_key, use_stubs=use_stubs)
        return {
            "status": "success",
            "sport": sport_upper,
            "stats": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Roster sync failed: {str(e)}")

@router.post("/rosters/player")
async def sync_single_player_roster(
    player_name: str,
    sport: str = "NBA",
    use_stubs: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """
    Look up and update a single player's team from roster API.
    
    Useful for fixing individual player team assignments.
    
    Args:
        player_name: Player name to look up
        sport: Sport (default: NBA)
        use_stubs: Use stub data
    
    Returns:
        Updated team name if successful
    """
    from app.services.etl_rosters import sync_player_team_from_roster_api
    
    sport_key_map = {
        "NBA": "basketball_nba",
        "NFL": "americanfootball_nfl",
        "MLB": "baseball_mlb",
        "NHL": "icehockey_nhl",
    }
    
    sport_upper = sport.upper()
    sport_key = sport_key_map.get(sport_upper)
    
    if not sport_key:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {list(sport_key_map.keys())}",
        )
    
    try:
        team_name = await sync_player_team_from_roster_api(
            db, player_name, sport_key, use_stubs=use_stubs
        )
        
        if team_name:
            return {
                "status": "success",
                "player": player_name,
                "team": team_name,
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Player not found or could not update: {player_name}",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Player roster sync failed: {str(e)}")

@router.post("/player-teams")
async def sync_player_teams(
    sport: str = "basketball_nba",
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk sync all player teams from PLAYER_TEAMS mapping.
    
    This updates all players in the database to have the correct team_id
    based on the PLAYER_TEAMS dictionary in etl_games_and_lines.py.
    
    Use this endpoint after updating PLAYER_TEAMS or to fix stale team assignments.
    
    Args:
        sport: Sport key (default: basketball_nba)
    
    Returns:
        Sync statistics: updated, not_found, teams_not_found, already_correct
    """
    from app.services.etl_games_and_lines import sync_all_player_teams
    
    try:
        stats = await sync_all_player_teams(db, sport)
        return {
            "status": "success",
            "sport": sport,
            "stats": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Player team sync failed: {str(e)}")

@router.post("/clear-games")
async def clear_games(
    sport: str = "basketball_nba",
    db: AsyncSession = Depends(get_db),
):
    """
    Clear all games, lines, and picks for a sport to start fresh.
    
    Use this to remove stale data before running a fresh sync.
    Keeps teams and players but removes all game-related data.
    
    Args:
        sport: Sport key (default: basketball_nba)
    
    Returns:
        Deletion counts: picks_deleted, lines_deleted, games_deleted
    """
    from app.services.etl_games_and_lines import clear_stale_games
    
    try:
        stats = await clear_stale_games(db, sport)
        return {
            "status": "success",
            "sport": sport,
            "stats": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear games failed: {str(e)}")

@router.get("/status")
async def get_sync_status(
    db: AsyncSession = Depends(get_db),
):
    """Get current sync status and data counts."""
    from sqlalchemy import select, func
    from app.models import Sport, Game, Line, Injury, ModelPick, Player

    # Get counts
    sports_count = await db.scalar(select(func.count()).select_from(Sport))
    games_count = await db.scalar(select(func.count()).select_from(Game))
    lines_count = await db.scalar(select(func.count()).select_from(Line))
    current_lines = await db.scalar(
        select(func.count()).select_from(Line).where(Line.is_current == True)
    )
    injuries_count = await db.scalar(select(func.count()).select_from(Injury))
    picks_count = await db.scalar(select(func.count()).select_from(ModelPick))
    active_picks = await db.scalar(
        select(func.count()).select_from(ModelPick).where(ModelPick.is_active == True)
    )
    players_count = await db.scalar(select(func.count()).select_from(Player))
    players_with_team = await db.scalar(
        select(func.count()).select_from(Player).where(Player.team_id.isnot(None))
    )

    return {
        "status": "ok",
        "counts": {
            "sports": sports_count or 0,
            "games": games_count or 0,
            "lines": {
                "total": lines_count or 0,
                "current": current_lines or 0,
            },
            "injuries": injuries_count or 0,
            "picks": {
                "total": picks_count or 0,
                "active": active_picks or 0,
            },
            "players": {
                "total": players_count or 0,
                "with_team": players_with_team or 0,
            },
        },
    }
