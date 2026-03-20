# apps/api/src/services/unified_ingestion.py
import logging
import asyncio
import json
import traceback
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Any, Optional

from db.session import async_session_maker
from schemas.props import PropRecord
from services.odds_mapping import odds_mapper
from services.persistence_helpers import upsert_props_live, insert_props_history
from core.config import settings
from services.brains import sharp_money_brain, brain_clv_tracker, injury_impact_brain, brain_advanced_service
from services.unified_odds_persistence import upsert_unified_odds
from services.odds_api_client import odds_api_client

logger = logging.getLogger(__name__)

class UnifiedIngestionService:
    @staticmethod
    def american_to_implied(american: int) -> Decimal:
        if american > 0:
            return Decimal(100) / Decimal(american + 100)
        return Decimal(abs(american)) / Decimal(abs(american) + 100)

    async def run(self, sport_key: str):
        from workers.ev_engine import ev_engine
        metrics = {
            "sport": sport_key,
            "status": "started",
            "events_count": 0,
            "odds_count": 0,
            "rows_upserted": 0,
            "errors": []
        }
        
        # 1. Fetch metadata (Teams and Times)
        try:
            events_raw = await odds_api_client.get_events(sport_key)
            metrics["events_count"] = len(events_raw) if events_raw else 0
            logger.info(f"UnifiedIngestion: Fetched {metrics['events_count']} events from OddsAPI for {sport_key}")
        except Exception as e:
            metrics["errors"].append(f"Events Fetch: {str(e)}")
            logger.error(f"UnifiedIngestion: Failed to fetch events from OddsAPI for {sport_key}: {e}")
            events_raw = None

        if not events_raw:
            logger.error(f"UnifiedIngestion: No events found for {sport_key}. Ingestion cycle aborted.")
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
            markets = ["h2h", "spreads", "totals"]
            markets = list(dict.fromkeys([m.strip().lower() for m in markets if m.strip()]))
            
            logger.info(f"UnifiedIngestion: Fetching odds for {sport_key} with markets: {markets}")
            odds_raw = await odds_api_client.fetch_odds(sport_key, markets=markets)
            metrics["odds_count"] = len(odds_raw) if odds_raw else 0
            logger.info(f"UnifiedIngestion: Fetched {metrics['odds_count']} odds entries for {sport_key}")
        except Exception as e:
            metrics["errors"].append(f"Odds Fetch: {str(e)}")
            logger.error(f"UnifiedIngestion: Failed to fetch odds from OddsAPI for {sport_key}: {e}")
            odds_raw = None

        if not odds_raw:
            logger.warning(f"UnifiedIngestion: No odds found for {sport_key}. Skipping persistence.")
            return

        # 3. Normalize into PropRecords
        records = odds_mapper.map_theodds_props_to_records(odds_raw, metadata_map, sport_key)
        metrics["odds_count"] = len(records)
        
        # 4. Standardized Persistence
        await upsert_props_live(records)
        await insert_props_history(records)
        metrics["rows_upserted"] = len(records)
        
        # 4b. Sync with UnifiedOdds for Brains
        unified_rows = []
        for r in records:
            unified_rows.append({
                "sport": r.sport,
                "event_id": r.game_id,
                "market_key": r.market_key,
                "outcome_key": r.market_label or r.market_key, # crude but unblocks
                "bookmaker": r.book,
                "line": float(r.line) if r.line else None,
                "price": 2.0, # Placeholder or map from odds_over/under
                # Note: UnifiedOdds expects price. We might need a better mapping.
            })
        await upsert_unified_odds(unified_rows)

        # 5. Trigger Brain & EV
        secondary_tasks = [
            ("Sharp Money", lambda: sharp_money_brain.detect_signals(sport_key)),
            ("CLV Tracker", lambda: brain_clv_tracker.record_opening_line(records)),
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
            metrics["errors"].append(f"ModelPick Promotion: {str(e)}")
            logger.error(f"UnifiedIngestion: ModelPick promotion failed: {e}")

        metrics["status"] = "completed" if not metrics["errors"] else "partial_success"
        logger.info(f"🏁 UnifiedIngestion Cycle Complete: {json.dumps(metrics)}")

    async def run_with_retries(self, sport_key: str, retries: int = 3):
        """Robust entrypoint with exponential backoff for transient API failures."""
        for i in range(retries):
            try:
                await self.run(sport_key)
                return
            except Exception as e:
                logger.error(f"UnifiedIngestion: Attempt {i+1}/{retries} failed for {sport_key}: {e}")
                if i < retries - 1:
                    wait = 2 ** i
                    logger.info(f"UnifiedIngestion: Retrying in {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    logger.critical(f"UnifiedIngestion: ALL ATTEMPTS FAILED for {sport_key}")

unified_ingestion = UnifiedIngestionService()
