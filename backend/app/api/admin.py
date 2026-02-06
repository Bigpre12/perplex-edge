"""Admin API endpoints for triggering ETL jobs and picks generation."""

import logging
import time
from datetime import datetime, timezone
from typing import Optional, Dict

logger = logging.getLogger(__name__)

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
# Rate Limiting for Manual Refresh (in-memory, resets on restart)
# =============================================================================

# Store last refresh time per sport: {sport_key: datetime}
_last_refresh_times: Dict[str, datetime] = {}
MANUAL_REFRESH_COOLDOWN_SECONDS = 300  # 5 minutes between manual refreshes


# =============================================================================
# Available Sport Keys
# =============================================================================

AVAILABLE_SPORTS = [
    # Basketball
    "basketball_nba",
    "basketball_ncaab",
    "basketball_wnba",
    # Football
    "americanfootball_nfl",
    "americanfootball_ncaaf",
    # Baseball
    "baseball_mlb",
    # Hockey
    "icehockey_nhl",
    # Tennis
    "tennis_atp",
    "tennis_wta",
    # Golf
    "golf_pga_tour",
    # Soccer
    "soccer_epl",
    "soccer_uefa_champs_league",
    "soccer_usa_mls",
    # MMA/UFC
    "mma_mixed_martial_arts",
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


# =============================================================================
# Cache Management Endpoints
# =============================================================================

@router.post("/cache/clear")
async def clear_cache():
    """
    Clear the in-memory cache.
    
    This forces all cached data (picks, games, hit rates) to be recalculated
    on the next request. Use after fixing season/date issues or after
    significant data changes.
    
    Returns:
        Status of cache clear operation
    """
    try:
        from app.services.memory_cache import get_memory_cache
        cache = get_memory_cache()
        cache.clear_all()
        
        return {
            "status": "ok",
            "message": "Cache cleared successfully",
            "note": "All cached data will be recalculated on next request",
        }
    except ImportError:
        return {
            "status": "warning",
            "message": "Memory cache module not available",
            "note": "No cache to clear",
        }


@router.get("/season-info")
async def get_season_info():
    """
    Get current season information for all sports.
    
    Useful for verifying season calculations are correct after fixes.
    
    Returns:
        Season labels, start dates, and schedule filenames for each sport
    """
    from app.services.season_helper import (
        get_nba_season_label,
        get_ncaab_season_label,
        get_nfl_season_year,
        get_mlb_season_label,
        get_ncaaf_season_label,
        get_nba_season_start,
        get_ncaab_season_start,
        get_nfl_season_start,
        get_mlb_season_start,
        get_ncaaf_season_start,
        get_schedule_filename,
    )
    
    return {
        "status": "ok",
        "current_date": datetime.now(timezone.utc).isoformat(),
        "sports": {
            "basketball_nba": {
                "season_label": get_nba_season_label(),
                "season_start": get_nba_season_start().isoformat(),
                "schedule_file": get_schedule_filename("basketball_nba"),
            },
            "basketball_ncaab": {
                "season_label": get_ncaab_season_label(),
                "season_start": get_ncaab_season_start().isoformat(),
                "schedule_file": get_schedule_filename("basketball_ncaab"),
            },
            "americanfootball_nfl": {
                "season_label": str(get_nfl_season_year()),
                "season_start": get_nfl_season_start().isoformat(),
                "schedule_file": get_schedule_filename("americanfootball_nfl"),
            },
            "baseball_mlb": {
                "season_label": get_mlb_season_label(),
                "season_start": get_mlb_season_start().isoformat(),
                "schedule_file": get_schedule_filename("baseball_mlb"),
            },
            "americanfootball_ncaaf": {
                "season_label": get_ncaaf_season_label(),
                "season_start": get_ncaaf_season_start().isoformat(),
                "schedule_file": get_schedule_filename("americanfootball_ncaaf"),
            },
        },
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
# Debug Endpoint (Check Schedule Files)
# =============================================================================

@router.get("/debug/schedules")
async def debug_schedules():
    """Check if schedule files exist and can be read."""
    from pathlib import Path
    import json
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    EASTERN_TZ = ZoneInfo("America/New_York")
    today = datetime.now(EASTERN_TZ).date()
    today_str = today.isoformat()
    
    schedules_dir = Path(__file__).parent.parent.parent / "data" / "schedules"
    
    # Use dynamic season helpers for schedule filenames
    from app.services.season_helper import get_schedule_filename, get_current_season_label
    
    result = {
        "today_eastern": today_str,
        "schedules_dir": str(schedules_dir),
        "schedules_dir_exists": schedules_dir.exists(),
        "current_nba_season": get_current_season_label("basketball_nba"),
        "current_ncaab_season": get_current_season_label("basketball_ncaab"),
        "files": {},
    }
    
    sport_keys = [
        ("nba", "basketball_nba"),
        ("ncaab", "basketball_ncaab"),
    ]
    
    for sport, sport_key in sport_keys:
        filename = get_schedule_filename(sport_key)
        filepath = schedules_dir / filename
        file_info = {
            "path": str(filepath),
            "filename": filename,
            "exists": filepath.exists(),
        }
        if filepath.exists():
            try:
                with open(filepath) as f:
                    data = json.load(f)
                file_info["total_games"] = len(data.get("games", []))
                todays_games = [g for g in data.get("games", []) if g.get("date") == today_str]
                file_info["games_today"] = len(todays_games)
                file_info["sample_today"] = todays_games[:2] if todays_games else []
            except Exception as e:
                file_info["error"] = str(e)
        result["files"][sport] = file_info
    
    return result


# =============================================================================
# Force Refresh Endpoint (Clear + Sync)
# =============================================================================

@router.get("/jobs/refresh/{sport}")
async def browser_force_refresh(
    sport: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Browser-friendly GET endpoint to force refresh data.
    
    Just open in browser:
    - /admin/jobs/refresh/basketball_nba
    - /admin/jobs/refresh/basketball_ncaab  
    - /admin/jobs/refresh/americanfootball_nfl
    """
    from app.services.etl_games_and_lines import clear_stale_games
    
    if sport not in AVAILABLE_SPORTS:
        return {"error": f"Unknown sport: {sport}", "available": AVAILABLE_SPORTS}
    
    start_time = time.time()
    
    try:
        # Clear old data
        clear_result = await clear_stale_games(db, sport, keep_today=False)
        
        # Sync fresh data
        sync_result = await sync_with_fallback(
            db,
            sport_key=sport,
            include_props=True,
            use_real_api=False,
        )
        
        # Generate picks for the synced data
        picks_result = await generate_picks(
            db,
            sport_key=sport,
            min_ev=0.0,
            min_confidence=0.5,
            use_stubs=True,
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return {
            "status": "success",
            "sport": sport,
            "duration_ms": duration_ms,
            "games_synced": sync_result.get("games_created", 0) + sync_result.get("games_updated", 0),
            "lines_synced": sync_result.get("lines_added", 0),
            "props_synced": sync_result.get("props_added", 0),
            "picks_generated": picks_result.get("picks_created", 0),
            "data_source": sync_result.get("data_source", "unknown"),
            "cleared": clear_result,
            "full_sync_result": sync_result,
            "picks_result": picks_result,
        }
    except Exception as e:
        import traceback
        return {"status": "error", "sport": sport, "error": str(e), "traceback": traceback.format_exc()}


@router.get("/jobs/manual-refresh/{sport}")
async def manual_refresh_live(
    sport: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Manual refresh with rate limiting - fetches LIVE data from API if quota allows.
    
    Rate limited to 1 request per 5 minutes per sport to protect API quota.
    Use this when you need real-time line updates before a game.
    
    Cascade order:
    1. Check rate limit (5 min cooldown)
    2. Check API quota
    3. Fetch live odds from The Odds API (if quota available)
    4. Fall back to stubs if API unavailable
    5. Generate fresh picks
    
    Browser-friendly: just open in browser.
    """
    global _last_refresh_times
    
    if sport not in AVAILABLE_SPORTS:
        return {"error": f"Unknown sport: {sport}", "available": AVAILABLE_SPORTS}
    
    # Check rate limit
    now = datetime.now(timezone.utc)
    last_refresh = _last_refresh_times.get(sport)
    
    if last_refresh:
        seconds_since = (now - last_refresh).total_seconds()
        if seconds_since < MANUAL_REFRESH_COOLDOWN_SECONDS:
            remaining = int(MANUAL_REFRESH_COOLDOWN_SECONDS - seconds_since)
            return {
                "status": "rate_limited",
                "sport": sport,
                "message": f"Please wait {remaining} seconds before refreshing again",
                "cooldown_seconds": MANUAL_REFRESH_COOLDOWN_SECONDS,
                "seconds_remaining": remaining,
                "last_refresh": last_refresh.isoformat(),
            }
    
    start_time = time.time()
    
    try:
        # Check quota - use real API if available
        quota = get_quota_status()
        use_real_api = quota["remaining"] > 10
        
        # Update rate limit tracker
        _last_refresh_times[sport] = now
        
        # Sync fresh data (prefer real API for live lines)
        sync_result = await sync_with_fallback(
            db,
            sport_key=sport,
            include_props=True,
            use_real_api=use_real_api,
        )
        
        # Generate picks for the synced data
        picks_result = await generate_picks(
            db,
            sport_key=sport,
            min_ev=0.0,
            min_confidence=0.5,
            use_stubs=not use_real_api,
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return {
            "status": "success",
            "sport": sport,
            "duration_ms": duration_ms,
            "data_source": sync_result.get("data_source", "unknown"),
            "used_live_api": use_real_api,
            "games_synced": sync_result.get("games_created", 0) + sync_result.get("games_updated", 0),
            "lines_synced": sync_result.get("lines_added", 0),
            "props_synced": sync_result.get("props_added", 0),
            "picks_generated": picks_result.get("picks_created", 0),
            "quota_remaining": quota["remaining"],
            "next_refresh_available": (now.timestamp() + MANUAL_REFRESH_COOLDOWN_SECONDS),
            "cooldown_seconds": MANUAL_REFRESH_COOLDOWN_SECONDS,
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "sport": sport,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


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
# Discord Alert Endpoints
# =============================================================================

@router.post("/alerts/test")
async def test_discord_alert():
    """
    Send a test Discord alert to verify webhook configuration.
    
    Make sure DISCORD_WEBHOOK_URL environment variable is set.
    """
    from app.services.alerts_service import send_discord_message, create_embed, DISCORD_WEBHOOK_URL
    
    if not DISCORD_WEBHOOK_URL:
        return {
            "status": "not_configured",
            "message": "DISCORD_WEBHOOK_URL environment variable is not set",
            "help": "Add DISCORD_WEBHOOK_URL to your Railway environment variables",
        }
    
    # Send test message
    embed = create_embed(
        title="Test Alert",
        description="This is a test alert from Perplex Edge. If you see this, your Discord webhook is configured correctly!",
        color=0x00FF00,  # Green
        footer="Perplex Edge | Test Alert",
    )
    
    success = await send_discord_message(embeds=[embed])
    
    return {
        "status": "sent" if success else "failed",
        "message": "Test alert sent to Discord" if success else "Failed to send alert",
    }


@router.get("/alerts/test-high-ev")
async def test_high_ev_alert(
    db: AsyncSession = Depends(get_db),
):
    """
    Send a sample high-EV pick alert to Discord.
    """
    from app.services.alerts_service import alert_high_ev_pick, DISCORD_WEBHOOK_URL
    
    if not DISCORD_WEBHOOK_URL:
        return {
            "status": "not_configured",
            "message": "DISCORD_WEBHOOK_URL environment variable is not set",
        }
    
    # Send sample alert
    success = await alert_high_ev_pick(
        player_name="LeBron James",
        stat_type="PTS",
        line=24.5,
        side="over",
        odds=-115,
        ev=0.092,  # 9.2% EV
        model_prob=0.62,
        hit_rate_5g=0.8,
        sport="NBA",
        game_time="7:30 PM ET",
    )
    
    return {
        "status": "sent" if success else "failed",
        "message": "Sample high-EV alert sent" if success else "Failed to send alert",
    }


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
# Brain (Autonomous System) Endpoints
# =============================================================================

@router.get("/brain/analyze", response_model=dict)
async def analyze_system():
    """Run comprehensive brain analyzer to understand and improve the system."""
    try:
        from app.services.brain_analyzer import brain_analyzer
        
        # Run comprehensive analysis
        analysis = await brain_analyzer.analyze_all_endpoints()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis": brain_analyzer.get_analysis_summary()
        }
        
    except Exception as e:
        logger.error(f"Brain analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Brain analysis failed: {str(e)}")


@router.post("/brain/analyze/auto-fix", response_model=dict)
async def generate_auto_fixes():
    """Generate automatic fixes for system issues."""
    try:
        from app.services.brain_analyzer import brain_analyzer
        
        # Generate auto-fixes
        fixes = await brain_analyzer.generate_auto_fixes()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "auto_fixes": fixes
        }
        
    except Exception as e:
        logger.error(f"Auto-fix generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Auto-fix generation failed: {str(e)}")


@router.post("/brain/analyze/expand", response_model=dict)
async def generate_expansions():
    """Generate system expansions and new features."""
    try:
        from app.services.brain_analyzer import brain_analyzer
        
        # Generate expansions
        expansions = await brain_analyzer.generate_expansions()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "expansions": expansions
        }
        
    except Exception as e:
        logger.error(f"Expansion generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Expansion generation failed: {str(e)}")


@router.post("/brain/analyze/commit", response_model=dict)
async def commit_improvements():
    """Commit improvements to git."""
    try:
        from app.services.brain_analyzer import brain_analyzer
        
        # Generate fixes and expansions
        fixes = await brain_analyzer.generate_auto_fixes()
        expansions = await brain_analyzer.generate_expansions()
        
        improvements = {
            "fixes": fixes.get("fixes", []),
            "expansions": expansions.get("expansions", [])
        }
        
        # Commit improvements
        result = await brain_analyzer.commit_improvements(improvements)
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "improvements": improvements,
            "commit_result": result
        }
        
    except Exception as e:
        logger.error(f"Improvement commit failed: {e}")
        raise HTTPException(status_code=500, detail=f"Improvement commit failed: {str(e)}")


@router.get("/brain/analyze/summary", response_model=dict)
async def get_analysis_summary():
    """Get comprehensive brain analysis summary."""
    try:
        from app.services.brain_analyzer import brain_analyzer
        
        summary = brain_analyzer.get_analysis_summary()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Analysis summary failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis summary failed: {str(e)}")


@router.post("/fix-sport-mappings", response_model=dict)
async def fix_sport_mappings_production(db: AsyncSession = Depends(get_db)):
    """Fix sport mappings in production database - CRITICAL FIX."""
    try:
        logger.info("[ADMIN] Starting PRODUCTION sport mapping fix...")
        
        from app.models import Player, Team, Line, ModelPick, Game
        from sqlalchemy import select, update, func
        
        # Track changes
        changes_made = {
            "nba_players_fixed": 0,
            "nhl_players_fixed": 0,
            "other_sports_fixed": 0,
            "total_players_fixed": 0,
            "lines_fixed": 0,
            "picks_fixed": 0,
            "errors": []
        }
        
        try:
            # Step 1: Fix NBA players incorrectly in NHL (sport_id=53)
            logger.info("[ADMIN] Fixing NBA players incorrectly assigned to NHL...")
            
            # Get NBA teams
            nba_teams_result = await db.execute(
                select(Team).where(Team.sport_id == 30)  # NBA sport_id
            )
            nba_teams = nba_teams_result.scalars().all()
            nba_team_ids = [team.id for team in nba_teams]
            
            if nba_team_ids:
                # Find NBA players incorrectly assigned to NHL
                nba_players_in_nhl_result = await db.execute(
                    select(Player)
                    .where(
                        Player.team_id.in_(nba_team_ids),
                        Player.sport_id == 53  # Incorrectly assigned to NHL
                    )
                )
                nba_players_in_nhl = nba_players_in_nhl_result.scalars().all()
                
                # Fix NBA players
                for player in nba_players_in_nhl:
                    await db.execute(
                        update(Player)
                        .where(Player.id == player.id)
                        .values(sport_id=30)  # Correct NBA sport_id
                    )
                    changes_made["nba_players_fixed"] += 1
                    logger.info(f"[ADMIN] Fixed NBA player: {player.name} (ID: {player.id})")
            
            # Step 2: Fix NHL players incorrectly in NBA (sport_id=30)
            logger.info("[ADMIN] Fixing NHL players incorrectly assigned to NBA...")
            
            # Get NHL teams
            nhl_teams_result = await db.execute(
                select(Team).where(Team.sport_id == 53)  # NHL sport_id
            )
            nhl_teams = nhl_teams_result.scalars().all()
            nhl_team_ids = [team.id for team in nhl_teams]
            
            if nhl_team_ids:
                # Find NHL players incorrectly assigned to NBA
                nhl_players_in_nba_result = await db.execute(
                    select(Player)
                    .where(
                        Player.team_id.in_(nhl_team_ids),
                        Player.sport_id == 30  # Incorrectly assigned to NBA
                    )
                )
                nhl_players_in_nba = nhl_players_in_nba_result.scalars().all()
                
                # Fix NHL players
                for player in nhl_players_in_nba:
                    await db.execute(
                        update(Player)
                        .where(Player.id == player.id)
                        .values(sport_id=53)  # Correct NHL sport_id
                    )
                    changes_made["nhl_players_fixed"] += 1
                    logger.info(f"[ADMIN] Fixed NHL player: {player.name} (ID: {player.id})")
            
            # Step 3: Fix ALL players to match their team's sport
            logger.info("[ADMIN] Fixing ALL players to match their team's sport...")
            
            # Get all players with incorrect sport mappings
            incorrect_mappings_result = await db.execute(
                select(Player, Team)
                .join(Team, Player.team_id == Team.id)
                .where(Player.sport_id != Team.sport_id)
            )
            incorrect_mappings = incorrect_mappings_result.all()
            
            for player, team in incorrect_mappings:
                await db.execute(
                    update(Player)
                    .where(Player.id == player.id)
                    .values(sport_id=team.sport_id)
                )
                changes_made["other_sports_fixed"] += 1
                logger.info(f"[ADMIN] Fixed {player.name} from sport_id={player.sport_id} to sport_id={team.sport_id} ({team.name})")
            
            # Step 4: Update related data (Lines) - Lines don't have sport_id, get from game
            logger.info("[ADMIN] Lines don't have sport_id - skipping Lines fix (they get sport from game)")
            changes_made["lines_fixed"] = 0
            
            # Step 5: Update related data (ModelPicks)
            logger.info("[ADMIN] Updating ModelPicks to match their game's sport...")
            
            picks_to_fix_result = await db.execute(
                select(ModelPick, Game)
                .join(Game, ModelPick.game_id == Game.id)
                .where(ModelPick.sport_id != Game.sport_id)
            )
            picks_to_fix = picks_to_fix_result.all()
            
            for pick, game in picks_to_fix:
                await db.execute(
                    update(ModelPick)
                    .where(ModelPick.id == pick.id)
                    .values(sport_id=game.sport_id)
                )
                changes_made["picks_fixed"] += 1
                logger.info(f"[ADMIN] Fixed ModelPick {pick.id} to sport_id={game.sport_id}")
            
            # Commit all changes
            await db.commit()
            
            # Calculate totals
            changes_made["total_players_fixed"] = (
                changes_made["nba_players_fixed"] + 
                changes_made["nhl_players_fixed"] + 
                changes_made["other_sports_fixed"]
            )
            
            logger.info("[ADMIN] ✅ Sport mapping fix completed!")
            logger.info(f"[ADMIN] 📊 Summary: {changes_made}")
            
            return {
                "status": "success",
                "message": "Sport mapping fix completed successfully",
                "changes_made": changes_made,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"[ADMIN] ❌ Error fixing sport mappings: {e}")
            await db.rollback()
            changes_made["errors"].append(str(e))
            return {
                "status": "error",
                "message": "Sport mapping fix failed",
                "changes_made": changes_made,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
    except Exception as e:
        logger.error(f"[ADMIN] Critical error in sport mapping fix: {e}")
        raise HTTPException(status_code=500, detail=f"Sport mapping fix failed: {str(e)}")


@router.post("/verify-sport-mappings", response_model=dict)
async def verify_sport_mappings_production(db: AsyncSession = Depends(get_db)):
    """Verify sport mappings are correct in production."""
    try:
        logger.info("[ADMIN] Verifying sport mappings...")
        
        from app.models import Player, Team
        from sqlalchemy import select, func
        
        verification_results = {
            "nba_players_in_nba": 0,
            "nba_players_in_nhl": 0,
            "nhl_players_in_nhl": 0,
            "nhl_players_in_nba": 0,
            "total_players": 0,
            "incorrect_mappings": 0,
            "status": "unknown"
        }
        
        try:
            # Count NBA players
            nba_teams_result = await db.execute(
                select(Team).where(Team.sport_id == 30)
            )
            nba_teams = nba_teams_result.scalars().all()
            nba_team_ids = [team.id for team in nba_teams]
            
            if nba_team_ids:
                # NBA players correctly in NBA
                nba_players_in_nba_result = await db.execute(
                    select(func.count(Player.id))
                    .where(
                        Player.team_id.in_(nba_team_ids),
                        Player.sport_id == 30
                    )
                )
                verification_results["nba_players_in_nba"] = nba_players_in_nba_result.scalar() or 0
                
                # NBA players incorrectly in NHL
                nba_players_in_nhl_result = await db.execute(
                    select(func.count(Player.id))
                    .where(
                        Player.team_id.in_(nba_team_ids),
                        Player.sport_id == 53
                    )
                )
                verification_results["nba_players_in_nhl"] = nba_players_in_nhl_result.scalar() or 0
            
            # Count NHL players
            nhl_teams_result = await db.execute(
                select(Team).where(Team.sport_id == 53)
            )
            nhl_teams = nhl_teams_result.scalars().all()
            nhl_team_ids = [team.id for team in nhl_teams]
            
            if nhl_team_ids:
                # NHL players correctly in NHL
                nhl_players_in_nhl_result = await db.execute(
                    select(func.count(Player.id))
                    .where(
                        Player.team_id.in_(nhl_team_ids),
                        Player.sport_id == 53
                    )
                )
                verification_results["nhl_players_in_nhl"] = nhl_players_in_nhl_result.scalar() or 0
                
                # NHL players incorrectly in NBA
                nhl_players_in_nba_result = await db.execute(
                    select(func.count(Player.id))
                    .where(
                        Player.team_id.in_(nhl_team_ids),
                        Player.sport_id == 30
                    )
                )
                verification_results["nhl_players_in_nba"] = nhl_players_in_nba_result.scalar() or 0
            
            # Total players and incorrect mappings
            total_players_result = await db.execute(select(func.count(Player.id)))
            verification_results["total_players"] = total_players_result.scalar() or 0
            
            incorrect_mappings_result = await db.execute(
                select(func.count(Player.id))
                .select_from(
                    select(Player.id)
                    .join(Team, Player.team_id == Team.id)
                    .where(Player.sport_id != Team.sport_id)
                    .subquery()
                )
            )
            verification_results["incorrect_mappings"] = incorrect_mappings_result.scalar() or 0
            
            # Determine status
            if verification_results["incorrect_mappings"] == 0:
                verification_results["status"] = "perfect"
            elif verification_results["nba_players_in_nhl"] == 0 and verification_results["nhl_players_in_nba"] == 0:
                verification_results["status"] = "good"
            else:
                verification_results["status"] = "needs_fix"
            
            logger.info("[ADMIN] ✅ Sport mapping verification completed!")
            logger.info(f"[ADMIN] 📊 Results: {verification_results}")
            
            return {
                "status": "success",
                "verification": verification_results,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"[ADMIN] ❌ Error verifying sport mappings: {e}")
            return {
                "status": "error",
                "verification": verification_results,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
    except Exception as e:
        logger.error(f"[ADMIN] Critical error in sport mapping verification: {e}")
        raise HTTPException(status_code=500, detail=f"Sport mapping verification failed: {str(e)}")


@router.get("/resources", response_model=dict)
async def get_resource_status():
    """Get current resource usage and credit monitoring."""
    try:
        from app.services.resource_monitor import resource_monitor
        
        # Get current metrics and optimization recommendations
        optimization = resource_monitor.optimize_resource_usage()
        baseline = resource_monitor.get_performance_baseline()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "resource_monitoring": optimization,
            "performance_baseline": baseline,
            "monitoring_active": resource_monitor.monitoring_active
        }
        
    except Exception as e:
        logger.error(f"Resource status failed: {e}")
        raise HTTPException(status_code=500, detail=f"Resource monitoring failed: {str(e)}")


@router.post("/resources/monitoring/start")
async def start_resource_monitoring(interval_seconds: int = 60):
    """Start continuous resource monitoring."""
    try:
        from app.services.resource_monitor import resource_monitor
        
        if resource_monitor.monitoring_active:
            return {
                "status": "already_active",
                "message": "Resource monitoring is already active"
            }
        
        # Start monitoring in background
        asyncio.create_task(resource_monitor.start_monitoring(interval_seconds))
        
        return {
            "status": "started",
            "message": f"Resource monitoring started with {interval_seconds}s interval",
            "interval_seconds": interval_seconds
        }
        
    except Exception as e:
        logger.error(f"Failed to start resource monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")


@router.post("/resources/monitoring/stop")
async def stop_resource_monitoring():
    """Stop continuous resource monitoring."""
    try:
        from app.services.resource_monitor import resource_monitor
        
        resource_monitor.stop_monitoring()
        
        return {
            "status": "stopped",
            "message": "Resource monitoring stopped"
        }
        
    except Exception as e:
        logger.error(f"Failed to stop resource monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")


@router.get("/resources/baseline", response_model=dict)
async def get_performance_baseline():
    """Get performance baseline statistics."""
    try:
        from app.services.resource_monitor import resource_monitor
        
        baseline = resource_monitor.get_performance_baseline()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "baseline": baseline
        }
        
    except Exception as e:
        logger.error(f"Performance baseline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Baseline failed: {str(e)}")


@router.get("/resources/export", response_model=dict)
async def export_resource_metrics():
    """Export resource metrics history."""
    try:
        from app.services.resource_monitor import resource_monitor
        
        export_data = resource_monitor.export_metrics()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "export_data": json.loads(export_data)
        }
        
    except Exception as e:
        logger.error(f"Resource export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/verification", response_model=dict)
