# apps/api/src/workers/ev_engine.py
import logging
from decimal import Decimal
from typing import List, Dict
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from db.session import async_session_maker
from models import UnifiedOdds, PropLive, UnifiedEVSignal
from routers.ws_ev import notify_ev_update

logger = logging.getLogger(__name__)

from services.ev_service import ev_service

from celery_app import celery_app
import asyncio

class EVEngine:
    async def run_ev_cycle(self, sport: str):
        from services.odds_quota_store import raise_if_quota_blocked, fetch_usage_summary
        from brain.decisions import props_live_age_minutes, should_skip_fetch_for_fresh_cache

        async with async_session_maker() as session:
            blocked, reason = await raise_if_quota_blocked(session)
            if blocked:
                logger.warning("EVEngine: skip %s — quota blocked (%s)", sport, reason)
                return

            usage = await fetch_usage_summary(session)
            quota_pct = float(usage.get("percent_used") or 0) / 100.0
            cache_age = await props_live_age_minutes(session, sport)

        skip, skip_reason = should_skip_fetch_for_fresh_cache(cache_age, quota_pct)
        if skip:
            logger.info(
                "EVEngine: skip %s — %s (quota_pct=%.3f, props_age_min=%s)",
                sport,
                skip_reason,
                quota_pct,
                cache_age,
            )
            return

        # 1. Run the unified ingestion and intelligence pipeline
        from services.unified_ingestion import unified_ingestion
        await unified_ingestion.run(sport)
        
        # 2. Broadcast to connected WebSocket clients that new signals are available
        try:
            await notify_ev_update(sport)
        except Exception as e:
            logger.error(f"EVEngine: Failed to broadcast EV update for {sport}: {e}")

@celery_app.task(name="workers.ev_engine.run_ev_cycle_task")
def run_ev_cycle_task(sport: str):
    """Celery task wrapper for the async EV cycle"""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If already in a loop (unlikely for Celery worker process), use create_task
        asyncio.create_task(ev_engine.run_ev_cycle(sport))
    else:
        loop.run_until_complete(ev_engine.run_ev_cycle(sport))

ev_engine = EVEngine()
