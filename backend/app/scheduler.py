"""Async background task scheduler for ETL jobs.

Uses native asyncio for background tasks instead of APScheduler
for better integration with FastAPI's async ecosystem.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Any
from zoneinfo import ZoneInfo

from app.core.config import get_settings
from app.core.database import get_session_maker

# Eastern timezone (handles DST automatically)
EASTERN_TZ = ZoneInfo("America/New_York")

logger = logging.getLogger(__name__)

# Store running tasks for graceful shutdown
_background_tasks: List[asyncio.Task] = []


# =============================================================================
# Sport Keys
# =============================================================================

SPORT_KEYS = [
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
    "soccer_uefa_europa",
    "soccer_uefa_conference",
    # MMA/UFC
    "mma_mixed_martial_arts",
]

# =============================================================================
# Smart Polling Windows (optimized for peak betting hours, stays under free tier)
# =============================================================================

# Smart sync hours in ET - peak betting windows
# 9 AM, 12 PM, 3 PM, 5 PM, 6 PM, 7 PM ET
SMART_SYNC_HOURS_ET = [9, 12, 15, 17, 18, 19]

# Convert to UTC (ET is UTC-5 in winter, UTC-4 in summer - handled dynamically)
# These are approximate for documentation; actual conversion happens at runtime
MORNING_SYNC_HOUR_UTC = 14  # ~9 AM ET (for backward compat)
PREGAME_SYNC_HOUR_UTC = 22  # ~5 PM ET (for backward compat)


# =============================================================================
# Core Refresh Functions
# =============================================================================

async def refresh_all_picks(sport_keys: List[str] | None = None) -> dict[str, Any]:
    """
    Refresh picks for all (or specified) sports.
    
    Args:
        sport_keys: List of sports to refresh, or None for all
    
    Returns:
        Dictionary with refresh results per sport
    """
    from app.services.picks_generator import generate_picks
    
    sports = sport_keys or SPORT_KEYS
    results = {}
    session_maker = get_session_maker()
    
    for sport_key in sports:
        try:
            async with session_maker() as db:
                result = await generate_picks(
                    db,
                    sport_key,
                    min_ev=0.0,
                    min_confidence=0.5,
                    use_stubs=True,
                )
                results[sport_key] = result
                logger.info(f"Refreshed picks for {sport_key}: {result}")
        except Exception as e:
            logger.error(f"Error refreshing picks for {sport_key}: {e}")
            results[sport_key] = {"error": str(e)}
    
    return results


async def update_historical_data() -> dict[str, Any]:
    """
    Update historical performance data for all players.
    
    Returns:
        Dictionary with update summary
    """
    from app.services.data_updater import update_historical_stats
    
    session_maker = get_session_maker()
    
    try:
        async with session_maker() as db:
            result = await update_historical_stats(db)
            logger.info(f"Updated historical data: {result}")
            return result
    except Exception as e:
        logger.error(f"Error updating historical data: {e}")
        return {"error": str(e)}


async def check_game_results_all() -> dict[str, Any]:
    """
    Check game results and update picks for all sports.
    
    Returns:
        Dictionary with results per sport
    """
    from app.services.data_updater import check_game_results
    
    results = {}
    session_maker = get_session_maker()
    
    for sport_key in SPORT_KEYS:
        try:
            async with session_maker() as db:
                result = await check_game_results(db, sport_key)
                results[sport_key] = result
                logger.info(f"Checked results for {sport_key}: {result}")
        except Exception as e:
            logger.error(f"Error checking results for {sport_key}: {e}")
            results[sport_key] = {"error": str(e)}
    
    return results


# =============================================================================
# Background Task Loops
# =============================================================================

async def daily_refresh_loop(refresh_hour: int = 9):
    """
    Background task that runs a full refresh at specified hour (EST).
    
    Args:
        refresh_hour: Hour to run daily refresh (24h format, EST)
    """
    logger.info(f"Daily refresh loop started (runs at {refresh_hour}:00 EST)")
    
    while True:
        try:
            # Calculate time until next refresh
            now = datetime.now(timezone.utc)
            # Use proper Eastern timezone (handles DST automatically)
            now_est = now.astimezone(EASTERN_TZ)
            
            # Target time today
            target = now_est.replace(
                hour=refresh_hour,
                minute=0,
                second=0,
                microsecond=0,
            )
            
            # If we've passed the time today, schedule for tomorrow
            if now_est >= target:
                target += timedelta(days=1)
            
            # Wait until target time
            wait_seconds = (target - now_est).total_seconds()
            logger.info(f"Next daily refresh in {wait_seconds/3600:.1f} hours")
            await asyncio.sleep(wait_seconds)
            
            # Run the refresh
            logger.info("=== DAILY REFRESH STARTING ===")
            
            # 1. Archive old picks (cleanup before refresh)
            from app.services.data_updater import archive_old_picks
            session_maker = get_session_maker()
            async with session_maker() as db:
                archive_result = await archive_old_picks(db, days_old=7)
                logger.info(f"Archived old picks: {archive_result}")
            
            # 2. Check yesterday's game results
            results_summary = await check_game_results_all()
            logger.info(f"Game results check: {results_summary}")
            
            # 3. Update historical data
            historical_summary = await update_historical_data()
            logger.info(f"Historical update: {historical_summary}")
            
            # 4. Refresh all picks for today
            picks_summary = await refresh_all_picks()
            logger.info(f"Picks refresh: {picks_summary}")
            
            logger.info("=== DAILY REFRESH COMPLETE ===")
            
        except asyncio.CancelledError:
            logger.info("Daily refresh loop cancelled")
            break
        except Exception as e:
            logger.error(f"Daily refresh loop error: {e}", exc_info=True)
            # Wait an hour before retrying on error
            await asyncio.sleep(3600)


async def daily_calibration_loop(calibration_hour: int = 10):
    """
    Background task that computes and stores calibration metrics daily.
    
    Runs after the daily refresh to ensure all results are settled,
    then computes calibration metrics for the previous day's picks.
    
    Args:
        calibration_hour: Hour to run calibration (24h format, EST)
    """
    from datetime import date
    from app.services.calibration_service import (
        compute_calibration_metrics,
        store_calibration_metrics,
    )
    
    logger.info(f"Daily calibration loop started (runs at {calibration_hour}:00 EST)")
    
    while True:
        try:
            # Calculate time until next calibration run
            now = datetime.now(timezone.utc)
            # Use proper Eastern timezone (handles DST automatically)
            now_est = now.astimezone(EASTERN_TZ)
            
            # Target time today
            target = now_est.replace(
                hour=calibration_hour,
                minute=0,
                second=0,
                microsecond=0,
            )
            
            # If we've passed the time today, schedule for tomorrow
            if now_est >= target:
                target += timedelta(days=1)
            
            # Wait until target time
            wait_seconds = (target - now_est).total_seconds()
            logger.info(f"Next calibration run in {wait_seconds/3600:.1f} hours")
            await asyncio.sleep(wait_seconds)
            
            # Run the calibration
            logger.info("=== DAILY CALIBRATION STARTING ===")
            
            session_maker = get_session_maker()
            
            # Calculate metrics for yesterday's settled picks
            yesterday = date.today() - timedelta(days=1)
            
            async with session_maker() as db:
                for sport_key in SPORT_KEYS:
                    try:
                        # Compute metrics for the last 7 days to capture any late settlements
                        metrics = await compute_calibration_metrics(
                            db,
                            sport_key,
                            start_date=yesterday - timedelta(days=6),
                            end_date=yesterday,
                        )
                        
                        if metrics:
                            stored = await store_calibration_metrics(
                                db,
                                sport_key,
                                metrics_date=yesterday,
                                metrics=metrics,
                            )
                            logger.info(f"Stored {stored} calibration metrics for {sport_key}")
                        else:
                            logger.info(f"No settled picks to calibrate for {sport_key}")
                            
                    except Exception as e:
                        logger.error(f"Error computing calibration for {sport_key}: {e}")
            
            logger.info("=== DAILY CALIBRATION COMPLETE ===")
            
        except asyncio.CancelledError:
            logger.info("Daily calibration loop cancelled")
            break
        except Exception as e:
            logger.error(f"Daily calibration loop error: {e}", exc_info=True)
            # Wait an hour before retrying on error
            await asyncio.sleep(3600)


async def hourly_odds_check_loop(interval_minutes: int = 60):
    """
    Background task that checks for line movements hourly.
    
    Args:
        interval_minutes: Check interval in minutes
    """
    from app.services.data_updater import check_line_movements
    
    logger.info(f"Hourly odds check loop started (every {interval_minutes} min)")
    
    # Initial delay to stagger with other tasks
    await asyncio.sleep(120)
    
    while True:
        try:
            logger.info("Checking for line movements...")
            session_maker = get_session_maker()
            
            async with session_maker() as db:
                result = await check_line_movements(db, hours_back=1)
                logger.info(f"Line movement check: {result.get('picks_checked', 0)} picks checked")
            
        except asyncio.CancelledError:
            logger.info("Hourly odds check loop cancelled")
            break
        except Exception as e:
            logger.error(f"Hourly odds check error: {e}", exc_info=True)
        
        await asyncio.sleep(interval_minutes * 60)


async def odds_sync_loop(interval_minutes: int, initial_delay: int = 0, use_stubs: bool = True):
    """
    DEPRECATED: Use quota_safe_sync_loop instead for production.
    
    Background task that syncs games, lines, and injuries on interval.
    WARNING: Running this frequently will exhaust free tier API quotas.
    
    Args:
        interval_minutes: Sync interval in minutes
        initial_delay: Delay before first sync in seconds
        use_stubs: If True, use stub data instead of real API calls
    """
    from app.services import sync_games_and_lines, sync_injuries

    if initial_delay > 0:
        logger.info(f"Odds sync loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)

    logger.info(f"Odds sync loop started (interval: {interval_minutes} min, use_stubs={use_stubs})")
    logger.warning("WARNING: Frequent interval syncing may exhaust API quota. Consider quota_safe_sync_loop.")

    while True:
        try:
            logger.info("Running odds/injuries sync...")
            session_maker = get_session_maker()
            
            async with session_maker() as db:
                # Sync games and lines for NBA (with player props)
                games_result = await sync_games_and_lines(
                    db, "basketball_nba", include_props=True, use_stubs=use_stubs
                )
                logger.info(f"NBA Games/lines sync: {games_result}")

                # Sync injuries for NBA
                injuries_result = await sync_injuries(db, "basketball_nba", use_stubs=use_stubs)
                logger.info(f"NBA Injuries sync: {injuries_result}")
                
                # Sync games and lines for NCAAB (with player props)
                ncaab_games_result = await sync_games_and_lines(
                    db, "basketball_ncaab", include_props=True, use_stubs=use_stubs
                )
                logger.info(f"NCAAB Games/lines sync: {ncaab_games_result}")

            logger.info("Odds/injuries sync completed")

        except asyncio.CancelledError:
            logger.info("Odds sync loop cancelled")
            break
        except Exception as e:
            logger.error(f"Odds sync loop error: {e}", exc_info=True)

        # Wait for next interval
        await asyncio.sleep(interval_minutes * 60)


async def quota_safe_sync_loop(initial_delay: int = 60, use_stubs: bool = False):
    """
    Smart polling sync that runs on startup + during peak betting windows.
    
    Uses smart windows (6x/day during peak hours) to keep data fresh while
    staying under 500/month free tier (~360 calls/month + manual refreshes).
    
    Features:
    - IMMEDIATE sync on startup (ensures data is available right away)
    - Smart polling windows during peak betting hours (9AM-7PM ET)
    - Pre-sync snapshots for data versioning (morning only)
    - Post-sync health checks with alerting
    - Automatic failover between providers
    - Respects SCHEDULER_USE_STUBS environment variable
    
    Schedule (all times ET):
    - On startup: Immediate sync after initial_delay
    - 9 AM ET: Morning sync - overnight line movements
    - 12 PM ET: Midday sync - lunch time updates
    - 3 PM ET: Afternoon sync - early game prep
    - 5 PM ET: Pre-game sync - final lines
    - 6 PM ET: Tip-off sync - last minute movements
    - 7 PM ET: Evening sync - late game coverage
    
    Args:
        initial_delay: Delay before first sync check in seconds
        use_stubs: If True, force stub data regardless of API quota
    """
    from app.services.etl_games_and_lines import sync_with_fallback, clear_stale_games
    from app.services.odds_provider import get_quota_status
    from app.services.snapshot_service import (
        pre_refresh_snapshot,
        post_sync_validation,
    )
    from app.services.sync_metadata_service import record_sync
    import time
    
    if initial_delay > 0:
        logger.info(f"Quota-safe sync loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)
    
    logger.info(f"Smart polling sync started (windows at {SMART_SYNC_HOURS_ET} ET)")
    
    # Track if this is the first run (for immediate startup sync)
    is_first_run = True
    
    # Sync window names for logging
    SYNC_WINDOW_NAMES = {
        9: "MORNING",
        12: "MIDDAY",
        15: "AFTERNOON",
        17: "PRE-GAME",
        18: "TIP-OFF",
        19: "EVENING",
    }
    
    while True:
        try:
            # Get current time in Eastern
            now_et = datetime.now(EASTERN_TZ)
            current_hour_et = now_et.hour
            
            # On first run, do an immediate sync instead of waiting
            if is_first_run:
                sync_name = "STARTUP"
                is_first_run = False
                logger.info("=== STARTUP SYNC: Running immediate sync to populate data ===")
            else:
                # Find next sync window in ET
                next_sync_hour_et = None
                for hour in SMART_SYNC_HOURS_ET:
                    if hour > current_hour_et:
                        next_sync_hour_et = hour
                        break
                
                # If no more windows today, use first window tomorrow
                if next_sync_hour_et is None:
                    next_sync_hour_et = SMART_SYNC_HOURS_ET[0]
                    # Target is tomorrow
                    target_et = now_et.replace(
                        hour=next_sync_hour_et, minute=0, second=0, microsecond=0
                    ) + timedelta(days=1)
                else:
                    target_et = now_et.replace(
                        hour=next_sync_hour_et, minute=0, second=0, microsecond=0
                    )
                
                sync_name = SYNC_WINDOW_NAMES.get(next_sync_hour_et, f"WINDOW_{next_sync_hour_et}")
                
                # Calculate wait time
                wait_seconds = (target_et - now_et).total_seconds()
                if wait_seconds < 0:
                    wait_seconds = 0
                
                logger.info(
                    f"Next {sync_name} sync in {wait_seconds/3600:.1f} hours "
                    f"(at {target_et.strftime('%I:%M %p ET')})"
                )
                
                # Wait until sync time
                await asyncio.sleep(wait_seconds)
            
            # Run the sync
            logger.info(f"=== {sync_name} SMART SYNC STARTING ===")
            
            session_maker = get_session_maker()
            health_issues = []
            
            async with session_maker() as db:
                # 1. Save pre-sync snapshots (versioned backups) - only on first sync of day (9 AM)
                if sync_name == "MORNING" or sync_name == "STARTUP":
                    logger.info("Saving pre-refresh snapshots...")
                    snapshot_result = await pre_refresh_snapshot(db, SPORT_KEYS)
                    logger.info(f"Snapshots saved: {snapshot_result}")
                
                # 2. Determine whether to use real API or stubs
                quota = get_quota_status()
                logger.info(f"API quota status: {quota['used']} used, {quota['remaining']} remaining")
                
                if use_stubs:
                    # SCHEDULER_USE_STUBS=true forces stub data
                    logger.info("SCHEDULER_USE_STUBS=true, forcing stub data (no API calls)")
                    use_real_api = False
                elif quota['remaining'] < 20:
                    logger.warning(f"Low quota ({quota['remaining']} remaining), using stubs only")
                    use_real_api = False
                else:
                    use_real_api = True
                
                # 3. Sync each sport with failover (upsert mode - no pre-clear)
                # NOTE: We don't clear games before sync anymore to prevent data loss
                # if the API fails. Games are upserted (add new, update existing).
                for sport_key in SPORT_KEYS:
                    sync_start = time.time()
                    try:
                        result = await sync_with_fallback(
                            db, 
                            sport_key, 
                            include_props=True,
                            use_real_api=use_real_api,
                        )
                        sync_duration = time.time() - sync_start
                        logger.info(f"{sport_key} sync result: {result}")
                        
                        # 4. Post-sync health check
                        health_result = await post_sync_validation(db, sport_key, result)
                        is_healthy = not health_result.get("alert_triggered", False)
                        
                        if not is_healthy:
                            health_issues.append({
                                "sport": sport_key,
                                "issues": health_result["health_check"]["issues"],
                            })
                        
                        # 5. Record sync metadata for "last updated" tracking
                        games_count = result.get("games_added", 0) + result.get("games_updated", 0)
                        await record_sync(
                            db,
                            sport_key=sport_key,
                            data_type="games",
                            games_count=games_count,
                            lines_count=result.get("lines_added", 0),
                            props_count=result.get("props_added", 0),
                            picks_count=result.get("picks_generated", 0),
                            source=result.get("source", "unknown"),
                            sync_duration_seconds=round(sync_duration, 2),
                            is_healthy=is_healthy,
                        )
                        
                        # 6. Sanity check: Alert on zero games (indicates stale schedule or API issue)
                        if games_count == 0:
                            # Check if it's a normal game day (NBA/NCAAB typically have games most days)
                            from datetime import date as date_type
                            today = date_type.today()
                            is_weekday = today.weekday() < 5  # Mon-Fri
                            
                            if sport_key in ["basketball_nba", "basketball_ncaab"] and is_weekday:
                                logger.error(
                                    f"ALERT: Zero games synced for {sport_key} on {today.isoformat()} - "
                                    f"check schedule data file or API response! Source: {result.get('source', 'unknown')}"
                                )
                            else:
                                logger.warning(
                                    f"No games for {sport_key} on {today.isoformat()} - "
                                    f"may be off-day or offseason"
                                )
                            
                    except Exception as e:
                        sync_duration = time.time() - sync_start
                        logger.error(f"Error syncing {sport_key}: {e}")
                        health_issues.append({
                            "sport": sport_key,
                            "issues": [f"Sync exception: {str(e)[:100]}"],
                        })
                        
                        # Record failed sync
                        await record_sync(
                            db,
                            sport_key=sport_key,
                            data_type="games",
                            source="failed",
                            sync_duration_seconds=round(sync_duration, 2),
                            error_message=str(e)[:500],
                            is_healthy=False,
                        )
            
            # Log updated quota
            quota = get_quota_status()
            logger.info(f"Post-sync quota: {quota['used']} used, {quota['remaining']} remaining")
            
            # Generate detailed summary
            logger.info("=" * 60)
            logger.info(f"{sync_name} SYNC SUMMARY")
            logger.info("=" * 60)
            
            # Get fresh metadata for summary
            async with session_maker() as db_summary:
                from app.services.sync_metadata_service import get_all_sync_status
                status = await get_all_sync_status(db_summary)
                
                for sport_key, sport_data in status.items():
                    games_meta = sport_data["data_types"].get("games", {})
                    if games_meta:
                        logger.info(
                            f"  {sport_data['display_name']:8} | "
                            f"Games: {games_meta.get('games_count', 0):3} | "
                            f"Lines: {games_meta.get('lines_count', 0):4} | "
                            f"Props: {games_meta.get('props_count', 0):4} | "
                            f"Source: {games_meta.get('source', 'N/A'):10} | "
                            f"Healthy: {'YES' if games_meta.get('is_healthy') else 'NO'}"
                        )
                    else:
                        logger.info(f"  {sport_data['display_name']:8} | No sync data")
            
            logger.info("-" * 60)
            
            # 6. Generate picks for all synced sports
            logger.info("Generating picks for all sports...")
            from app.services.picks_generator import generate_picks
            picks_summary = {}
            
            async with session_maker() as db_picks:
                for sport_key in SPORT_KEYS:
                    try:
                        picks_result = await generate_picks(
                            db_picks,
                            sport_key,
                            min_ev=0.0,
                            min_confidence=0.5,
                            use_stubs=True,
                        )
                        picks_summary[sport_key] = picks_result.get("picks_created", 0)
                        logger.info(f"  {sport_key}: {picks_result.get('picks_created', 0)} picks generated")
                    except Exception as e:
                        logger.error(f"  {sport_key}: Error generating picks: {e}")
                        picks_summary[sport_key] = 0
            
            logger.info(f"Picks generation complete: {picks_summary}")
            
            # Invalidate cache after picks generation
            try:
                from app.services.memory_cache import invalidate_all_picks
                invalidated = await invalidate_all_picks()
                if invalidated > 0:
                    logger.info(f"Invalidated {invalidated} cache entries after picks generation")
            except Exception as cache_error:
                logger.warning(f"Failed to invalidate cache: {cache_error}")
            
            # 7. Send Discord alerts for high-EV picks (if webhook configured)
            try:
                from app.services.alerts_service import (
                    alert_sync_complete,
                    process_picks_for_alerts,
                    HIGH_EV_THRESHOLD,
                )
                from app.models import ModelPick, Player, Market, Sport
                
                # For each sport, find high-EV picks and send alerts
                async with session_maker() as db_alerts:
                    total_high_ev = 0
                    
                    for sport_key in SPORT_KEYS:
                        # Get sport display name
                        sport_name = {
                            "basketball_nba": "NBA",
                            "basketball_ncaab": "NCAAB",
                            "americanfootball_nfl": "NFL",
                        }.get(sport_key, sport_key)
                        
                        # Query high-EV picks from this sync
                        from sqlalchemy import select
                        result = await db_alerts.execute(
                            select(ModelPick, Player, Market)
                            .join(Player, ModelPick.player_id == Player.id, isouter=True)
                            .join(Market, ModelPick.market_id == Market.id)
                            .where(
                                ModelPick.is_active == True,
                                ModelPick.expected_value >= HIGH_EV_THRESHOLD,
                            )
                        )
                        high_ev_picks = result.all()
                        
                        # Convert to dict format for alert processing
                        picks_for_alert = []
                        for pick, player, market in high_ev_picks:
                            picks_for_alert.append({
                                "player_name": player.name if player else "Unknown",
                                "stat_type": market.stat_type or market.market_type,
                                "line": pick.line_value,
                                "side": pick.side,
                                "odds": pick.odds,
                                "expected_value": pick.expected_value,
                                "model_probability": pick.model_probability,
                            })
                        
                        if picks_for_alert:
                            alert_result = await process_picks_for_alerts(picks_for_alert, sport_name)
                            total_high_ev += alert_result["high_ev_count"]
                            logger.info(f"Discord alerts for {sport_name}: {alert_result}")
                    
                    # Send sync complete summary
                    total_games = sum(status.get(sk, {}).get("data_types", {}).get("games", {}).get("games_count", 0) for sk in SPORT_KEYS) if 'status' in dir() else 0
                    total_props = sum(status.get(sk, {}).get("data_types", {}).get("games", {}).get("props_count", 0) for sk in SPORT_KEYS) if 'status' in dir() else 0
                    total_picks = sum(picks_summary.values())
                    
                    # Note: Only send sync complete for significant syncs
                    if total_games > 0 or total_picks > 0:
                        await alert_sync_complete(
                            sport="ALL",
                            games_synced=total_games,
                            props_synced=total_props,
                            picks_generated=total_picks,
                            high_ev_count=total_high_ev,
                            duration_ms=int((time.time() - sync_start) * 1000) if 'sync_start' in dir() else 0,
                        )
                        
            except Exception as alert_error:
                logger.warning(f"Failed to send Discord alerts: {alert_error}")
            
            # Final status
            if health_issues:
                logger.warning(f"=== {sync_name} SYNC COMPLETE WITH ISSUES ===")
                for issue in health_issues:
                    logger.warning(f"  {issue['sport']}: {issue['issues']}")
                
                # Alert on critical issues (low game counts for game days)
                for issue in health_issues:
                    if "games" in str(issue['issues']).lower():
                        logger.error(f"ALERT: Low game count detected for {issue['sport']} - check API/data source!")
            else:
                logger.info(f"=== {sync_name} QUOTA-SAFE SYNC COMPLETE (all healthy) ===")
            
        except asyncio.CancelledError:
            logger.info("Quota-safe sync loop cancelled")
            break
        except Exception as e:
            logger.error(f"Quota-safe sync loop error: {e}", exc_info=True)
            # Wait an hour before retrying on error
            await asyncio.sleep(3600)


async def stats_sync_loop(interval_minutes: int, initial_delay: int = 30, use_stubs: bool = True):
    """
    Background task that syncs player statistics on interval.
    
    Runs:
    - sync_recent_player_stats (fetches recent game logs for active players)
    
    Args:
        interval_minutes: Sync interval in minutes
        initial_delay: Delay before first sync in seconds
        use_stubs: If True, use stub data instead of real API calls
    """
    from app.services import sync_recent_player_stats

    if initial_delay > 0:
        logger.info(f"Stats sync loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)

    logger.info(f"Stats sync loop started (interval: {interval_minutes} min, use_stubs={use_stubs})")

    while True:
        try:
            logger.info("Running stats sync...")
            session_maker = get_session_maker()

            async with session_maker() as db:
                # Sync recent player stats for NBA
                stats_result = await sync_recent_player_stats(
                    db, 
                    sport_key="basketball_nba",
                    games_back=10,
                    use_stubs=use_stubs,
                )
                logger.info(f"Stats sync: {stats_result}")

            logger.info("Stats sync completed")

        except asyncio.CancelledError:
            logger.info("Stats sync loop cancelled")
            break
        except Exception as e:
            logger.error(f"Stats sync loop error: {e}", exc_info=True)

        # Wait for next interval
        await asyncio.sleep(interval_minutes * 60)


async def model_generation_loop(interval_minutes: int, initial_delay: int = 60, use_stubs: bool = True):
    """
    Background task that generates model picks on interval.
    
    Runs:
    - generate_model_picks_for_today (computes probabilities and creates picks)
    
    Args:
        interval_minutes: Generation interval in minutes
        initial_delay: Delay before first generation in seconds
        use_stubs: If True, use stub probability generator
    """
    from app.services import generate_model_picks_for_today

    if initial_delay > 0:
        logger.info(f"Model generation loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)

    logger.info(f"Model generation loop started (interval: {interval_minutes} min, use_stubs={use_stubs})")

    while True:
        try:
            logger.info("Running model pick generation...")
            session_maker = get_session_maker()

            async with session_maker() as db:
                # Generate picks for NBA
                picks_result = await generate_model_picks_for_today(
                    db,
                    sport_key="basketball_nba",
                    ev_threshold=0.03,  # 3% minimum EV
                    confidence_threshold=0.4,  # 40% minimum confidence
                    use_stubs=use_stubs,
                )
                logger.info(f"Model picks: {picks_result}")

            logger.info("Model pick generation completed")

        except asyncio.CancelledError:
            logger.info("Model generation loop cancelled")
            break
        except Exception as e:
            logger.error(f"Model generation loop error: {e}", exc_info=True)

        # Wait for next interval
        await asyncio.sleep(interval_minutes * 60)


async def roster_sync_loop(interval_hours: int = 24, initial_delay: int = 120, use_stubs: bool = True):
    """
    Background task that syncs player rosters daily.
    
    Runs:
    - sync_rosters (updates player-team relationships from roster API)
    
    Args:
        interval_hours: Sync interval in hours (default: 24 = daily)
        initial_delay: Initial delay in seconds before first run
        use_stubs: If True, use stub data instead of real API calls
    """
    from app.services import sync_rosters

    if initial_delay > 0:
        logger.info(f"Roster sync loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)

    logger.info(f"Roster sync loop started (interval: {interval_hours} hours, use_stubs={use_stubs})")

    while True:
        try:
            logger.info("Running roster sync...")
            session_maker = get_session_maker()

            async with session_maker() as db:
                # Sync rosters for NBA
                roster_result = await sync_rosters(
                    db,
                    sport_key="basketball_nba",
                    use_stubs=use_stubs,
                )
                logger.info(f"Roster sync: {roster_result}")

            logger.info("Roster sync completed")

        except asyncio.CancelledError:
            logger.info("Roster sync loop cancelled")
            break
        except Exception as e:
            logger.error(f"Roster sync loop error: {e}", exc_info=True)

        # Wait for next interval (in hours)
        await asyncio.sleep(interval_hours * 3600)


async def historical_odds_sync_loop(interval_hours: int = 24, initial_delay: int = 300):
    """
    Background task that syncs historical odds from OddsPapi daily.
    
    Fetches historical odds movements for analytics and trend analysis.
    
    Args:
        interval_hours: Sync interval in hours (default: 24 = daily)
        initial_delay: Initial delay in seconds before first run
    """
    from app.services.etl_historical import sync_historical_odds
    from app.core.config import get_settings
    
    settings = get_settings()
    
    # Only run if OddsPapi API key is configured
    if not settings.oddspapi_api_key:
        logger.info("OddsPapi API key not configured, historical odds sync disabled")
        return
    
    if initial_delay > 0:
        logger.info(f"Historical odds sync loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)
    
    logger.info(f"Historical odds sync loop started (interval: {interval_hours} hours)")
    
    while True:
        try:
            logger.info("Running historical odds sync from OddsPapi...")
            session_maker = get_session_maker()
            
            async with session_maker() as db:
                result = await sync_historical_odds(
                    db,
                    sport_key="basketball_nba",
                    days_back=7,
                )
                logger.info(f"Historical odds sync: {result}")
            
            logger.info("Historical odds sync completed")
            
        except asyncio.CancelledError:
            logger.info("Historical odds sync loop cancelled")
            break
        except Exception as e:
            logger.error(f"Historical odds sync loop error: {e}", exc_info=True)
        
        # Wait for next interval (in hours)
        await asyncio.sleep(interval_hours * 3600)


async def oddspapi_results_sync_loop(interval_minutes: int = 60, initial_delay: int = 240):
    """
    Background task that syncs game results from OddsPapi hourly.
    
    Fetches final scores and settlements for completed games.
    
    Args:
        interval_minutes: Sync interval in minutes
        initial_delay: Initial delay in seconds before first run
    """
    from app.services.etl_historical import sync_game_results, settle_picks
    from app.core.config import get_settings
    
    settings = get_settings()
    
    # Only run if OddsPapi API key is configured
    if not settings.oddspapi_api_key:
        logger.info("OddsPapi API key not configured, results sync disabled")
        return
    
    if initial_delay > 0:
        logger.info(f"OddsPapi results sync loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)
    
    logger.info(f"OddsPapi results sync loop started (interval: {interval_minutes} min)")
    
    while True:
        try:
            logger.info("Running game results sync from OddsPapi...")
            session_maker = get_session_maker()
            
            async with session_maker() as db:
                # 1. Sync game results
                results_sync = await sync_game_results(
                    db,
                    sport_key="basketball_nba",
                    days_back=3,
                )
                logger.info(f"Game results sync: {results_sync}")
                
                # 2. Settle picks based on results
                settlement_result = await settle_picks(
                    db,
                    sport_key="basketball_nba",
                )
                logger.info(f"Pick settlement: {settlement_result}")
            
            logger.info("OddsPapi results sync completed")
            
        except asyncio.CancelledError:
            logger.info("OddsPapi results sync loop cancelled")
            break
        except Exception as e:
            logger.error(f"OddsPapi results sync loop error: {e}", exc_info=True)
        
        # Wait for next interval
        await asyncio.sleep(interval_minutes * 60)


async def results_settlement_loop(interval_minutes: int = 30, initial_delay: int = 180, use_stubs: bool = True):
    """
    Background task that settles picks for completed games.
    
    Checks for games with status "final" that have unsettled picks,
    then calculates hit/miss for each pick and updates player hit rates.
    
    Args:
        interval_minutes: Check interval in minutes
        initial_delay: Initial delay in seconds before first run
        use_stubs: If True, simulate game results for testing
    """
    from sqlalchemy import select, and_
    from app.models import Game, ModelPick, PickResult
    from app.services.results_tracker import ResultsTracker

    if initial_delay > 0:
        logger.info(f"Results settlement loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)

    logger.info(f"Results settlement loop started (interval: {interval_minutes} min, use_stubs={use_stubs})")

    while True:
        try:
            logger.info("Checking for games to settle...")
            session_maker = get_session_maker()
            tracker = ResultsTracker(use_stubs=use_stubs)

            async with session_maker() as db:
                # Find games to settle
                if use_stubs:
                    # For stub mode: find games that started 3+ hours ago (treat as "completed")
                    from datetime import datetime, timedelta, timezone
                    cutoff_time = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=3)
                    games_result = await db.execute(
                        select(Game.id)
                        .where(Game.start_time < cutoff_time)
                    )
                    logger.info(f"Stub mode: looking for games started before {cutoff_time}")
                else:
                    # For real mode: find games with final status
                    games_result = await db.execute(
                        select(Game.id)
                        .where(Game.status == "final")
                    )
                
                game_ids_to_settle = [row[0] for row in games_result.all()]
                
                if not game_ids_to_settle:
                    logger.info("No games found to settle")
                else:
                    # For each game, check if there are unsettled picks
                    total_settled = 0
                    total_hits = 0
                    total_misses = 0
                    logger.info(f"Found {len(game_ids_to_settle)} games to check for settlement")
                    
                    for game_id in game_ids_to_settle:
                        # Check if game has unsettled picks
                        unsettled_result = await db.execute(
                            select(ModelPick.id)
                            .outerjoin(PickResult, ModelPick.id == PickResult.pick_id)
                            .where(
                                and_(
                                    ModelPick.game_id == game_id,
                                    ModelPick.player_id.isnot(None),
                                    PickResult.id.is_(None),
                                )
                            )
                            .limit(1)
                        )
                        
                        if unsettled_result.first():
                            # Settle the game
                            if use_stubs:
                                result = await tracker.simulate_game_results(db, game_id)
                            else:
                                result = await tracker.settle_picks_for_game(db, game_id)
                            
                            settled = result.get("settled", 0)
                            hits = result.get("hits", 0)
                            misses = result.get("misses", 0)
                            
                            total_settled += settled
                            total_hits += hits
                            total_misses += misses
                            
                            logger.info(f"Settled game {game_id}: {hits}/{settled} hits")
                    
                    if total_settled > 0:
                        hit_rate = total_hits / total_settled if total_settled > 0 else 0
                        logger.info(f"Settlement complete: {total_settled} picks, {hit_rate:.1%} hit rate")
                    else:
                        logger.info("No unsettled picks found")

        except asyncio.CancelledError:
            logger.info("Results settlement loop cancelled")
            break
        except Exception as e:
            logger.error(f"Results settlement loop error: {e}", exc_info=True)

        # Wait for next interval
        await asyncio.sleep(interval_minutes * 60)


async def _seed_stub_hit_rates_once(initial_delay: int = 90):
    """
    One-shot task: wait for initial sync to populate players/picks,
    then seed PlayerHitRate and PlayerMarketHitRate tables so the
    Stats tab has data immediately in stub mode.
    """
    from app.services.results_tracker import seed_stub_hit_rates
    from app.core.constants import SPORT_ID_TO_KEY

    if initial_delay > 0:
        logger.info(f"Stub hit rate seeder starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)

    try:
        session_maker = get_session_maker()
        async with session_maker() as db:
            # Seed for all sports that have picks
            for sport_id in SPORT_ID_TO_KEY:
                result = await seed_stub_hit_rates(db, sport_id=sport_id)
                if result.get("seeded"):
                    logger.info(f"Seeded hit rates for sport {sport_id}: {result}")
        logger.info("Stub hit rate seeding complete")
    except Exception as e:
        logger.error(f"Stub hit rate seeding failed: {e}", exc_info=True)


# =============================================================================
# NFL Scheduler Loops
# =============================================================================

async def nfl_odds_sync_loop(interval_minutes: int = 60, initial_delay: int = 60):
    """
    Background task that syncs NFL odds hourly.
    
    Uses cascade: OddsAPI -> BetStack -> JSON backup
    
    Args:
        interval_minutes: Sync interval in minutes
        initial_delay: Initial delay in seconds before first run
    """
    from app.services.nfl_odds_service import sync_nfl_odds
    
    if initial_delay > 0:
        logger.info(f"NFL odds sync loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)
    
    logger.info(f"NFL odds sync loop started (interval: {interval_minutes} min)")
    
    while True:
        try:
            logger.info("Running NFL odds sync...")
            session_maker = get_session_maker()
            
            async with session_maker() as db:
                result = await sync_nfl_odds(db)
                logger.info(f"NFL odds sync: fetched {result.get('records_fetched', 0)} from {result.get('fetch_source', 'unknown')}")
            
            logger.info("NFL odds sync completed")
            
        except asyncio.CancelledError:
            logger.info("NFL odds sync loop cancelled")
            break
        except Exception as e:
            logger.error(f"NFL odds sync loop error: {e}", exc_info=True)
        
        await asyncio.sleep(interval_minutes * 60)


async def nfl_snapshot_loop(snapshot_hour: int = 6, initial_delay: int = 120):
    """
    Background task that creates daily NFL odds snapshots.
    
    Runs at the specified hour each day (EST).
    
    Args:
        snapshot_hour: Hour to run snapshot (24h format, EST)
        initial_delay: Initial delay in seconds before first check
    """
    from datetime import timezone, timedelta
    from app.services.nfl_odds_service import create_daily_snapshot
    from app.services.nfl_backup import save_backup
    
    if initial_delay > 0:
        logger.info(f"NFL snapshot loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)
    
    logger.info(f"NFL snapshot loop started (runs at {snapshot_hour}:00 EST)")
    
    while True:
        try:
            # Calculate time until next snapshot
            now = datetime.now(timezone.utc)
            # Use proper Eastern timezone (handles DST automatically)
            now_est = now.astimezone(EASTERN_TZ)
            
            target = now_est.replace(
                hour=snapshot_hour,
                minute=0,
                second=0,
                microsecond=0,
            )
            
            if now_est >= target:
                target += timedelta(days=1)
            
            wait_seconds = (target - now_est).total_seconds()
            logger.info(f"Next NFL snapshot in {wait_seconds/3600:.1f} hours")
            await asyncio.sleep(wait_seconds)
            
            # Run the snapshot
            logger.info("=== NFL DAILY SNAPSHOT STARTING ===")
            session_maker = get_session_maker()
            
            async with session_maker() as db:
                # Create historical snapshot
                snapshot_result = await create_daily_snapshot(db)
                logger.info(f"NFL snapshot: {snapshot_result}")
                
                # Get live odds for JSON backup
                from app.services.nfl_odds_service import get_live_odds
                live_odds = await get_live_odds(db)
                
                if live_odds:
                    backup_path = save_backup(live_odds)
                    logger.info(f"NFL backup saved: {backup_path}")
            
            logger.info("=== NFL DAILY SNAPSHOT COMPLETE ===")
            
        except asyncio.CancelledError:
            logger.info("NFL snapshot loop cancelled")
            break
        except Exception as e:
            logger.error(f"NFL snapshot loop error: {e}", exc_info=True)
            # Wait an hour before retrying on error
            await asyncio.sleep(3600)


# =============================================================================
# NCAAB Scheduler Loops
# =============================================================================

async def ncaab_odds_sync_loop(interval_minutes: int = 60, initial_delay: int = 75):
    """
    Background task that syncs NCAAB odds hourly.
    
    Uses cascade: OddsAPI -> BetStack -> JSON backup
    
    Args:
        interval_minutes: Sync interval in minutes
        initial_delay: Initial delay in seconds before first run
    """
    from app.services.ncaab_odds_service import sync_ncaab_odds
    
    if initial_delay > 0:
        logger.info(f"NCAAB odds sync loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)
    
    logger.info(f"NCAAB odds sync loop started (interval: {interval_minutes} min)")
    
    while True:
        try:
            logger.info("Running NCAAB odds sync...")
            session_maker = get_session_maker()
            
            async with session_maker() as db:
                result = await sync_ncaab_odds(db)
                logger.info(f"NCAAB odds sync: fetched {result.get('records_fetched', 0)} from {result.get('fetch_source', 'unknown')}")
            
            logger.info("NCAAB odds sync completed")
            
        except asyncio.CancelledError:
            logger.info("NCAAB odds sync loop cancelled")
            break
        except Exception as e:
            logger.error(f"NCAAB odds sync loop error: {e}", exc_info=True)
        
        await asyncio.sleep(interval_minutes * 60)


async def ncaab_snapshot_loop(snapshot_hour: int = 6, initial_delay: int = 135):
    """
    Background task that creates daily NCAAB odds snapshots.
    
    Runs at the specified hour each day (EST).
    
    Args:
        snapshot_hour: Hour to run snapshot (24h format, EST)
        initial_delay: Initial delay in seconds before first check
    """
    from datetime import timezone, timedelta
    from app.services.ncaab_odds_service import create_daily_snapshot
    from app.services.ncaab_backup import save_backup
    
    if initial_delay > 0:
        logger.info(f"NCAAB snapshot loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)
    
    logger.info(f"NCAAB snapshot loop started (runs at {snapshot_hour}:00 EST)")
    
    while True:
        try:
            # Calculate time until next snapshot
            now = datetime.now(timezone.utc)
            # Use proper Eastern timezone (handles DST automatically)
            now_est = now.astimezone(EASTERN_TZ)
            
            target = now_est.replace(
                hour=snapshot_hour,
                minute=0,
                second=0,
                microsecond=0,
            )
            
            if now_est >= target:
                target += timedelta(days=1)
            
            wait_seconds = (target - now_est).total_seconds()
            logger.info(f"Next NCAAB snapshot in {wait_seconds/3600:.1f} hours")
            await asyncio.sleep(wait_seconds)
            
            # Run the snapshot
            logger.info("=== NCAAB DAILY SNAPSHOT STARTING ===")
            session_maker = get_session_maker()
            
            async with session_maker() as db:
                # Create historical snapshot
                snapshot_result = await create_daily_snapshot(db)
                logger.info(f"NCAAB snapshot: {snapshot_result}")
                
                # Get live odds for JSON backup
                from app.services.ncaab_odds_service import get_live_odds
                live_odds = await get_live_odds(db)
                
                if live_odds:
                    backup_path = save_backup(live_odds)
                    logger.info(f"NCAAB backup saved: {backup_path}")
            
            logger.info("=== NCAAB DAILY SNAPSHOT COMPLETE ===")
            
        except asyncio.CancelledError:
            logger.info("NCAAB snapshot loop cancelled")
            break
        except Exception as e:
            logger.error(f"NCAAB snapshot loop error: {e}", exc_info=True)
            # Wait an hour before retrying on error
            await asyncio.sleep(3600)


# =============================================================================
# Watchlist Alert Loop
# =============================================================================

async def watchlist_alert_loop(interval_minutes: int = 15, initial_delay: int = 60):
    """
    Background task that checks watchlists and sends Discord alerts for new matches.
    
    Args:
        interval_minutes: Check interval in minutes (default: 15)
        initial_delay: Initial delay in seconds before first check
    """
    from app.services.watchlist_alert_service import check_watchlists_and_alert
    
    if initial_delay > 0:
        logger.info(f"Watchlist alert loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)
    
    logger.info(f"Watchlist alert loop started (interval: {interval_minutes} min)")
    
    while True:
        try:
            logger.info("Checking watchlists for new matches...")
            session_maker = get_session_maker()
            
            async with session_maker() as db:
                result = await check_watchlists_and_alert(db)
                if result.get("alerts_sent", 0) > 0:
                    logger.info(
                        f"Watchlist alerts: {result['alerts_sent']} sent, "
                        f"{result['total_new_matches']} new matches"
                    )
            
        except asyncio.CancelledError:
            logger.info("Watchlist alert loop cancelled")
            break
        except Exception as e:
            logger.error(f"Watchlist alert loop error: {e}", exc_info=True)
        
        # Wait for next interval
        await asyncio.sleep(interval_minutes * 60)


# =============================================================================
# Autonomous Brain Loop
# =============================================================================

async def _brain_loop(interval_minutes: int = 5, initial_delay: int = 90):
    """Wrapper that lazily imports and runs the brain loop."""
    from app.services.brain import brain_loop
    await brain_loop(interval_minutes=interval_minutes, initial_delay=initial_delay)


# =============================================================================
# Scheduler Control Functions
# =============================================================================

def start_background_tasks() -> List[asyncio.Task]:
    """
    Start all background ETL tasks.
    
    Returns list of task handles for later cancellation.
    """
    global _background_tasks

    settings = get_settings()
    
    # Safety guard: check if scheduler is enabled
    if not settings.scheduler_enabled:
        logger.info("Scheduler disabled via SCHEDULER_ENABLED=false - no background tasks started")
        return []
    
    tasks = []
    
    # Get use_stubs setting (default True for scheduled tasks)
    use_stubs = getattr(settings, 'scheduler_use_stubs', True)
    logger.info(f"Scheduler use_stubs={use_stubs}")

    # Daily refresh task (9 AM EST)
    daily_hour = getattr(settings, 'daily_refresh_hour', 9)
    task_daily = asyncio.create_task(
        daily_refresh_loop(refresh_hour=daily_hour),
        name="daily_refresh_loop"
    )
    tasks.append(task_daily)
    logger.info(f"Created daily_refresh_loop task (runs at {daily_hour}:00 EST)")

    # Hourly odds check task
    hourly_interval = getattr(settings, 'hourly_check_interval', 60)
    task_hourly = asyncio.create_task(
        hourly_odds_check_loop(interval_minutes=hourly_interval),
        name="hourly_odds_check_loop"
    )
    tasks.append(task_hourly)
    logger.info(f"Created hourly_odds_check_loop task (every {hourly_interval} min)")

    # Quota-safe odds sync task (2x daily: 6 AM + 5 PM ET)
    # Replaces frequent odds_sync_loop to protect API free tier quota
    task1 = asyncio.create_task(
        quota_safe_sync_loop(initial_delay=30, use_stubs=use_stubs),
        name="quota_safe_sync_loop"
    )
    tasks.append(task1)
    logger.info(f"Created quota_safe_sync_loop task (2x daily at 6 AM + 5 PM ET, use_stubs={use_stubs})")

    # Stats sync task
    task2 = asyncio.create_task(
        stats_sync_loop(
            interval_minutes=settings.sched_stats_interval_min,
            initial_delay=30,  # Stagger start by 30 seconds
            use_stubs=use_stubs,
        ),
        name="stats_sync_loop"
    )
    tasks.append(task2)
    logger.info(f"Created stats_sync_loop task (every {settings.sched_stats_interval_min} min, use_stubs={use_stubs})")

    # Model generation task
    task3 = asyncio.create_task(
        model_generation_loop(
            interval_minutes=settings.sched_model_interval_min,
            initial_delay=60,  # Stagger start by 60 seconds
            use_stubs=use_stubs,
        ),
        name="model_generation_loop"
    )
    tasks.append(task3)
    logger.info(f"Created model_generation_loop task (every {settings.sched_model_interval_min} min, use_stubs={use_stubs})")

    # Roster sync task (daily)
    roster_interval_hours = getattr(settings, 'sched_roster_interval_hours', 24)
    task4 = asyncio.create_task(
        roster_sync_loop(
            interval_hours=roster_interval_hours,
            initial_delay=120,  # Stagger start by 2 minutes
            use_stubs=use_stubs,
        ),
        name="roster_sync_loop"
    )
    tasks.append(task4)
    logger.info(f"Created roster_sync_loop task (every {roster_interval_hours} hours, use_stubs={use_stubs})")

    # Results settlement task (checks for completed games and settles picks)
    settlement_interval = getattr(settings, 'sched_settlement_interval_min', 30)
    task5 = asyncio.create_task(
        results_settlement_loop(
            interval_minutes=settlement_interval,
            initial_delay=180,  # Stagger start by 3 minutes
            use_stubs=use_stubs,
        ),
        name="results_settlement_loop"
    )
    tasks.append(task5)
    logger.info(f"Created results_settlement_loop task (every {settlement_interval} min, use_stubs={use_stubs})")

    # Seed stub hit rates (one-shot, runs after initial sync populates players/picks)
    if use_stubs:
        task_seed = asyncio.create_task(
            _seed_stub_hit_rates_once(initial_delay=90),
            name="seed_stub_hit_rates"
        )
        tasks.append(task_seed)
        logger.info("Created seed_stub_hit_rates one-shot task (90s delay)")

    # Daily calibration task (runs at 10 AM EST, after settlement has time to process)
    calibration_hour = getattr(settings, 'calibration_hour', 10)
    task_calibration = asyncio.create_task(
        daily_calibration_loop(calibration_hour=calibration_hour),
        name="daily_calibration_loop"
    )
    tasks.append(task_calibration)
    logger.info(f"Created daily_calibration_loop task (runs at {calibration_hour}:00 EST)")

    # OddsPapi historical odds sync task (daily)
    # Only starts if ODDSPAPI_API_KEY is configured
    if settings.oddspapi_api_key:
        task6 = asyncio.create_task(
            historical_odds_sync_loop(
                interval_hours=24,
                initial_delay=300,  # Stagger start by 5 minutes
            ),
            name="historical_odds_sync_loop"
        )
        tasks.append(task6)
        logger.info("Created historical_odds_sync_loop task (daily)")
        
        # OddsPapi game results sync task (hourly)
        task7 = asyncio.create_task(
            oddspapi_results_sync_loop(
                interval_minutes=60,
                initial_delay=240,  # Stagger start by 4 minutes
            ),
            name="oddspapi_results_sync_loop"
        )
        tasks.append(task7)
        logger.info("Created oddspapi_results_sync_loop task (hourly)")
    else:
        logger.info("OddsPapi tasks skipped (no API key configured)")

    # NFL odds sync task (hourly)
    nfl_sync_interval = getattr(settings, 'nfl_sync_interval_min', 60)
    task_nfl_sync = asyncio.create_task(
        nfl_odds_sync_loop(
            interval_minutes=nfl_sync_interval,
            initial_delay=90,  # Stagger start
        ),
        name="nfl_odds_sync_loop"
    )
    tasks.append(task_nfl_sync)
    logger.info(f"Created nfl_odds_sync_loop task (every {nfl_sync_interval} min)")
    
    # NFL daily snapshot task
    nfl_snapshot_hour = getattr(settings, 'nfl_snapshot_hour', 6)
    task_nfl_snapshot = asyncio.create_task(
        nfl_snapshot_loop(
            snapshot_hour=nfl_snapshot_hour,
            initial_delay=120,  # Stagger start
        ),
        name="nfl_snapshot_loop"
    )
    tasks.append(task_nfl_snapshot)
    logger.info(f"Created nfl_snapshot_loop task (daily at {nfl_snapshot_hour}:00 EST)")

    # NCAAB odds sync task (hourly)
    ncaab_sync_interval = getattr(settings, 'ncaab_sync_interval_min', 60)
    task_ncaab_sync = asyncio.create_task(
        ncaab_odds_sync_loop(
            interval_minutes=ncaab_sync_interval,
            initial_delay=75,  # Stagger start
        ),
        name="ncaab_odds_sync_loop"
    )
    tasks.append(task_ncaab_sync)
    logger.info(f"Created ncaab_odds_sync_loop task (every {ncaab_sync_interval} min)")
    
    # NCAAB daily snapshot task
    ncaab_snapshot_hour = getattr(settings, 'ncaab_snapshot_hour', 6)
    task_ncaab_snapshot = asyncio.create_task(
        ncaab_snapshot_loop(
            snapshot_hour=ncaab_snapshot_hour,
            initial_delay=135,  # Stagger start
        ),
        name="ncaab_snapshot_loop"
    )
    tasks.append(task_ncaab_snapshot)
    logger.info(f"Created ncaab_snapshot_loop task (daily at {ncaab_snapshot_hour}:00 EST)")
    
    # Watchlist alert loop (checks every 15 minutes for new matches)
    watchlist_interval = getattr(settings, 'watchlist_alert_interval_min', 15)
    task_watchlist = asyncio.create_task(
        watchlist_alert_loop(
            interval_minutes=watchlist_interval,
            initial_delay=60,  # Start after initial sync
        ),
        name="watchlist_alert_loop"
    )
    tasks.append(task_watchlist)
    logger.info(f"Created watchlist_alert_loop task (every {watchlist_interval} min)")

    # Autonomous brain loop (self-monitoring, self-healing, self-optimizing)
    brain_interval = getattr(settings, 'brain_interval_min', 5)
    task_brain = asyncio.create_task(
        _brain_loop(interval_minutes=brain_interval, initial_delay=90),
        name="brain_loop"
    )
    tasks.append(task_brain)
    logger.info(f"Created brain_loop task (every {brain_interval} min)")

    _background_tasks = tasks
    return tasks


async def stop_background_tasks(tasks: List[asyncio.Task] | None = None):
    """
    Stop all background tasks gracefully.
    
    Args:
        tasks: List of tasks to cancel. If None, uses global task list.
    """
    global _background_tasks

    tasks_to_cancel = tasks if tasks is not None else _background_tasks

    if not tasks_to_cancel:
        logger.info("No background tasks to stop")
        return

    logger.info(f"Stopping {len(tasks_to_cancel)} background tasks...")

    for task in tasks_to_cancel:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info(f"Task {task.get_name()} cancelled")
        except Exception as e:
            logger.error(f"Error cancelling task {task.get_name()}: {e}")

    _background_tasks = []
    logger.info("All background tasks stopped")


def get_background_tasks() -> List[asyncio.Task]:
    """Get list of currently running background tasks."""
    return _background_tasks


def get_scheduler_status() -> dict[str, Any]:
    """Get current scheduler status."""
    tasks = get_background_tasks()
    return {
        "enabled": get_settings().scheduler_enabled,
        "tasks_running": len(tasks),
        "tasks": [
            {
                "name": t.get_name(),
                "done": t.done(),
                "cancelled": t.cancelled(),
            }
            for t in tasks
        ],
    }


# =============================================================================
# Legacy compatibility (for existing code that may import these)
# =============================================================================

def start_scheduler():
    """Legacy function - now starts asyncio background tasks."""
    settings = get_settings()
    if settings.scheduler_enabled:
        start_background_tasks()
    else:
        logger.info("Scheduler disabled via SCHEDULER_ENABLED=false")


def shutdown_scheduler():
    """Legacy function - schedules task cancellation."""
    # Note: This is synchronous but tasks will be cleaned up on app shutdown
    for task in _background_tasks:
        task.cancel()
    logger.info("Scheduler shutdown requested")


def get_scheduler():
    """Legacy function - returns None (no APScheduler)."""
    return None