async def get_verification_status():
    """Get comprehensive verification status and go-live checklist."""
    try:
        from app.services.verification_engine import run_complete_verification
        
        # Run complete verification suite
        verification_results = await run_complete_verification()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verification": verification_results
        }
        
    except Exception as e:
        logger.error(f"Verification status failed: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.get("/verification/stress-test", response_model=dict)
async def run_stress_test():
    """Run brain loop stress test on historical data."""
    try:
        from app.services.verification_engine import stress_test_brain_loop
        
        result = await stress_test_brain_loop()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stress_test": result
        }
        
    except Exception as e:
        logger.error(f"Stress test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stress test failed: {str(e)}")


@router.get("/verification/backtest", response_model=dict)
async def run_ev_backtest():
    """Run EV and Kelly backtest with historical data."""
    try:
        from app.services.verification_engine import backtest_ev_kelly_outputs
        
        result = await backtest_ev_kelly_outputs()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "backtest": result
        }
        
    except Exception as e:
        logger.error(f"EV backtest failed: {e}")
        raise HTTPException(status_code=500, detail=f"EV backtest failed: {str(e)}")


@router.get("/verification/performance", response_model=dict)
async def run_performance_benchmark():
    """Run Hobby tier performance benchmark."""
    try:
        from app.services.verification_engine import benchmark_hobby_performance
        
        result = await benchmark_hobby_performance()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "benchmark": result
        }
        
    except Exception as e:
        logger.error(f"Performance benchmark failed: {e}")
        raise HTTPException(status_code=500, detail=f"Performance benchmark failed: {str(e)}")


