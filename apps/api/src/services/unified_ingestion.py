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
from services.heartbeat_service import HeartbeatService
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
            async with async_session_maker() as session:
                await HeartbeatService.log_heartbeat(session, f"ingest_{sport_key}", status="upstream_error", meta={"error": "No events found"})
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
            logger.warning(f"UnifiedIngestion: No bulk odds found for {sport_key}. Initializing empty list.")
            odds_raw = []

        # 2b. Fetch Player Props (Requires per-event calls)
        prop_markets = ["player_points", "player_rebounds", "player_assists", "player_threes", "player_double_double"]
        if sport_key == "basketball_nba":
            active_events = [e['id'] for e in events_raw[:15]] # Limit to avoid excessive API usage in one cycle
            logger.info(f"UnifiedIngestion: Fetching player props for {len(active_events)} events...")
            
            for eid in active_events:
                try:
                    event_props = await odds_api_client.get_player_props(
                        sport=sport_key,
                        event_id=eid,
                        markets=",".join(prop_markets)
                    )
                    if event_props and "bookmakers" in event_props:
                        # Normalize into the same structure as bulk odds for the mapper
                        # Bulk odds: [{"id": eid, "bookmakers": [...]}, ...]
                        # Single event props: {"id": eid, "bookmakers": [...]}
                        odds_raw.append(event_props)
                except Exception as e:
                    logger.error(f"UnifiedIngestion: Failed to fetch props for event {eid}: {e}")

        if not odds_raw:
            logger.warning(f"UnifiedIngestion: No odds (bulk or props) found for {sport_key}. Skipping persistence.")
            async with async_session_maker() as session:
                await HeartbeatService.log_heartbeat(session, f"ingest_{sport_key}", status="upstream_error", meta={"error": "No odds found"})
            return

        # 3. Normalize into PropRecords
        records = odds_mapper.map_theodds_props_to_records(odds_raw, metadata_map, sport_key)
        metrics["odds_count"] = len(records)
        
        # 4. Standardized Persistence
        await upsert_props_live(records)
        await insert_props_history(records)
        metrics["rows_upserted"] = len(records)
        
        # 4b. Sync with UnifiedOdds for Brains (Split into discrete outcomes)
        unified_rows = []
        for r in records:
            # Common metadata
            base = {
                "sport": r.sport,
                "league": r.league,
                "event_id": r.game_id,
                "game_time": r.game_start_time,
                "home_team": r.home_team,
                "away_team": r.away_team,
                "market_key": r.market_key,
                "player_name": r.player_name,
                "bookmaker": r.book,
                "line": float(r.line) if r.line else None,
            }

            # Over Outcome
            if r.odds_over is not None or r.implied_over is not None:
                over_row = base.copy()
                over_row.update({
                    "outcome_key": "over",
                    "price": float(r.odds_over) if r.odds_over else 2.0,
                    "implied_prob": float(r.implied_over) if r.implied_over else None
                })
                unified_rows.append(over_row)

            # Under Outcome
            if r.odds_under is not None or r.implied_under is not None:
                under_row = base.copy()
                under_row.update({
                    "outcome_key": "under",
                    "price": float(r.odds_under) if r.odds_under else 2.0,
                    "implied_prob": float(r.implied_under) if r.implied_under else None
                })
                unified_rows.append(under_row)

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
        
        async with async_session_maker() as session:
            await HeartbeatService.log_heartbeat(
                session, 
                f"ingest_{sport_key}", 
                status="ok" if not metrics["errors"] else "error",
                rows_written=metrics.get("rows_upserted", 0),
                error_count=len(metrics["errors"]),
                meta={"metrics": metrics}
            )

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
                    async with async_session_maker() as session:
                        await HeartbeatService.log_heartbeat(
                            session, 
                            f"ingest_{sport_key}", 
                            status="pipeline_error",
                            meta={"error": str(e), "attempts": retries}
                        )

unified_ingestion = UnifiedIngestionService()
