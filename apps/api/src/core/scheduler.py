import logging
import os
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from core.config import settings
from core.sports_config import ACTIVE_SPORTS
from core.ingest_scheduler_config import build_unified_ingest_schedule, scheduled_sport_keys

logger = logging.getLogger(__name__)

# Global singleton instance
scheduler = AsyncIOScheduler(timezone="UTC")
_scheduler_initialized = False

# 1. Guarded Wrappers (Module level to ensure stable function references)
async def guarded_unified_ingest(sport_key: str):
    from services.odds_api_client import odds_api_client
    from services.unified_ingestion import unified_ingestion
    if odds_api_client.all_keys_dead():
        logger.debug(f"Skipping ingest_{sport_key} — all Odds API keys cooling down")
        return
    await unified_ingestion.run_with_retries(sport_key)

async def guarded_kalshi_sync(sport_key: str):
    from services.kalshi_service import kalshi_service
    from services.kalshi_ingestion import kalshi_ingestion
    from services.odds_api_client import odds_api_client
    if not kalshi_service.enabled:
        logger.debug(f"Skipping kalshi_sync_{sport_key} — Kalshi service disabled")
        return
    if odds_api_client.all_keys_dead():
        logger.debug(f"Skipping kalshi_sync_{sport_key} — all Odds API keys cooling down")
        return
    await kalshi_ingestion.run(sport_key)

def init_scheduler_jobs():
    """
    Register all recurring background jobs in the global scheduler.
    Uses fixed IDs and 'replace_existing=True' to prevent duplication.
    """
    global _scheduler_initialized
    if _scheduler_initialized:
        logger.info("📡 [Scheduler] Jobs already initialized. Skipping to prevent duplicates.")
        return
    
    logger.info("📡 [Scheduler] Initializing background jobs...")

    from services.grading_service import grading_service
    from services.whale_service import whale_service
    from services.grader import run_full_grading_pipeline
    from services.live_data_service import live_data_service
    from services.seed_scheduler import setup_seed_scheduler

    # Common job configuration for stability
    common_kw = {
        "replace_existing": True,
        "max_instances": 1,
        "coalesce": True,
        "jitter": 30,
    }

    # 2. Build Ingest Schedule
    ingest_job_specs, ingest_meta = build_unified_ingest_schedule()
    
    for spec in ingest_job_specs:
        job_id = f"ingest_{spec.sport_key}"
        job_kw: dict = common_kw.copy()
        job_kw.update({
            "args": [spec.sport_key],
            "id": job_id,
            "name": job_id,
        })
        if spec.minutes is not None:
            job_kw["minutes"] = spec.minutes
        else:
            job_kw["hours"] = spec.hours
            
        scheduler.add_job(guarded_unified_ingest, "interval", **job_kw)

    # 3. Grading Jobs
    scheduler.add_job(
        grading_service.run_grading_cycle,
        'interval',
        minutes=10,
        id="auto_grading",
        name="auto_grading",
        **common_kw
    )

    scheduler.add_job(
        run_full_grading_pipeline,
        'interval',
        minutes=5,
        id="sql_grading",
        name="sql_grading",
        **common_kw
    )

    # 4. Kalshi Sync
    kalshi_supported = ["NBA", "MLB", "WNBA", "NFL", "NHL"]
    for sport_key in ACTIVE_SPORTS:
        k_sport = sport_key.split("_")[-1].upper()
        if k_sport in kalshi_supported:
            job_id = f"kalshi_sync_{k_sport.lower()}"
            scheduler.add_job(
                guarded_kalshi_sync,
                'interval',
                minutes=8,
                args=[k_sport],
                id=job_id,
                name=job_id,
                **common_kw
            )

    # 5. Whale Service
    scheduler.add_job(
        whale_service.detect_whale_signals,
        'interval',
        minutes=12,
        id="whale_global_check",
        name="whale_global_check",
        **common_kw
    )

    # 6. Live Scores Polling
    poll_kw = common_kw.copy()
    poll_kw["jitter"] = 10
    scheduler.add_job(
        live_data_service.poll_scores,
        "interval",
        seconds=max(60, int(settings.LIVE_DATA_POLLING_INTERVAL)),
        id="live_scores_cache_upsert",
        name="live_scores_cache_upsert",
        **poll_kw
    )

    # 7. Seed Pipeline (PrizePicks Nightly)
    setup_seed_scheduler(scheduler)

    _scheduler_initialized = True
    logger.info("📡 [Scheduler] Job initialization complete. Registered %d total jobs.", len(scheduler.get_jobs()))

def start_scheduler():
    if not scheduler.running:
        init_scheduler_jobs()
        logger.info("📡 [Scheduler] Starting global APScheduler...")
        scheduler.start()
    else:
        logger.debug("📡 [Scheduler] Global APScheduler is already running.")
