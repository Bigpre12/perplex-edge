"""Async background task scheduler for ETL jobs.

Uses native asyncio for background tasks instead of APScheduler
for better integration with FastAPI's async ecosystem.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Any

from app.core.config import get_settings
from app.core.database import get_session_maker

logger = logging.getLogger(__name__)

# Store running tasks for graceful shutdown
_background_tasks: List[asyncio.Task] = []


# =============================================================================
# Sport Keys
# =============================================================================

SPORT_KEYS = [
    "basketball_nba",
    "americanfootball_nfl",
]


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
            # EST is UTC-5 (ignoring DST for simplicity)
            est_offset = timedelta(hours=-5)
            now_est = now + est_offset
            
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
            
            # 1. Check yesterday's game results
            results_summary = await check_game_results_all()
            logger.info(f"Game results check: {results_summary}")
            
            # 2. Update historical data
            historical_summary = await update_historical_data()
            logger.info(f"Historical update: {historical_summary}")
            
            # 3. Refresh all picks for today
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


async def odds_sync_loop(interval_minutes: int, initial_delay: int = 0):
    """
    Background task that syncs games, lines, and injuries on interval.
    
    Runs:
    - sync_games_and_lines (fetches games and odds)
    - sync_injuries (fetches injury data)
    """
    from app.services import sync_games_and_lines, sync_injuries

    if initial_delay > 0:
        logger.info(f"Odds sync loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)

    logger.info(f"Odds sync loop started (interval: {interval_minutes} min)")

    while True:
        try:
            logger.info("Running odds/injuries sync...")
            session_maker = get_session_maker()
            
            async with session_maker() as db:
                # Sync games and lines for NBA
                games_result = await sync_games_and_lines(db, "basketball_nba")
                logger.info(f"Games/lines sync: {games_result}")

                # Sync injuries for NBA
                injuries_result = await sync_injuries(db, "basketball_nba")
                logger.info(f"Injuries sync: {injuries_result}")

            logger.info("Odds/injuries sync completed")

        except asyncio.CancelledError:
            logger.info("Odds sync loop cancelled")
            break
        except Exception as e:
            logger.error(f"Odds sync loop error: {e}", exc_info=True)

        # Wait for next interval
        await asyncio.sleep(interval_minutes * 60)


async def stats_sync_loop(interval_minutes: int, initial_delay: int = 30):
    """
    Background task that syncs player statistics on interval.
    
    Runs:
    - sync_recent_player_stats (fetches recent game logs for active players)
    """
    from app.services import sync_recent_player_stats

    if initial_delay > 0:
        logger.info(f"Stats sync loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)

    logger.info(f"Stats sync loop started (interval: {interval_minutes} min)")

    while True:
        try:
            logger.info("Running stats sync...")
            session_maker = get_session_maker()

            async with session_maker() as db:
                # Sync recent player stats for NBA
                stats_result = await sync_recent_player_stats(
                    db, 
                    sport_key="basketball_nba",
                    n_games=10
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


async def model_generation_loop(interval_minutes: int, initial_delay: int = 60):
    """
    Background task that generates model picks on interval.
    
    Runs:
    - generate_model_picks_for_today (computes probabilities and creates picks)
    """
    from app.services import generate_model_picks_for_today

    if initial_delay > 0:
        logger.info(f"Model generation loop starting in {initial_delay}s...")
        await asyncio.sleep(initial_delay)

    logger.info(f"Model generation loop started (interval: {interval_minutes} min)")

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
    tasks = []

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

    # Odds/injuries sync task
    task1 = asyncio.create_task(
        odds_sync_loop(
            interval_minutes=settings.sched_odds_interval_min,
            initial_delay=0,
        ),
        name="odds_sync_loop"
    )
    tasks.append(task1)
    logger.info(f"Created odds_sync_loop task (every {settings.sched_odds_interval_min} min)")

    # Stats sync task
    task2 = asyncio.create_task(
        stats_sync_loop(
            interval_minutes=settings.sched_stats_interval_min,
            initial_delay=30,  # Stagger start by 30 seconds
        ),
        name="stats_sync_loop"
    )
    tasks.append(task2)
    logger.info(f"Created stats_sync_loop task (every {settings.sched_stats_interval_min} min)")

    # Model generation task
    task3 = asyncio.create_task(
        model_generation_loop(
            interval_minutes=settings.sched_model_interval_min,
            initial_delay=60,  # Stagger start by 60 seconds
        ),
        name="model_generation_loop"
    )
    tasks.append(task3)
    logger.info(f"Created model_generation_loop task (every {settings.sched_model_interval_min} min)")

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
