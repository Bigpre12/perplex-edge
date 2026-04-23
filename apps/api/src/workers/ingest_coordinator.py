"""
Quota-aware Celery ingest: single beat tick decides per-sport whether to run unified_ingestion.
"""
from __future__ import annotations

import logging
import time

from celery_app import celery_app
from core.ingest_coordinator_env import INGEST_COORDINATOR_MAX_PER_TICK

logger = logging.getLogger(__name__)


async def run_ingest_coordinator_tick() -> None:
    from services.cache import cache
    from db.session import async_session_maker
    from services.odds_quota_store import raise_if_quota_blocked, fetch_usage_summary
    from services.unified_ingestion import unified_ingestion
    from core.sports_config import ALL_SPORTS, ingest_interval_seconds_for_sport
    from brain.quota_guard import scale_interval_seconds

    await cache.connect()

    async with async_session_maker() as session:
        blocked, reason = await raise_if_quota_blocked(session)
        if blocked:
            logger.warning("ingest_coordinator: quota blocked (%s) — skipping all sports", reason)
            return
        usage = await fetch_usage_summary(session)
    quota_pct = float(usage.get("percent_used") or 0) / 100.0

    now = time.time()
    ran = 0
    max_per_tick = INGEST_COORDINATOR_MAX_PER_TICK
    for sport in ALL_SPORTS:
        if ran >= max_per_tick:
            break
        key = f"ingest:last_run:{sport}"
        raw = await cache.get(key)
        base = int(ingest_interval_seconds_for_sport(sport))
        required = float(scale_interval_seconds(base, quota_pct))
        try:
            last = float(raw) if raw else now - (abs(hash(sport)) % max(60, int(base)))
        except (TypeError, ValueError):
            last = now - required
        if now - last < required:
            continue
        try:
            await unified_ingestion.run(sport)
            await cache.set(key, str(now), ttl=86400 * 7)
            ran += 1
        except Exception as e:
            logger.error("ingest_coordinator: unified_ingestion failed for %s: %s", sport, e)
    if ran:
        logger.info("ingest_coordinator: completed %s sport ingests (quota_pct=%.3f)", ran, quota_pct)


@celery_app.task(name="workers.ingest_coordinator.ingest_coordinator_task")
def ingest_coordinator_task() -> None:
    import asyncio

    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(run_ingest_coordinator_tick())
    else:
        loop.run_until_complete(run_ingest_coordinator_tick())
