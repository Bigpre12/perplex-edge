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
from db.session import async_session_maker, engine
from models.unified import UnifiedOdds, LineTick
from clients.odds_client import odds_api_client
from services.cache import cache
from services.odds.fetchers import SPORT_KEY_MAP, SPORT_MARKETS
from services.espn_client import espn_client
from services.brain_sharp_money import sharp_money_brain
from services.brain_clv_tracker_loop import brain_clv_tracker
from services.brain_injury_impact import injury_impact_brain
from services.brain_advanced_service import brain_advanced_service
from core.config import settings

logger = logging.getLogger(__name__)

class UnifiedIngestionService:
    @staticmethod
    def american_to_implied(american: int) -> Decimal:
        if american > 0:
            return Decimal(100) / Decimal(american + 100)
        return Decimal(abs(american)) / Decimal(abs(american) + 100)

    async def run(self, sport_key: str):
        from workers.ev_engine import ev_engine
        
        # 1. Fetch metadata (Teams and Times)
        try:
            events_raw = await odds_api_client.fetch_events(sport_key)
            logger.info(f"UnifiedIngestion: Fetched {len(events_raw) if events_raw else 0} events from OddsAPI for {sport_key}")
        except Exception as e:
            logger.error(f"UnifiedIngestion: Failed to fetch events from OddsAPI for {sport_key}: {e}")
            events_raw = None

        if not events_raw:
            logger.info(f"UnifiedIngestion: Attempting ESPN fallback for {sport_key}...")
            try:
                espn_games = await espn_client.get_scoreboard(sport_key)
                if espn_games:
                    events_raw = [
                        {
                            'id': g['id'],
                            'home_team': g['home_team_name'],
                            'away_team': g['away_team_name'],
                            'commence_time': g['start_time'].isoformat().replace('+00:00', 'Z')
                        }
                        for g in espn_games
                    ]
                    logger.info(f"UnifiedIngestion: ESPN fallback successful, found {len(events_raw)} games.")
                else:
                    logger.warning(f"UnifiedIngestion: ESPN fallback returned no games for {sport_key}")
                    return
            except Exception as ex:
                logger.error(f"UnifiedIngestion: ESPN fallback failed for {sport_key}: {ex}")
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

        # 2. Fetch Pricing
        try:
            # Sport-wide endpoint usually only supports main lines reliably
            markets = ["h2h", "spreads", "totals"]
            
            # Deduplicate and Clean
            markets = list(dict.fromkeys([m.strip().lower() for m in markets if m.strip()]))
            
            logger.info(f"UnifiedIngestion: Fetching odds for {sport_key} with markets: {markets}")
            odds_raw = await odds_api_client.fetch_odds(sport_key, markets=markets)
            logger.info(f"UnifiedIngestion: Fetched {len(odds_raw) if odds_raw else 0} odds entries for {sport_key}")
        except Exception as e:
            logger.error(f"UnifiedIngestion: Failed to fetch odds from OddsAPI for {sport_key}: {e}")
            odds_raw = None

        if not odds_raw:
            logger.info(f"UnifiedIngestion: No odds for {sport_key}, creating placeholders from metadata.")
            rows = []
            now = datetime.now(timezone.utc)
            for eid, meta in metadata_map.items():
                rows.append({
                    'sport': sport_key,
                    'league': sport_key.split('_')[-1].upper(),
                    'event_id': eid,
                    'home_team': meta.get('home_team'),
                    'away_team': meta.get('away_team'),
                    'game_time': meta.get('game_time'),
                    'market_key': 'h2h',
                    'outcome_key': 'home',
                    'player_name': None,
                    'bookmaker': 'espn_fallback',
                    'price': Decimal('0'),
                    'line': None,
                    'implied_prob': Decimal('0'),
                    'source_ts': now,
                    'ingested_ts': now
                })
        else:
            # 3. Normalize
            rows = self.normalize_data(odds_raw, metadata_map, sport_key)
        
        # 4. Upsert
        await self.upsert_odds(rows)

        # 5. Trigger Brain & EV
        secondary_tasks = [
            ("Sharp Money", lambda: sharp_money_brain.detect_signals(sport_key)),
            ("CLV Tracker", lambda: brain_clv_tracker.record_opening_line(rows)),
            ("Injury Impact", lambda: injury_impact_brain.analyze_impacts(sport_key)),
            ("EV Engine", lambda: ev_engine.run_ev_cycle(sport_key)),
        ]

        for name, task_fn in secondary_tasks:
            try:
                res = task_fn()
                if asyncio.iscoroutine(res):
                    await res
                logger.info(f"UnifiedIngestion: Successfully completed {name}")
            except Exception as e:
                logger.error(f"UnifiedIngestion: Secondary processing failed for {name}: {e}")

        # Promote EV signals to ModelPicks for the dashboard
        try:
            async with async_session_maker() as session:
                await brain_advanced_service.generate_model_picks(sport_key, session)
            logger.info(f"UnifiedIngestion: Successfully promoted ModelPicks for {sport_key}")
        except Exception as e:
            logger.error(f"UnifiedIngestion: ModelPick promotion failed: {e}")

    def normalize_data(self, odds_raw: List[Dict], metadata_map: Dict[str, Dict], sport: str) -> List[Dict]:
        rows = []
        now = datetime.now(timezone.utc)
        
        if not isinstance(odds_raw, list):
            logger.error(f"UnifiedIngestion: odds_raw is not a list: {type(odds_raw)}")
            return []

        for event in odds_raw:
            try:
                if not isinstance(event, dict):
                    logger.warning(f"UnifiedIngestion: Skipping non-dict event: {event}")
                    continue

                eid = event.get('id')
                if not eid:
                    continue

                meta = metadata_map.get(eid, {})
                league = event.get('sport_title') or sport.split('_')[-1].upper()
                
                bookmakers = event.get('bookmakers', [])
                if not isinstance(bookmakers, list):
                    continue

                for book in bookmakers:
                    if not isinstance(book, dict): continue
                    book_key = book.get('key')
                    
                    markets = book.get('markets', [])
                    if not isinstance(markets, list): continue

                    for market in markets:
                        if not isinstance(market, dict): continue
                        m_key = market.get('key')
                        
                        outcomes = market.get('outcomes', [])
                        if not isinstance(outcomes, list): continue

                        for outcome in outcomes:
                            if not isinstance(outcome, dict): continue
                            # Outcome name normalization
                            name = outcome.get('name')
                            desc = outcome.get('description') # Usually player name for props
                            price = outcome.get('price')
                            line = outcome.get('point')
                            
                            if name is None or price is None:
                                continue

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
            except Exception as e:
                logger.error(f"UnifiedIngestion: Error normalizing event {event.get('id') if isinstance(event, dict) else 'unknown'}: {e}")
                continue

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
                
                # 2. Record Ticks for Movement Analysis
                # Filter rows to only record meaningful data (e.g. price > 0)
                tick_rows = [
                    {
                        "sport": r["sport"],
                        "event_id": r["event_id"],
                        "market_key": r["market_key"],
                        "outcome_key": r["outcome_key"],
                        "player_name": r["player_name"],
                        "bookmaker": r["bookmaker"],
                        "price": r["price"],
                        "line": r["line"]
                    }
                    for r in rows if r["price"] != 0
                ]
                
                if tick_rows:
                    await session.execute(pg_insert(LineTick).values(tick_rows) if not is_sqlite else sqlite_insert(LineTick).values(tick_rows))
                
                await session.commit()
                
                # Immediate verification
                count_res = await session.execute(text("SELECT count(*) FROM odds"))
                count = count_res.scalar()
                logger.info(f"UnifiedIngestion: Upsert successful. New odds count: {count}")
                logger.info(f"UnifiedIngestion: Upserted {len(rows)} rows and recorded {len(tick_rows)} ticks for {rows[0]['sport']}")
            except Exception as e:
                await session.rollback()
                logger.error(f"UnifiedIngestion: Upsert failed: {e}")

unified_ingestion = UnifiedIngestionService()
