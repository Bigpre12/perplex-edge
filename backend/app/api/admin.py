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
    get_quota_status,
    sync_with_fallback,
    save_daily_snapshot,
    list_snapshots,
    load_snapshot,
    check_sync_health,
    run_all_health_checks,
    validate_database_state,
    get_api_monitor,
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
# Quota Management Endpoints
# =============================================================================

@router.get("/quota")
async def get_api_quota():
    """
    Get current API quota status for The Odds API.
    
    Returns:
        - remaining: Requests remaining this month
        - used: Requests used this month  
        - monthly_limit: Total monthly limit (500 for free tier)
        - percent_used: Percentage of quota consumed
        - last_updated: When quota was last updated from API response
    """
    quota = get_quota_status()
    return {
        "status": "ok",
        "quota": quota,
        "recommendations": {
            "daily_budget": 6,  # 2x daily × 3 sports
            "monthly_budget": 180,
            "buffer_remaining": quota["remaining"] - 180 if quota["remaining"] > 180 else 0,
        }
    }


@router.post("/jobs/sync-quota-safe")
async def run_quota_safe_sync(
    sport: str = Query("basketball_nba", description="Sport key to sync"),
    include_props: bool = Query(True, description="Include player props"),
    force_stubs: bool = Query(False, description="Force stubs (skip real API)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Quota-safe sync with automatic failover.
    
    Cascade order:
    1. The Odds API (if quota available)
    2. ESPN free API (if available for sport)
    3. Stub data (guaranteed fallback)
    
    Use this for ad-hoc syncs to protect your API quota.
    """
    if sport not in AVAILABLE_SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {AVAILABLE_SPORTS}",
        )
    
    start_time = time.time()
    
    try:
        result = await sync_with_fallback(
            db,
            sport_key=sport,
            include_props=include_props,
            use_real_api=not force_stubs,
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        quota = get_quota_status()
        
        return {
            "job": "sync-quota-safe",
            "status": "success",
            "sport": sport,
            "data_source": result.get("data_source", "unknown"),
            "duration_ms": duration_ms,
            "counts": {
                "games_created": result.get("games_created", 0),
                "games_updated": result.get("games_updated", 0),
                "lines_added": result.get("lines_added", 0),
                "props_added": result.get("props_added", 0),
            },
            "quota": quota,
            "errors": result.get("errors", []),
        }
    
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        raise HTTPException(
            status_code=500,
            detail={
                "job": "sync-quota-safe",
                "status": "error",
                "sport": sport,
                "duration_ms": duration_ms,
                "error": str(e),
            },
        )


# =============================================================================
# Snapshot Endpoints
# =============================================================================

@router.get("/snapshots")
async def get_snapshots(
    sport: Optional[str] = Query(None, description="Filter by sport key"),
    limit: int = Query(30, description="Max snapshots to return"),
):
    """
    List available data snapshots.
    
    Snapshots are dated backups saved before each daily refresh.
    Use them to:
    - Audit past slates
    - Debug pick decisions
    - Rebuild models from historical data
    """
    snapshots = list_snapshots(sport_key=sport, limit=limit)
    return {
        "count": len(snapshots),
        "snapshots": snapshots,
    }


@router.post("/snapshots")
async def create_snapshot(
    sport: str = Query("basketball_nba", description="Sport to snapshot"),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a manual snapshot of current data.
    
    Normally snapshots are created automatically before daily refresh.
    Use this endpoint for ad-hoc backups.
    """
    if sport not in AVAILABLE_SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {AVAILABLE_SPORTS}",
        )
    
    from datetime import date
    result = await save_daily_snapshot(db, sport, date.today())
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return {
        "status": "success",
        "snapshot": result,
    }


@router.get("/snapshots/{sport}/{snapshot_date}")
async def get_snapshot(
    sport: str,
    snapshot_date: str,
):
    """
    Load a specific snapshot by sport and date.
    
    Path params:
    - sport: Sport key or short name (e.g., "nba" or "basketball_nba")
    - snapshot_date: Date in YYYY-MM-DD format
    """
    from datetime import date as date_type
    
    # Normalize sport key
    if sport in ("nba", "ncaab", "nfl"):
        sport_key = {
            "nba": "basketball_nba",
            "ncaab": "basketball_ncaab",
            "nfl": "americanfootball_nfl",
        }[sport]
    else:
        sport_key = sport
    
    try:
        snapshot_date_parsed = date_type.fromisoformat(snapshot_date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format: {snapshot_date}. Use YYYY-MM-DD.",
        )
    
    try:
        snapshot = load_snapshot(sport_key, snapshot_date_parsed)
        return snapshot
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Snapshot not found for {sport} on {snapshot_date}",
        )


