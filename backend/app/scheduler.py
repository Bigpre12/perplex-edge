"""Async background task scheduler for ETL jobs.

Uses native asyncio for background tasks instead of APScheduler
for better integration with FastAPI's async ecosystem.
"""

import asyncio
import logging
from typing import List

from app.core.config import get_settings
from app.core.database import get_session_maker

logger = logging.getLogger(__name__)

# Store running tasks for graceful shutdown
_background_tasks: List[asyncio.Task] = []


# =============================================================================
# Background Task Loops
# =============================================================================

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
