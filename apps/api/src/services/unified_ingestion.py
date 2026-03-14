# apps/api/src/services/unified_ingestion.py
import logging
import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy.dialects.postgresql import insert
from database import async_session_maker
from models.unified import UnifiedOdds
from services.odds.fetchers import fetch_props_for_sport, fetch_lines_for_sport, SPORT_KEY_MAP
from real_data_connector import real_data_connector

logger = logging.getLogger(__name__)

class UnifiedIngestionService:
    @staticmethod
    def american_to_implied(american: int) -> Decimal:
        if american > 0:
            return Decimal(100) / Decimal(american + 100)
        return Decimal(abs(american)) / Decimal(abs(american) + 100)

    async def has_active_events(self, sport: str) -> bool:
        """Check if there are any games scheduled for today/imminent."""
        try:
            games = await real_data_connector.fetch_games_by_sport(sport)
            return len(games) > 0
        except Exception as e:
            logger.error(f"QuotaGuard: Error checking events for {sport}: {e}")
            return True # Fail open to be safe

    async def ingest_and_compute_ev(self, sport_id: int):
        """Unified entry point for a sport's periodic sync."""
        from workers.ev_engine import ev_engine
        
        sport_key = SPORT_KEY_MAP.get(sport_id) if isinstance(sport_id, int) else sport_id
        if not sport_key: return

        # Quota Guard: skip if no games
        if not await self.has_active_events(sport_key):
            logger.info(f"QuotaGuard: Skipping {sport_key} — no active events today.")
            return

        # 1. Ingest
        await self.ingest_sport(sport_id)
        
        # 2. Compute EV
        await ev_engine.run_ev_cycle(sport_key)

    async def ingest_sport(self, sport_id: int):
        sport_key = SPORT_KEY_MAP.get(sport_id)
        if not sport_key:
            return

        logger.info(f"UnifiedIngestion: Starting sync for {sport_key}")
        
        # 1. Fetch Props
        props = await fetch_props_for_sport(sport_id)
        prop_rows = self.normalize_props(props, sport_key)
        await self.upsert_odds(prop_rows)

        # 2. Fetch Game Lines
        lines = await fetch_lines_for_sport(sport_id)
        line_rows = self.normalize_lines(lines, sport_key)
        await self.upsert_odds(line_rows)

    def normalize_props(self, raw_events: List[Dict], sport_key: str) -> List[Dict]:
        rows = []
        now = datetime.now(timezone.utc)
        
        for event in raw_events:
            event_id = event.get('id')
            league = event.get('sport_title')
            commence_time_str = event.get('commence_time')
            source_ts = datetime.fromisoformat(commence_time_str.replace('Z', '+00:00')) if commence_time_str else now
            
            for book in event.get('bookmakers', []):
                book_key = book.get('key')
                for market in book.get('markets', []):
                    market_key = market.get('key')
                    for outcome in market.get('outcomes', []):
                        # Outcome keys: 'over', 'under'
                        outcome_name = outcome.get('name').lower()
                        # Outcome keys in DB should be standardized
                        outcome_key = outcome_name
                        if 'over' in outcome_name: outcome_key = 'over'
                        elif 'under' in outcome_name: outcome_key = 'under'
                        
                        price = outcome.get('price')
                        line = outcome.get('point')
                        
                        rows.append({
                            'sport': sport_key,
                            'league': league,
                            'event_id': event_id,
                            'market_key': market_key,
                            'outcome_key': f"{outcome.get('description')}:{outcome_key}", # e.g. "LeBron James:over"
                            'bookmaker': book_key,
                            'price': Decimal(str(price)),
                            'implied_prob': self.american_to_implied(price),
                            'line': Decimal(str(line)) if line is not None else None,
                            'source_ts': source_ts,
                            'ingested_ts': now
                        })
        return rows

    def normalize_lines(self, raw_odds: List[Dict], sport_key: str) -> List[Dict]:
        rows = []
        now = datetime.now(timezone.utc)
        
        for event in raw_odds:
            event_id = event.get('id')
            league = event.get('sport_title')
            commence_time_str = event.get('commence_time')
            source_ts = datetime.fromisoformat(commence_time_str.replace('Z', '+00:00')) if commence_time_str else now
            
            for book in event.get('bookmakers', []):
                book_key = book.get('key')
                for market in book.get('markets', []):
                    market_key = market.get('key')
                    for outcome in market.get('outcomes', []):
                        outcome_name = outcome.get('name')
                        outcome_key = outcome_name.lower() # 'home', 'away', 'over', 'under'
                        
                        price = outcome.get('price')
                        line = outcome.get('point')
                        
                        rows.append({
                            'sport': sport_key,
                            'league': league,
                            'event_id': event_id,
                            'market_key': market_key,
                            'outcome_key': outcome_key,
                            'bookmaker': book_key,
                            'price': Decimal(str(price)),
                            'implied_prob': self.american_to_implied(price),
                            'line': Decimal(str(line)) if line is not None else None,
                            'source_ts': source_ts,
                            'ingested_ts': now
                        })
        return rows

    async def upsert_odds(self, rows: List[Dict]):
        if not rows:
            return
            
        async with async_session_maker() as session:
            try:
                # Use PostgreSQL ON CONFLICT if available, or manual merge for SQLite
                # The user blueprint specifically mentioned postgres
                stmt = insert(UnifiedOdds).values(rows)
                stmt = stmt.on_conflict_do_update(
                    constraint='uix_odds_unique',
                    set_={
                        'price': stmt.excluded.price,
                        'implied_prob': stmt.excluded.implied_prob,
                        'line': stmt.excluded.line,
                        'source_ts': stmt.excluded.source_ts,
                        'ingested_ts': stmt.excluded.ingested_ts
                    }
                )
                await session.execute(stmt)
                await session.commit()
                logger.info(f"UnifiedIngestion: Upserted {len(rows)} odds.")
            except Exception as e:
                await session.rollback()
                logger.error(f"UnifiedIngestion: Bulk upsert failed: {e}")

unified_ingestion = UnifiedIngestionService()
