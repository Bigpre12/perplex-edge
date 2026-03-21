# apps/api/src/workers/ev_engine.py
import logging
from decimal import Decimal
from typing import List, Dict
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from db.session import async_session_maker
from models import UnifiedOdds, PropLive, UnifiedEVSignal
from services.ev_persistence import insert_edges_ev_history
from routers.ws_ev import notify_ev_update

logger = logging.getLogger(__name__)

from services.ev_service import ev_service

class EVEngine:
    async def run_ev_cycle(self, sport: str):
        # 1. Run the core EV calculation logic
        await ev_service.run_ev_cycle(sport)
        
        # 2. Broadcast to connected WebSocket clients that new signals are available
        try:
            await notify_ev_update(sport)
        except Exception as e:
            logger.error(f"EVEngine: Failed to broadcast EV update for {sport}: {e}")

ev_engine = EVEngine()