@router.get("/verification/checklist", response_model=dict)
async def get_go_live_checklist():
    """Get comprehensive go-live checklist."""
    try:
        from app.services.verification_engine import generate_go_live_checklist
        
        checklist = await generate_go_live_checklist()
        
        return {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checklist": checklist
        }
        
    except Exception as e:
        logger.error(f"Go-live checklist failed: {e}")
        raise HTTPException(status_code=500, detail=f"Go-live checklist failed: {str(e)}")


@router.get("/brain", response_model=dict)
async def get_brain_status():
    """
    Get full autonomous brain status.
    
    Shows self-monitoring health checks, healing history,
    optimization state, and recent decisions.
    """
    from app.services.brain import get_brain_status as _get_brain_status
    return _get_brain_status()


@router.get("/brain/health")
async def get_brain_health():
    """
    Get compact brain health summary.
    
    Quick check: how many components are healthy/degraded/critical.
    """
    from app.services.brain import get_brain_health_summary
    return get_brain_health_summary()


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
# Sport ID Verification Endpoint (for debugging NFL/NCAAF/Tennis mapping issues)
# =============================================================================

@router.get("/verify/sport-ids")
async def verify_sport_id_counts(
    db: AsyncSession = Depends(get_db),
):
    """
    Verify props/games/picks counts by sport_id.
    
    Use this endpoint to debug NFL/NCAAF bleed issues:
    - NFL props should be under sport_id=31 (americanfootball_nfl)
    - NCAAF props should be under sport_id=41 (americanfootball_ncaaf)
    - ATP tennis under sport_id=42, WTA under sport_id=43
    
    Returns counts grouped by sport_id with the expected sport key.
    """
    from sqlalchemy import select, func
    from app.models import Sport, Game, Line, ModelPick
    from app.core.constants import SPORT_ID_TO_KEY
    
    # Get all sports from DB
    sports_result = await db.execute(select(Sport))
    sports = {s.id: s for s in sports_result.scalars().all()}
    
    results = []
    for sport_id, sport_key in SPORT_ID_TO_KEY.items():
        sport = sports.get(sport_id)
        
        # Count games
        games_count = await db.scalar(
            select(func.count()).select_from(Game).where(Game.sport_id == sport_id)
        ) or 0
        
        # Count lines (props)
        lines_count = await db.scalar(
            select(func.count()).select_from(Line)
            .join(Game, Line.game_id == Game.id)
            .where(Game.sport_id == sport_id)
        ) or 0
        
        # Count player props (lines with player_id)
        props_count = await db.scalar(
            select(func.count()).select_from(Line)
            .join(Game, Line.game_id == Game.id)
            .where(Game.sport_id == sport_id, Line.player_id.isnot(None))
        ) or 0
        
        # Count picks
        picks_count = await db.scalar(
            select(func.count()).select_from(ModelPick).where(ModelPick.sport_id == sport_id)
        ) or 0
        
        results.append({
            "sport_id": sport_id,
            "expected_key": sport_key,
            "db_key": sport.key if sport else None,
            "db_league_code": sport.league_code if sport else None,
            "exists_in_db": sport is not None,
            "counts": {
                "games": games_count,
                "lines": lines_count,
                "player_props": props_count,
                "picks": picks_count,
            }
        })
    
    return {
        "status": "ok",
        "sport_id_audit": results,
        "verification_notes": [
            "NFL should have sport_id=31 (americanfootball_nfl)",
            "NCAAF should have sport_id=41 (americanfootball_ncaaf)",
            "If NFL props appear under sport_id=41, there's a mapping issue",
            "Tennis ATP=42, WTA=43 should have non-zero counts after sync",
        ]
    }


