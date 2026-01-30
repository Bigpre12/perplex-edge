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
    get_reliability_data,
    get_roi_by_confidence,
    get_clv_analysis,
    compute_calibration_metrics,
    get_all_sync_status,
    check_stale_data,
)
from app.services.picks_generator import generate_picks

router = APIRouter()


# =============================================================================
# Available Sport Keys
# =============================================================================

AVAILABLE_SPORTS = [
    "basketball_nba",
    "basketball_ncaab",
    "americanfootball_nfl",
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
# Force Refresh Endpoint (Clear + Sync)
# =============================================================================

@router.post("/jobs/force-refresh")
async def force_refresh_games(
    sport: str = Query("basketball_nba", description="Sport key to refresh"),
    db: AsyncSession = Depends(get_db),
):
    """
    Force refresh games by clearing old data and syncing with stubs.
    
    This endpoint:
    1. Clears all existing games for the sport
    2. Syncs fresh games using dynamic schedule stubs
    
    Use this when data appears stale or to reset to today's schedule.
    """
    from app.services.etl_games_and_lines import clear_stale_games
    
    if sport not in AVAILABLE_SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {AVAILABLE_SPORTS}",
        )
    
    start_time = time.time()
    
    try:
        # Step 1: Clear ALL old games (keep_today=False ensures complete refresh)
        clear_result = await clear_stale_games(db, sport, keep_today=False)
        
        # Check for clear errors
        if isinstance(clear_result, dict) and "error" in clear_result:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to clear games: {clear_result['error']}",
            )
        
        # Step 2: Sync fresh data with stubs (guaranteed to work)
        sync_result = await sync_with_fallback(
            db,
            sport_key=sport,
            include_props=True,
            use_real_api=False,  # Force stubs for reliability
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Check for sync warnings/errors
        sync_errors = sync_result.get("errors", [])
        status = "success" if not sync_errors else "partial_success"
        
        return {
            "job": "force-refresh",
            "status": status,
            "sport": sport,
            "duration_ms": duration_ms,
            "cleared": clear_result,
            "synced": {
                "data_source": sync_result.get("data_source", "stubs"),
                "games_created": sync_result.get("games_created", 0),
                "lines_added": sync_result.get("lines_added", 0),
                "props_added": sync_result.get("props_added", 0),
                "errors": sync_errors,
            },
        }
    
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        raise HTTPException(
            status_code=500,
            detail={
                "job": "force-refresh",
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
# Sync Status Endpoints
# =============================================================================

@router.get("/sync-status")
async def get_sync_status(
    db: AsyncSession = Depends(get_db),
):
    """
    Get current sync status for all sports.
    
    Shows last_updated timestamps, counts, and health status.
    Use this to verify that scheduled jobs are running.
    """
    return await get_all_sync_status(db)


@router.get("/sync-status/stale")
async def get_stale_data_alerts(
    max_age_hours: int = Query(24, description="Hours before data is considered stale"),
    db: AsyncSession = Depends(get_db),
):
    """
    Check for stale data across all sports.
    
    Returns alerts for any sport/data-type that hasn't been
    updated in the specified number of hours.
    """
    return await check_stale_data(db, max_age_hours)


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
# Calibration Endpoints
# =============================================================================

@router.get("/calibration/{sport}")
async def get_calibration_report(
    sport: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get calibration metrics by probability bucket.
    
    Shows how well predicted probabilities match actual hit rates.
    Perfect calibration = predicted % equals actual hit %.
    
    Returns:
    - Metrics per probability bucket (50-55%, 55-60%, etc.)
    - Brier score (lower is better, 0 = perfect)
    - Calibration error (ECE)
    """
    if sport not in AVAILABLE_SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {AVAILABLE_SPORTS}",
        )
    
    result = await get_reliability_data(db, sport, days)
    return result


@router.get("/calibration/{sport}/reliability")
async def get_reliability_plot_data(
    sport: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get data for reliability plot (calibration curve).
    
    A reliability plot shows predicted probability vs actual hit rate.
    Perfect calibration = diagonal line from (0,0) to (1,1).
    
    Use this data to visualize model calibration.
    """
    if sport not in AVAILABLE_SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {AVAILABLE_SPORTS}",
        )
    
    result = await get_reliability_data(db, sport, days)
    
    # Format for plotting
    plot_data = {
        "sport": sport,
        "days": days,
        "x_predicted": [b["predicted_prob"] for b in result.get("buckets", [])],
        "y_actual": [b["actual_hit_rate"] for b in result.get("buckets", [])],
        "sample_sizes": [b["sample_size"] for b in result.get("buckets", [])],
        "bucket_labels": [b["probability_bucket"] for b in result.get("buckets", [])],
        "overall_brier": result.get("overall_brier"),
        "calibration_error": result.get("calibration_error"),
    }
    return plot_data


@router.get("/calibration/{sport}/roi")
async def get_roi_by_confidence_bucket(
    sport: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get ROI breakdown by confidence/probability bucket.
    
    Shows which confidence levels are most profitable.
    Use this to identify your edge and optimal bet sizing.
    """
    if sport not in AVAILABLE_SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {AVAILABLE_SPORTS}",
        )
    
    result = await get_roi_by_confidence(db, sport, days)
    return result


@router.get("/calibration/{sport}/clv")
async def get_clv_analysis_endpoint(
    sport: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get Closing Line Value (CLV) analysis.
    
    CLV measures how often you beat the closing line.
    Positive CLV = got better odds than market close (edge indicator).
    
    Returns:
    - Average CLV in cents
    - % of bets with positive CLV
    - CLV distribution
    """
    if sport not in AVAILABLE_SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport: {sport}. Available: {AVAILABLE_SPORTS}",
        )
    
    result = await get_clv_analysis(db, sport, days)
    return result


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
