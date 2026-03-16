# apps/api/src/workers/ev_engine.py
import logging
from decimal import Decimal
from typing import List, Dict
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from db.session import async_session_maker
from models.unified import UnifiedOdds, UnifiedEVSignal
from routers.ws_ev import notify_ev_update

logger = logging.getLogger(__name__)

class EVEngine:
    async def run_ev_cycle(self, sport: str):
        """
        No-Vig Blended Average Strategy:
        1. Load latest odds
        2. Group by Event/Market/Line/Player
        3. Compute Fair Prob (No-Vig)
        4. Identify Edge (EV)
        5. Upsert Signals
        """
        async with async_session_maker() as session:
            # 1. Load odds
            stmt = select(UnifiedOdds).where(UnifiedOdds.sport == sport)
            result = await session.execute(stmt)
            all_odds = result.scalars().all()
            
            if not all_odds: return

            # Grouping: (eid, mkey, line, p_name) -> outcome -> book -> (price, imp)
            grouped = {}
            for o in all_odds:
                key = (o.event_id, o.market_key, o.line, o.player_name)
                if key not in grouped: grouped[key] = {}
                if o.outcome_key not in grouped[key]: grouped[key][o.outcome_key] = {}
                grouped[key][o.outcome_key][o.bookmaker] = (o.price, o.implied_prob)

            # 2. Compute Signals
            signals = []
            for (eid, mkey, line, p_name), outcomes in grouped.items():
                if len(outcomes) < 2: continue
                
                # Blended Fair Prob
                avg_fair_probs = {}
                for outcome, books in outcomes.items():
                    avg_fair_probs[outcome] = sum(p for _, p in books.values()) / len(books)
                
                total_prob = sum(avg_fair_probs.values())
                if total_prob == 0: continue
                fair_probs = {o: p / total_prob for o, p in avg_fair_probs.items()}

                # 3. Detect Edge
                for outcome, books in outcomes.items():
                    true_p = fair_probs[outcome]
                    for book, (price, implied) in books.items():
                        edge = (true_p - implied) * 100
                        if edge > 0:
                            signals.append({
                                'sport': sport,
                                'event_id': eid,
                                'market_key': mkey,
                                'outcome_key': outcome,
                                'player_name': p_name,
                                'bookmaker': book,
                                'price': price,
                                'line': line,
                                'true_prob': true_p,
                                'edge_percent': edge,
                                'implied_prob': implied,
                                'engine_version': 'v1-blended'
                            })

            # 4. Upsert
            if signals:
                await self.upsert_ev_signals(signals)
                await notify_ev_update(sport)

    async def upsert_ev_signals(self, signals: List[Dict]):
        async with async_session_maker() as session:
            try:
                engine = session.bind
                is_sqlite = "sqlite" in str(engine.url)
                
                ins_obj = sqlite_insert(UnifiedEVSignal) if is_sqlite else pg_insert(UnifiedEVSignal)
                stmt = ins_obj.values(signals)
                
                update_cols = {
                    'price': ins_obj.excluded.price,
                    'line': ins_obj.excluded.line,
                    'true_prob': ins_obj.excluded.true_prob,
                    'edge_percent': ins_obj.excluded.edge_percent,
                    'implied_prob': ins_obj.excluded.implied_prob,
                    'updated_at': func.now()
                }
                
                if is_sqlite:
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['sport', 'event_id', 'market_key', 'outcome_key', 'bookmaker', 'engine_version'],
                        set_=update_cols
                    )
                else:
                    stmt = stmt.on_conflict_do_update(
                        constraint='uix_ev_unique',
                        set_=update_cols
                    )
                await session.execute(stmt)
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"EVEngine: Signal upsert failed: {e}")

ev_engine = EVEngine()

ev_engine = EVEngine()