@router.get("/verify/sportsbooks")
async def verify_sportsbooks(
    db: AsyncSession = Depends(get_db),
):
    """
    Verify which sportsbooks have lines in the database.
    
    Use this to debug why only DraftKings (or one book) is showing:
    - If only 1 sportsbook, data was synced before multi-book fix
    - Trigger /admin/jobs/force-refresh to re-sync with multiple books
    """
    from sqlalchemy import select, func, distinct
    from app.models import Line, Game
    from app.core.constants import SPORT_ID_TO_KEY
    
    # Get unique sportsbooks and their counts
    sportsbook_result = await db.execute(
        select(
            Line.sportsbook,
            func.count(Line.id).label("line_count"),
        )
        .where(Line.is_current == True)
        .group_by(Line.sportsbook)
        .order_by(func.count(Line.id).desc())
    )
    sportsbooks = [
        {"sportsbook": row[0], "line_count": row[1]}
        for row in sportsbook_result.all()
    ]
    
    # Get counts per sport
    sport_books_result = await db.execute(
        select(
            Game.sport_id,
            Line.sportsbook,
            func.count(Line.id).label("count"),
        )
        .join(Game, Line.game_id == Game.id)
        .where(Line.is_current == True)
        .group_by(Game.sport_id, Line.sportsbook)
        .order_by(Game.sport_id, func.count(Line.id).desc())
    )
    
    by_sport = {}
    for row in sport_books_result.all():
        sport_id = row[0]
        sport_key = SPORT_ID_TO_KEY.get(sport_id, f"unknown_{sport_id}")
        if sport_key not in by_sport:
            by_sport[sport_key] = {"sport_id": sport_id, "books": []}
        by_sport[sport_key]["books"].append({
            "sportsbook": row[1],
            "line_count": row[2],
        })
    
    total_books = len(sportsbooks)
    
    return {
        "status": "ok" if total_books > 1 else "warning",
        "total_unique_sportsbooks": total_books,
        "sportsbooks": sportsbooks,
        "by_sport": by_sport,
        "notes": [
            "Expected: 5+ sportsbooks (DraftKings, FanDuel, BetMGM, Caesars, PointsBet)",
            "If only 1 sportsbook: data was synced before multi-book stub fix",
            "Fix: Call /admin/jobs/force-refresh?sport=basketball_nba to re-sync",
        ] if total_books <= 1 else [
            f"Found {total_books} sportsbooks - multi-book data is working correctly",
        ]
    }


