# apps/api/src/workers/ev_engine.py
import logging
import asyncio
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from database import async_session_maker
from models.unified import UnifiedOdds, UnifiedEVSignal
from routers.ws_ev import notify_ev_update
from services.unified_ingestion import UnifiedIngestionService

logger = logging.getLogger(__name__)

from celery_app import celery_app


def get_ev_engine():
    global _ev_engine
    if _ev_engine is None:
        _ev_engine = EVEngine()
    return _ev_engine

_ev_engine = None

# --- Celery Task Wrapper ---
@celery_app.task(name="workers.ev_engine.run_ev_cycle_task")
def run_ev_cycle_task(sport: str):
    """Sync wrapper for Celery to call the async ingestion service."""
    import asyncio
    service = UnifiedIngestionService()
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # This shouldn't happen in a standard Celery worker thread
        asyncio.ensure_future(service.ingest_and_compute_ev(sport))
    else:
        loop.run_until_complete(service.ingest_and_compute_ev(sport))

class EVEngine:
    async def run_ev_cycle(self, sport: str):
        """Compute EV for a specific sport market using a 'No-Vig' blended average strategy."""
        async with async_session_maker() as session:
            # 1. Load latest odds (within last 1 hour)
            logger.info(f"EVEngine: Loading latest {sport} odds...")
            stmt = select(UnifiedOdds).where(
                UnifiedOdds.sport == sport
            ).order_by(UnifiedOdds.ingested_ts.desc())
            
            result = await session.execute(stmt)
            all_odds = result.scalars().all()
            
            if not all_odds:
                logger.warning(f"EVEngine: No odds found for {sport} to process.")
                return

            # Group odds by (event_id, market_key, line, outcome_key)
            grouped = {} # (event_id, market_key, line) -> outcomes -> bookmakers -> price
            for o in all_odds:
                key = (o.event_id, o.market_key, o.line)
                if key not in grouped:
                    grouped[key] = {}
                
                if o.outcome_key not in grouped[key]:
                    grouped[key][o.outcome_key] = {}
                
                grouped[key][o.outcome_key][o.bookmaker] = o.implied_prob

            # 2. Compute Signals
            signals = []
            for (event_id, market_key, line), outcomes in grouped.items():
                if len(outcomes) < 2: continue
                
                avg_probs = {}
                for outcome, books in outcomes.items():
                    avg_probs[outcome] = sum(books.values()) / len(books)
                
                sum_prob = sum(avg_probs.values())
                if sum_prob == 0: continue
                
                fair_probs = {outcome: prob / sum_prob for outcome, prob in avg_probs.items()}
                
                for outcome, books in outcomes.items():
                    true_prob = fair_probs[outcome]
                    for book, implied in books.items():
                        edge = (true_prob - implied) * 100
                        
                        if edge > 0:
                            signals.append({
                                'sport': sport,
                                'event_id': event_id,
                                'market_key': market_key,
                                'outcome_key': outcome,
                                'bookmaker': book,
                                'price': Decimal('0'), 
                                'true_prob': true_prob,
                                'edge_percent': edge,
                                'engine_version': 'v1-blended'
                            })

            # 3. Upsert Signals
            if signals:
                await self.upsert_ev_signals(signals)
                await notify_ev_update(sport)

    async def upsert_ev_signals(self, signals: List[Dict]):
        async with async_session_maker() as session:
            try:
                dialect_name = session.sync_session.bind.dialect.name
                
                if dialect_name == 'sqlite':
                    from sqlalchemy.dialects.sqlite import insert as sqlite_insert
                    stmt = sqlite_insert(UnifiedEVSignal).values(signals)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['sport', 'event_id', 'market_key', 'outcome_key', 'bookmaker', 'engine_version'],
                        set_={
                            'price': stmt.excluded.price,
                            'true_prob': stmt.excluded.true_prob,
                            'edge_percent': stmt.excluded.edge_percent,
                            'updated_at': func.now()
                        }
                    )
                else:
                    from sqlalchemy.dialects.postgresql import insert as pg_insert
                    stmt = pg_insert(UnifiedEVSignal).values(signals)
                    stmt = stmt.on_conflict_do_update(
                        constraint='uix_ev_unique',
                        set_={
                            'price': stmt.excluded.price,
                            'true_prob': stmt.excluded.true_prob,
                            'edge_percent': stmt.excluded.edge_percent,
                            'updated_at': func.now()
                        }
                    )
                await session.execute(stmt)
                await session.commit()
                logger.info(f"EVEngine: Upserted {len(signals)} EV signals.")
            except Exception as e:
                await session.rollback()
                logger.error(f"EVEngine: Signal upsert failed: {e}")

ev_engine = EVEngine()
