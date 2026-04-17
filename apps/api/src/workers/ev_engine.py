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