@router.get("/verify/players-by-sport")
async def verify_players_by_sport(
    db: AsyncSession = Depends(get_db),
):
    """
    List sample players by sport_id to debug NFL/NCAAF data bleed.
    
    Shows first 10 players for each sport so you can verify:
    - NFL (31) players are NFL players (Mahomes, Allen, etc.)
    - NCAAF (41) players are college players (not NFL starters)
    """
    from sqlalchemy import select
    from app.models import Player, Sport
    from app.core.constants import SPORT_ID_TO_KEY
    
    results = {}
    
    # Check NFL (31) and NCAAF (41) specifically
    for sport_id in [31, 41]:
        sport_key = SPORT_ID_TO_KEY.get(sport_id, "UNKNOWN")
        
        # Get sample players
        players_result = await db.execute(
            select(Player.id, Player.name, Player.external_player_id)
            .where(Player.sport_id == sport_id)
            .limit(10)
        )
        players = [
            {"id": p[0], "name": p[1], "external_id": p[2]}
            for p in players_result.all()
        ]
        
        results[f"sport_{sport_id}_{sport_key}"] = {
            "sport_id": sport_id,
            "sport_key": sport_key,
            "player_count": len(players),
            "sample_players": players,
        }
    
    return {
        "status": "ok",
        "players_by_sport": results,
        "notes": [
            "If NFL players (Mahomes, Allen, etc.) appear under sport_id=41 (NCAAF), there's a data issue",
            "NCAAF should have college player names or be empty (off-season)",
        ]
    }


