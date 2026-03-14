import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from jobs.ingestion_service import ingest_all_odds, run_steam_scout, run_clv_snapshot

logger = logging.getLogger(__name__)

# Singleton scheduler
scheduler = AsyncIOScheduler()

def start_ingestion_scheduler():
    """Start the 24/7 ingestion scheduler."""
    logger.info("Initializing 24/7 Ingestion Scheduler...")
    
    # Every 30 minutes — fresh odds for game state and detailed player props
    scheduler.add_job(ingest_all_odds, 'interval', minutes=30, id='ingest_odds')

    # Every 10 minutes — steam detection (high-velocity line moves)
    scheduler.add_job(run_steam_scout, 'interval', minutes=10, id='steam_scout')

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