# =============================================================================
# Health Check Endpoints
# =============================================================================

@router.get("/health")
async def get_health_status(
    db: AsyncSession = Depends(get_db),
):
    """
    Run health checks on all sports.
    
    Checks that each sport has minimum expected:
    - Games
    - Lines
    - Props
    - Picks
    
    Use this to detect silent sync failures.
    """
    result = await run_all_health_checks(db)
    return result


@router.get("/health/{sport}")
async def get_sport_health(
    sport: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Run health check for a specific sport.
    
    Returns detailed counts vs. thresholds.
    """
    if sport not in AVAILABLE_SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {AVAILABLE_SPORTS}",
        )
    
    result = await check_sync_health(db, sport)
    return result.to_dict()


# =============================================================================
# API Monitoring Endpoints
# =============================================================================

@router.get("/monitoring/api")
async def get_api_metrics(
    minutes: int = Query(60, description="Time window in minutes"),
):
    """
    Get API call metrics and statistics.
    
    Returns:
    - Total calls, error rates, latency
    - Per-provider breakdown
    - Recent call history
    """
    monitor = get_api_monitor()
    return {
        "metrics": monitor.get_metrics(minutes=minutes),
        "recent_calls": [c.to_dict() for c in monitor.get_recent_calls(minutes=minutes)[-20:]],
    }


@router.get("/monitoring/alerts")
async def get_api_alerts():
    """
    Check for API monitoring alerts.
    
    Returns active alerts for:
    - High error rates (>10%)
    - Rate limiting (429 responses)
    - High latency (>5s average)
    - Sudden count drops
    """
    monitor = get_api_monitor()
    alerts = monitor.get_alerts()
    
    return {
        "alert_count": len(alerts),
        "has_critical": any(a.get("severity") == "error" for a in alerts),
        "alerts": alerts,
    }


# =============================================================================
# Data Quality Endpoints
# =============================================================================

@router.get("/quality/{sport}")
async def get_data_quality(
    sport: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Run data quality validation on current database state.
    
    Checks:
    - No duplicate game IDs
    - Game times within expected windows
    - Prop lines within valid ranges (no 0 pts, no 500 pt totals)
    - Count comparison vs. yesterday (detect sudden drops)
    """
    if sport not in AVAILABLE_SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {AVAILABLE_SPORTS}",
        )
    
    result = await validate_database_state(db, sport)
    
    # Add alert level to response
    if not result.valid:
        alert_level = "error"
    elif result.warning_count > 5:
        alert_level = "warning"
    else:
        alert_level = "ok"
    
    return {
        "alert_level": alert_level,
        "validation": result.to_dict(),
    }


@router.get("/quality")
async def get_all_data_quality(
    db: AsyncSession = Depends(get_db),
):
    """
    Run data quality validation on all sports.
    
    Returns combined quality report.
    """
    results = {}
    all_valid = True
    total_errors = 0
    total_warnings = 0
    
    for sport in ["basketball_nba", "basketball_ncaab", "americanfootball_nfl"]:
        result = await validate_database_state(db, sport)
        results[sport] = result.to_dict()
        if not result.valid:
            all_valid = False
        total_errors += result.error_count
        total_warnings += result.warning_count
    
    return {
        "overall_valid": all_valid,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "sports": results,
    }


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