# =============================================================================
# Data Freshness Diagnostic Endpoint
# =============================================================================

@router.get("/debug/data-freshness")
async def debug_data_freshness(
    db: AsyncSession = Depends(get_db),
):
    """
    Comprehensive data freshness diagnostic for troubleshooting.
    
    Shows per-sport:
    - Last sync time
    - Games count (today vs total)
    - Props/lines count
    - Picks count
    - Staleness status
    - Data source (API vs stubs)
    
    Use this to diagnose:
    - Why a sport isn't showing data
    - If data is stale
    - If syncs are failing silently
    """
    from sqlalchemy import select, func, and_
    from datetime import datetime, timezone, timedelta
    from app.models import Sport, Game, Line, ModelPick, SyncMetadata
    from app.core.constants import SPORT_ID_TO_KEY
    from app.core.sport_availability import get_sport_status
    
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today_start + timedelta(days=1)
    
    results = []
    
    # Check each sport in our mapping
    for sport_id, sport_key in SPORT_ID_TO_KEY.items():
        # Get sport from DB
        sport_result = await db.execute(
            select(Sport).where(Sport.id == sport_id)
        )
        sport = sport_result.scalar_one_or_none()
        
        # Get sync metadata
        sync_result = await db.execute(
            select(SyncMetadata)
            .where(
                and_(
                    SyncMetadata.sport_key == sport_key,
                    SyncMetadata.data_type == "games",
                )
            )
            .order_by(SyncMetadata.last_updated.desc())
            .limit(1)
        )
        sync_meta = sync_result.scalar_one_or_none()
        
        # Count games (total and today)
        total_games = await db.scalar(
            select(func.count())
            .select_from(Game)
            .where(Game.sport_id == sport_id)
        ) or 0
        
        today_games = await db.scalar(
            select(func.count())
            .select_from(Game)
            .where(
                and_(
                    Game.sport_id == sport_id,
                    Game.start_time >= today_start,
                    Game.start_time < tomorrow,
                )
            )
        ) or 0
        
        upcoming_games = await db.scalar(
            select(func.count())
            .select_from(Game)
            .where(
                and_(
                    Game.sport_id == sport_id,
                    Game.start_time >= now.replace(tzinfo=None),
                    Game.start_time < (now + timedelta(days=7)).replace(tzinfo=None),
                )
            )
        ) or 0
        
        # Count props/lines
        props_count = await db.scalar(
            select(func.count())
            .select_from(Line)
            .join(Game, Line.game_id == Game.id)
            .where(
                and_(
                    Game.sport_id == sport_id,
                    Line.is_current == True,
                    Line.player_id.isnot(None),
                )
            )
        ) or 0
        
        # Count picks
        picks_count = await db.scalar(
            select(func.count())
            .select_from(ModelPick)
            .where(
                and_(
                    ModelPick.sport_id == sport_id,
                    ModelPick.is_active == True,
                )
            )
        ) or 0
        
        # Calculate staleness
        last_sync = None
        staleness = "unknown"
        data_source = None
        
        if sync_meta:
            last_sync = sync_meta.last_updated.isoformat() if sync_meta.last_updated else None
            data_source = sync_meta.source
            
            if sync_meta.last_updated:
                age_hours = (now.replace(tzinfo=None) - sync_meta.last_updated).total_seconds() / 3600
                if age_hours < 1:
                    staleness = "fresh"
                elif age_hours < 4:
                    staleness = "recent"
                elif age_hours < 12:
                    staleness = "stale"
                else:
                    staleness = "very_stale"
        
        # Get sport availability status
        sport_status = get_sport_status(sport_key)
        
        results.append({
            "sport_id": sport_id,
            "sport_key": sport_key,
            "exists_in_db": sport is not None,
            "db_name": sport.name if sport else None,
            "season_status": sport_status["status"],
            "is_active_season": sport_status["is_active"],
            "counts": {
                "total_games": total_games,
                "today_games": today_games,
                "upcoming_games": upcoming_games,
                "active_props": props_count,
                "active_picks": picks_count,
            },
            "sync": {
                "last_sync": last_sync,
                "staleness": staleness,
                "data_source": data_source,
            },
            "alerts": _get_sport_alerts(
                sport_key, sport_status, today_games, props_count, picks_count, staleness
            ),
        })
    
    # Sort by alert severity
    results.sort(key=lambda x: len(x["alerts"]), reverse=True)
    
    return {
        "timestamp": now.isoformat(),
        "sports": results,
        "summary": {
            "total_sports": len(results),
            "sports_with_alerts": sum(1 for r in results if r["alerts"]),
            "sports_with_data": sum(1 for r in results if r["counts"]["today_games"] > 0),
            "stale_sports": sum(1 for r in results if r["sync"]["staleness"] in ("stale", "very_stale")),
        },
    }


