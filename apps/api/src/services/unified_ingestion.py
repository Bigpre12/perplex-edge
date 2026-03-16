# apps/api/src/services/unified_ingestion.py
import logging
import asyncio
import json
import traceback
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from database import async_session_maker, engine
from models.unified import UnifiedOdds
from clients.odds_client import odds_api_client
from services.cache import cache
from services.odds.fetchers import SPORT_KEY_MAP, SPORT_MARKETS
from config import settings

logger = logging.getLogger(__name__)

class UnifiedIngestionService:
    @staticmethod
    def american_to_implied(american: int) -> Decimal:
        if american > 0:
            return Decimal(100) / Decimal(american + 100)
        return Decimal(abs(american)) / Decimal(abs(american) + 100)

    async def run(self, sport_key: str):
        """
        Production Ingestion Pipeline:
        1. Fetch Events (Metadata: Teams, Game Time)
        2. Fetch Odds (Market Pricing)
        3. Merge & Normalize
        4. Bulk Upsert (Idempotent)
        5. Trigger Brain Layers
        """
        from workers.ev_engine import ev_engine
        
        # 1. Fetch metadata (Teams and Times)
        try:
            events_raw = await odds_api_client.fetch_events(sport_key)
            logger.info(f"UnifiedIngestion: Fetched {len(events_raw) if events_raw else 0} events for {sport_key}")
            if not events_raw:
                logger.info(f"UnifiedIngestion: No active events for {sport_key}")
                return
            
            # Map event_id -> metadata
            metadata_map = {
                e['id']: {
                    'home_team': e.get('home_team'),
                    'away_team': e.get('away_team'),
                    'game_time': datetime.fromisoformat(e['commence_time'].replace('Z', '+00:00')) if e.get('commence_time') else None
                }
                for e in events_raw
            }
        except Exception as e:
            logger.error(f"UnifiedIngestion: Failed to fetch events for {sport_key}: {e}")
            return

        # 2. Fetch Pricing
        try:
            # Sport-wide endpoint usually only supports main lines reliably
            markets = ["h2h", "spreads", "totals"]
            # To fetch props, we should use the per-event endpoint in the future
            
            # Deduplicate and Clean
            markets = list(dict.fromkeys([m.strip().lower() for m in markets if m.strip()]))
            
            logger.info(f"UnifiedIngestion: Fetching odds for {sport_key} with markets: {markets}")
            odds_raw = await odds_api_client.fetch_odds(sport_key, markets=markets)
            logger.info(f"UnifiedIngestion: Fetched {len(odds_raw) if odds_raw else 0} odds entries for {sport_key}")
            if not odds_raw:
                logger.warning(f"UnifiedIngestion: No odds returned for {sport_key}")
                return
        except Exception as e:
            logger.error(f"UnifiedIngestion: Failed to fetch odds for {sport_key}: {e}")
            return

        # 3. Normalize
        rows = self.normalize_data(odds_raw, metadata_map, sport_key)
        
        # 4. Upsert
        await self.upsert_odds(rows)

        # 5. Trigger Brain & EV
        try:
            from services.brain_sharp_money import sharp_money_brain
            from services.brain_injury_impact import injury_impact_brain
            from services.brain_clv_tracker import brain_clv_tracker
            
            await sharp_money_brain.detect_signals(sport_key)
            await brain_clv_tracker.record_opening_line(rows)
            await injury_impact_brain.analyze_impacts(sport_key)
            
            await ev_engine.run_ev_cycle(sport_key)
        except Exception as e:
            logger.error(f"UnifiedIngestion: Secondary processing failed: {e}")

    def normalize_data(self, odds_raw: List[Dict], metadata_map: Dict[str, Dict], sport: str) -> List[Dict]:
        rows = []
        now = datetime.now(timezone.utc)
        
        for event in odds_raw:
            eid = event.get('id')
            meta = metadata_map.get(eid, {})
            league = event.get('sport_title') or sport.split('_')[-1].upper()
            
            for book in event.get('bookmakers', []):
                book_key = book.get('key')
                for market in book.get('markets', []):
                    m_key = market.get('key')
                    for outcome in market.get('outcomes', []):
                        # Outcome name normalization
                        name = outcome.get('name')
                        desc = outcome.get('description') # Usually player name for props
                        price = outcome.get('price')
                        line = outcome.get('point')
                        
                        # Outcome key logic
                        if m_key in ['h2h', 'spreads', 'totals']:
                            o_key = name.lower()
                            p_name = None
                        else:
                            # Prop handling
                            p_name = desc or name
                            side = name.lower()
                            if 'over' in side: o_key = 'over'
                            elif 'under' in side: o_key = 'under'
                            else: o_key = side
                            
                        rows.append({
                            'sport': sport,
                            'league': league,
                            'event_id': eid,
                            'home_team': meta.get('home_team'),
                            'away_team': meta.get('away_team'),
                            'game_time': meta.get('game_time'),
                            'market_key': m_key,
                            'outcome_key': o_key,
                            'player_name': p_name,
                            'bookmaker': book_key,
                            'price': Decimal(str(price)),
                            'line': Decimal(str(line)) if line is not None else None,
                            'implied_prob': self.american_to_implied(int(price)) if isinstance(price, (int, float)) else Decimal('0'),
                            'source_ts': datetime.fromisoformat(book.get('last_update').replace('Z', '+00:00')) if book.get('last_update') else now,
                            'ingested_ts': now
                        })
        return rows

    async def upsert_odds(self, rows: List[Dict]):
        if not rows: 
            logger.warning("UnifiedIngestion: No rows to upsert.")
            return
        
        logger.info(f"UnifiedIngestion: Upserting {len(rows)} rows into odds table.")
        async with async_session_maker() as session:
            try:
                # Detect dialect
                is_sqlite = "sqlite" in str(engine.url)
                
                ins_obj = sqlite_insert(UnifiedOdds) if is_sqlite else pg_insert(UnifiedOdds)
                stmt = ins_obj.values(rows)
                
                update_cols = {
                    'price': ins_obj.excluded.price,
                    'line': ins_obj.excluded.line,
                    'implied_prob': ins_obj.excluded.implied_prob,
                    'source_ts': ins_obj.excluded.source_ts,
                    'ingested_ts': ins_obj.excluded.ingested_ts,
                    'home_team': ins_obj.excluded.home_team,
                    'away_team': ins_obj.excluded.away_team,
                    'game_time': ins_obj.excluded.game_time,
                    'player_name': ins_obj.excluded.player_name
                }
                
                if is_sqlite:
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['sport', 'event_id', 'market_key', 'outcome_key', 'bookmaker'],
                        set_=update_cols
                    )
                else:
                    stmt = stmt.on_conflict_do_update(
                        constraint='uix_odds_unique',
                        set_=update_cols
                    )
                    
                from sqlalchemy import text
                await session.execute(stmt)
                await session.commit()
                
                # Immediate verification
                count_res = await session.execute(text("SELECT count(*) FROM odds"))
                count = count_res.scalar()
                logger.info(f"UnifiedIngestion: Upsert successful. New odds count: {count}")
                logger.info(f"UnifiedIngestion: Upserted {len(rows)} rows for {rows[0]['sport']}")
            except Exception as e:
                await session.rollback()
                logger.error(f"UnifiedIngestion: Upsert failed: {e}")

unified_ingestion = UnifiedIngestionService()

unified_ingestion = UnifiedIngestionService()
