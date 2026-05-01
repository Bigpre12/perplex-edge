# apps/api/src/services/seed_scheduler.py
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from services.prizepicks_collector import run_collector
from services.results_grader import run_grader
from services.hit_rate_updater import run_hit_rate_update

logger = logging.getLogger(__name__)

async def run_seed_pipeline():
    """
    Executes the full PrizePicks -> Grader -> Hit Rate pipeline.
    This can be triggered manually or via scheduler.
    """
    logger.info("SEED PIPELINE: Starting full execution...")
    try:
        # Step 1: Collect latest projections from PrizePicks
        await run_collector()
        
        # Step 2: Grade projections where games have finished (BallDontLie)
        await run_grader()
        
        # Step 3: Recompute rolling hit rates for the Monte Carlo engine
        await run_hit_rate_update()
        
        logger.info("SEED PIPELINE: Successfully completed all stages.")
    except Exception as e:
        logger.error(f"SEED PIPELINE: Critical failure in pipeline: {e}", exc_info=True)

def setup_seed_scheduler(scheduler: AsyncIOScheduler):
    """
    Register the seed pipeline job in the existing APScheduler.
    Runs every night at 3:00 AM CT.
    """
    logger.info("SEED PIPELINE: Configuring nightly cron (3:00 AM CT / America/Chicago)...")
    
    try:
        scheduler.add_job(
            run_seed_pipeline,
            CronTrigger(hour=3, minute=0, timezone="America/Chicago"),
            id="nightly_seed_pipeline",
            name="PrizePicks Board & Results Pipeline",
            replace_existing=True
        )
    except Exception as e:
        logger.error(f"SEED PIPELINE: Failed to register scheduler job: {e}")