def _get_sport_alerts(
    sport_key: str,
    sport_status: dict,
    today_games: int,
    props_count: int,
    picks_count: int,
    staleness: str,
) -> list[str]:
    """Generate alerts for a sport based on data health."""
    alerts = []
    
    # Active season but no games
    if sport_status["is_active"] and today_games == 0:
        alerts.append(f"Sport is in-season but has 0 games for today")
    
    # Has games but no props
    if today_games > 0 and props_count == 0:
        alerts.append(f"Has {today_games} games but 0 props - sync may have failed")
    
    # Has props but no picks
    if props_count > 0 and picks_count == 0:
        alerts.append(f"Has {props_count} props but 0 picks - picks generation may have failed")
    
    # Stale data
    if staleness in ("stale", "very_stale"):
        alerts.append(f"Data is {staleness} - needs refresh")
    
    # Unknown staleness
    if staleness == "unknown":
        alerts.append("Never synced or no sync metadata")
    
    return alerts


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


@router.get("/metrics/dashboard")
async def get_metrics_dashboard(
    db: AsyncSession = Depends(get_db),
):
    """
    Comprehensive metrics dashboard for monitoring system health.
    
    Returns:
    - Request metrics (total, error rate, latency)
    - Database metrics (picks, games, lines counts)
    - API quota status
    - Circuit breaker status
    - Top slowest endpoints
    """
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import select, func
    from app.core.logging import request_metrics
    from app.core.resilience import CircuitBreakerRegistry
    from app.models import ModelPick, Game, Line, Sport
    
    # Get request metrics
    req_metrics = request_metrics.get_metrics()
    
    # Get circuit breaker status
    circuit_status = CircuitBreakerRegistry.get_status()
    
    # Get database counts
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Count active picks generated today
    picks_today_result = await db.execute(
        select(func.count(ModelPick.id)).where(
            ModelPick.generated_at >= today_start
        )
    )
    picks_today = picks_today_result.scalar() or 0
    
    # Count total active picks
    total_picks_result = await db.execute(
        select(func.count(ModelPick.id)).where(ModelPick.is_active == True)
    )
    total_active_picks = total_picks_result.scalar() or 0
    
    # Count games
    total_games_result = await db.execute(select(func.count(Game.id)))
    total_games = total_games_result.scalar() or 0
    
    # Count sports
    sports_result = await db.execute(select(Sport))
    sports = sports_result.scalars().all()
    
    # Get quota status
    quota_status = get_quota_status()
    
    return {
        "timestamp": now.isoformat(),
        "request_metrics": {
            "total_requests": req_metrics.get("total_requests", 0),
            "total_errors": req_metrics.get("total_errors", 0),
            "error_rate_pct": req_metrics.get("error_rate_pct", 0),
            "avg_duration_ms": req_metrics.get("avg_duration_ms", 0),
            "top_endpoints": req_metrics.get("endpoints", {}),
        },
        "database_metrics": {
            "picks_generated_today": picks_today,
            "total_active_picks": total_active_picks,
            "total_games": total_games,
            "sports": [{"id": s.id, "name": s.name} for s in sports],
        },
        "api_metrics": {
            "odds_api_quota_remaining": quota_status.get("remaining", 0),
            "odds_api_quota_used": quota_status.get("used", 0),
        },
        "circuit_breakers": circuit_status,
        "health_summary": {
            "all_breakers_closed": all(
                info.get("state") != "open"
                for info in circuit_status.values()
            ) if circuit_status else True,
            "quota_healthy": quota_status.get("remaining", 0) > 20,
            "error_rate_healthy": req_metrics.get("error_rate_pct", 0) < 5,
        },
    }


@router.post("/metrics/reset")
async def reset_request_metrics():
    """Reset request metrics counters (for testing)."""
    from app.core.logging import request_metrics
    request_metrics.reset()
    return {"status": "reset", "message": "Request metrics have been reset"}


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


