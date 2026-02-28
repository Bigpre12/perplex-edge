import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from jobs.ingestion_service import ingest_all_odds, ingest_all_props, run_steam_scout, run_clv_snapshot

logger = logging.getLogger(__name__)

# Singleton scheduler
scheduler = AsyncIOScheduler()

def start_ingestion_scheduler():
    """Start the 24/7 ingestion scheduler."""
    logger.info("Initializing 24/7 Ingestion Scheduler...")
    
    # Every 4 minutes — fresh odds for game state
    scheduler.add_job(ingest_all_odds, 'interval', minutes=4, id='ingest_odds')

    # Every 4 minutes — detailed player props
    scheduler.add_job(ingest_all_props, 'interval', minutes=4, id='ingest_props')

    # Every 2 minutes — steam detection (high-velocity line moves)
    scheduler.add_job(run_steam_scout, 'interval', minutes=2, id='steam_scout')

    # Every hour — CLV snapshots for starting games
    scheduler.add_job(run_clv_snapshot, 'interval', hours=1, id='clv_snapshot')

    try:
        scheduler.start()
        logger.info("Scheduler started successfully.")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

async def shutdown_scheduler():
    """Graceful shutdown of the scheduler."""
    logger.info("Shutting down scheduler...")
    scheduler.shutdown()
