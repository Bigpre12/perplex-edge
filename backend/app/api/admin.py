"""Admin API endpoints for triggering ETL jobs and picks generation."""

import time
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import (
    sync_games_and_lines,
    sync_recent_player_stats,
    sync_injuries,
)
from app.services.picks_generator import generate_picks

router = APIRouter()


# =============================================================================
# Available Sport Keys
# =============================================================================

AVAILABLE_SPORTS = [
    "basketball_nba",
    "americanfootball_nfl",
    "baseball_mlb",
    "icehockey_nhl",
    "basketball_ncaab",
    "americanfootball_ncaaf",
]


# =============================================================================
# Admin Job Endpoints
# =============================================================================

@router.post("/jobs/sync-odds")
async def run_sync_odds_job(
    sport: str = Query("basketball_nba", description="Sport key to sync"),
    include_props: bool = Query(False, description="Include player props"),
    use_stubs: bool = Query(False, description="Use stub data for testing"),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger odds sync job for a sport.
    
    Syncs games, teams, markets, and betting lines from the odds provider.
    """
    if sport not in AVAILABLE_SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {AVAILABLE_SPORTS}",
        )
    
    start_time = time.time()
    
    try:
        result = await sync_games_and_lines(
            db,
            sport_key=sport,
            include_props=include_props,
            use_stubs=use_stubs,
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return {
            "job": "sync-odds",
            "status": "success",
            "sport": sport,
            "duration_ms": duration_ms,
            "counts": {
                "games_created": result.get("games_created", 0),
                "games_updated": result.get("games_updated", 0),
                "teams_created": result.get("teams_created", 0),
                "markets_created": result.get("markets_created", 0),
                "lines_added": result.get("lines_added", 0),
                "lines_marked_old": result.get("lines_marked_old", 0),
                "players_created": result.get("players_created", 0),
                "props_added": result.get("props_added", 0),
            },
            "errors": result.get("errors", []),
        }
    
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        raise HTTPException(
            status_code=500,
            detail={
                "job": "sync-odds",
                "status": "error",
                "sport": sport,
                "duration_ms": duration_ms,
                "error": str(e),
            },
        )


@router.post("/jobs/sync-stats")
async def run_sync_stats_job(
    sport: str = Query("basketball_nba", description="Sport key to sync"),
    games_back: int = Query(10, ge=1, le=50, description="Number of games to fetch"),
    only_today: bool = Query(True, description="Only players with lines today"),
    use_stubs: bool = Query(False, description="Use stub data for testing"),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger player stats sync job for a sport.
    
    Fetches recent game logs for players and writes to PlayerGameStats.
    """
    if sport not in AVAILABLE_SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {AVAILABLE_SPORTS}",
        )
    
    start_time = time.time()
    
    try:
        result = await sync_recent_player_stats(
            db,
            sport_key=sport,
            games_back=games_back,
            only_players_with_lines_today=only_today,
            use_stubs=use_stubs,
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Handle error response
        if "error" in result:
            return {
                "job": "sync-stats",
                "status": "error",
                "sport": sport,
                "duration_ms": duration_ms,
                "error": result["error"],
            }
        
        return {
            "job": "sync-stats",
            "status": "success",
            "sport": sport,
            "duration_ms": duration_ms,
            "counts": {
                "players_processed": result.get("players_processed", 0),
                "stats_created": result.get("stats_created", 0),
                "stats_updated": result.get("stats_updated", 0),
                "stats_skipped": result.get("stats_skipped", 0),
                "games_not_found": result.get("games_not_found", 0),
            },
            "errors": result.get("errors", []),
        }
    
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        raise HTTPException(
            status_code=500,
            detail={
                "job": "sync-stats",
                "status": "error",
                "sport": sport,
                "duration_ms": duration_ms,
                "error": str(e),
            },
        )


@router.post("/jobs/sync-injuries")
async def run_sync_injuries_job(
    sport: str = Query("basketball_nba", description="Sport key to sync"),
    include_lineups: bool = Query(True, description="Also fetch lineup data"),
    use_stubs: bool = Query(False, description="Use stub data for testing"),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger injury sync job for a sport.
    
    Fetches current injuries and projected availability, updates Injury table.
    """
    if sport not in AVAILABLE_SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {AVAILABLE_SPORTS}",
        )
    
    start_time = time.time()
    
    try:
        result = await sync_injuries(
            db,
            sport_key=sport,
            include_lineups=include_lineups,
            use_stubs=use_stubs,
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Handle error response
        if "error" in result:
            return {
                "job": "sync-injuries",
                "status": "error",
                "sport": sport,
                "duration_ms": duration_ms,
                "error": result["error"],
            }
        
        return {
            "job": "sync-injuries",
            "status": "success",
            "sport": sport,
            "duration_ms": duration_ms,
            "counts": {
                "injuries_created": result.get("injuries_created", 0),
                "injuries_updated": result.get("injuries_updated", 0),
                "players_created": result.get("players_created", 0),
                "players_not_found": result.get("players_not_found", 0),
                "starters_updated": result.get("starters_updated", 0),
            },
            "errors": result.get("errors", []),
        }
    
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        raise HTTPException(
            status_code=500,
            detail={
                "job": "sync-injuries",
                "status": "error",
                "sport": sport,
                "duration_ms": duration_ms,
                "error": str(e),
            },
        )


@router.post("/jobs/generate-picks")
async def run_generate_picks_job(
    sport: str = Query("basketball_nba", description="Sport key to generate picks for"),
    min_ev: float = Query(0.0, description="Minimum expected value threshold"),
    min_confidence: float = Query(0.5, ge=0.0, le=1.0, description="Minimum confidence threshold"),
    use_stubs: bool = Query(True, description="Use stub probability generator"),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger picks generation job for a sport.
    
    Generates model picks for today's games based on current lines and player stats.
    Old picks are marked as inactive before generating new ones.
    """
    if sport not in AVAILABLE_SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {AVAILABLE_SPORTS}",
        )
    
    start_time = time.time()
    
    try:
        result = await generate_picks(
            db,
            sport_key=sport,
            min_ev=min_ev,
            min_confidence=min_confidence,
            use_stubs=use_stubs,
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Handle error response
        if "error" in result:
            return {
                "job": "generate-picks",
                "status": "error",
                "sport": sport,
                "duration_ms": duration_ms,
                "error": result["error"],
            }
        
        return {
            "job": "generate-picks",
            "status": "success",
            "sport": sport,
            "duration_ms": duration_ms,
            "counts": {
                "picks_created": result.get("picks_created", 0),
                "picks_deactivated": result.get("picks_deactivated", 0),
                "lines_evaluated": result.get("lines_evaluated", 0),
                "games_processed": result.get("games_processed", 0),
            },
            "errors": result.get("errors", []),
        }
    
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        raise HTTPException(
            status_code=500,
            detail={
                "job": "generate-picks",
                "status": "error",
                "sport": sport,
                "duration_ms": duration_ms,
                "error": str(e),
            },
        )


# =============================================================================
# Utility Endpoints
# =============================================================================

@router.get("/sports")
async def list_available_sports():
    """List available sports for admin jobs."""
    return {
        "sports": AVAILABLE_SPORTS,
    }


@router.post("/jobs/run-all")
async def run_all_jobs(
    sport: str = Query("basketball_nba", description="Sport key to process"),
    use_stubs: bool = Query(False, description="Use stub data for testing"),
    db: AsyncSession = Depends(get_db),
):
    """
    Run all ETL jobs in sequence for a sport.
    
    Order: sync-odds -> sync-stats -> sync-injuries -> generate-picks
    """
    if sport not in AVAILABLE_SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {AVAILABLE_SPORTS}",
        )
    
    start_time = time.time()
    results = {}
    
    # Sync odds
    try:
        odds_result = await sync_games_and_lines(db, sport, include_props=True, use_stubs=use_stubs)
        results["sync-odds"] = {"status": "success", "counts": odds_result}
    except Exception as e:
        results["sync-odds"] = {"status": "error", "error": str(e)}
    
    # Sync stats
    try:
        stats_result = await sync_recent_player_stats(db, sport, use_stubs=use_stubs)
        results["sync-stats"] = {"status": "success", "counts": stats_result}
    except Exception as e:
        results["sync-stats"] = {"status": "error", "error": str(e)}
    
    # Sync injuries
    try:
        injuries_result = await sync_injuries(db, sport, use_stubs=use_stubs)
        results["sync-injuries"] = {"status": "success", "counts": injuries_result}
    except Exception as e:
        results["sync-injuries"] = {"status": "error", "error": str(e)}
    
    # Generate picks
    try:
        picks_result = await generate_picks(db, sport, use_stubs=use_stubs)
        results["generate-picks"] = {"status": "success", "counts": picks_result}
    except Exception as e:
        results["generate-picks"] = {"status": "error", "error": str(e)}
    
    duration_ms = int((time.time() - start_time) * 1000)
    
    return {
        "job": "run-all",
        "sport": sport,
        "duration_ms": duration_ms,
        "results": results,
    }