@router.post("/jobs/sync-injuries-espn")
async def sync_injuries_from_espn(
    sport: str = Query("basketball_nba", description="Sport key to sync"),
    db: AsyncSession = Depends(get_db),
):
    """
    Sync injuries from ESPN (free, no API key needed).
    
    This fetches injury data from ESPN's public API and saves it directly
    to the Injury database table. Use this when INJURY_API_KEY is not configured.
    """
    from app.services.etl_injuries import sync_espn_injuries_to_db
    
    start_time = time.time()
    
    try:
        result = await sync_espn_injuries_to_db(db, sport)
        duration_ms = int((time.time() - start_time) * 1000)
        
        if "error" in result:
            return {
                "job": "sync-injuries-espn",
                "status": "error",
                "sport": sport,
                "duration_ms": duration_ms,
                "error": result["error"],
            }
        
        return {
            "job": "sync-injuries-espn",
            "status": "success",
            "sport": sport,
            "duration_ms": duration_ms,
            "counts": result,
        }
    
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"ESPN injury sync failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "job": "sync-injuries-espn",
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


# =============================================================================
# Cache Management Endpoints
# =============================================================================

@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get in-memory cache statistics.
    
    Returns:
    - Hit/miss rates
    - Entry counts
    - Expiration stats
    
    Useful for monitoring cache effectiveness.
    """
    from app.services.memory_cache import cache
    
    return {
        "stats": cache.get_stats(),
        "entries": cache.get_entries_info()[:50],  # Top 50 by hits
    }


@router.post("/cache/clear")
async def clear_cache(
    key_prefix: Optional[str] = Query(None, description="Clear only keys with this prefix"),
):
    """
    Clear the in-memory cache.
    
    Options:
    - No prefix: Clear everything
    - With prefix: Clear only matching keys (e.g., 'picks' clears all picks)
    """
    from app.services.memory_cache import cache
    
    if key_prefix:
        count = cache.invalidate_prefix(key_prefix)
        return {
            "status": "partial_clear",
            "prefix": key_prefix,
            "entries_cleared": count,
        }
    else:
        count = cache.clear()
        return {
            "status": "full_clear",
            "entries_cleared": count,
        }


@router.post("/cache/cleanup")
async def cleanup_expired_cache():
    """
    Remove expired entries from cache.
    
    This runs automatically in the background, but can be triggered manually.
    """
    from app.services.memory_cache import cache
    
    count = await cache.cleanup_expired()
    return {
        "status": "cleanup_complete",
        "entries_removed": count,
    }


# =============================================================================
# Dashboard Endpoints
# =============================================================================

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
):
    """
    Get per-sport data health summary for admin dashboard.
    
    Returns for each sport:
    - game_count: Games scheduled in next 24 hours
    - prop_count: Current player prop lines
    - book_count: Unique sportsbooks with lines
    - last_update: Most recent line fetch time
    - status: ok/warn/error based on health checks
    - issues: List of detected problems
    
    Use this to monitor:
    - Games > 0 but props = 0: ETL or mapping issue
    - Books <= 1: Single-book data (DK-only)
    - last_update > 10 min: Stale odds data
    """
    try:
        from datetime import timedelta
        from sqlalchemy import select, func, case, and_
        from app.models import Game, Line
        from app.config.sports import SPORT_ID_TO_KEY
        
        now_utc = datetime.now(timezone.utc)
        # Use naive datetimes for DB comparison (DB stores naive UTC)
        now_naive = now_utc.replace(tzinfo=None)
        cutoff = now_utc - timedelta(minutes=10)
        next_24h = now_naive + timedelta(hours=24)
        
        sport_ids = list(SPORT_ID_TO_KEY.keys())
        
        # --- Bulk query 1: game counts per sport (next 24h) ---
        game_rows = await db.execute(
            select(Game.sport_id, func.count(Game.id))
            .where(
                and_(
                    Game.sport_id.in_(sport_ids),
                    Game.start_time >= now_naive,
                    Game.start_time <= next_24h,
                )
            )
            .group_by(Game.sport_id)
        )
        game_counts: dict[int, int] = {row[0]: row[1] for row in game_rows.all()}
        
        # --- Bulk query 2: prop counts, book counts, last_update per sport ---
        line_rows = await db.execute(
            select(
                Game.sport_id,
                func.sum(case((Line.player_id.isnot(None), 1), else_=0)),
                func.count(func.distinct(Line.sportsbook)),
                func.max(Line.fetched_at),
            )
            .select_from(Line)
            .join(Game, Line.game_id == Game.id)
            .where(
                and_(
                    Game.sport_id.in_(sport_ids),
                    Line.is_current == True,
                )
            )
            .group_by(Game.sport_id)
        )
        line_data: dict[int, tuple] = {
            row[0]: (row[1] or 0, row[2] or 0, row[3]) for row in line_rows.all()
        }
        
        # --- Build response rows ---
        rows = []
        for sport_id, sport_key in SPORT_ID_TO_KEY.items():
            sport_key_str = sport_key.value if hasattr(sport_key, 'value') else str(sport_key)
            
            game_count = game_counts.get(sport_id, 0)
            prop_count, book_count, last_update_result = line_data.get(sport_id, (0, 0, None))
            
            # Determine status and issues
            status = "ok"
            issues = []
            
            if game_count > 0 and prop_count == 0:
                status = "error"
                issues.append("Games today but no props")
            
            if book_count == 0 and game_count > 0:
                status = "error" if status != "error" else status
                issues.append("No sportsbook data")
            elif book_count == 1:
                status = "warn" if status == "ok" else status
                issues.append("Single-book market (DK-only?)")
            
            if last_update_result:
                # Make timezone-aware comparison safe
                last_update_tz = last_update_result
                if last_update_result.tzinfo is None:
                    last_update_tz = last_update_result.replace(tzinfo=timezone.utc)
                if last_update_tz < cutoff:
                    status = "warn" if status == "ok" else status
                    minutes_stale = int((now_utc - last_update_tz).total_seconds() / 60)
                    issues.append(f"Odds stale ({minutes_stale} min)")
            
            rows.append({
                "sport_id": sport_id,
                "sport_key": sport_key_str,
                "game_count": game_count,
                "prop_count": int(prop_count),
                "book_count": int(book_count),
                "last_update": last_update_result.isoformat() if last_update_result else None,
                "status": status,
                "issues": issues,
            })
        
        # Sort by sport_id for consistent ordering
        rows.sort(key=lambda x: x["sport_id"])
        
        return {
            "now": now_utc.isoformat(),
            "sports": rows,
        }
    
    except Exception as e:
        logger.error(
            "dashboard_summary_error",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Dashboard query failed: {type(e).__name__}: {str(e)}"
        )
