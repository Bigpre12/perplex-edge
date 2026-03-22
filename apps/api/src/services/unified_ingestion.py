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
from core.config import settings
from services.brains import sharp_money_brain, brain_clv_tracker, injury_impact_brain, brain_advanced_service
from services.unified_odds_persistence import upsert_unified_odds
from services.heartbeat_service import HeartbeatService
from services.odds_api_client import odds_api_client
from services.persistence_helpers import upsert_props_live, insert_props_history, delete_props_for_sport

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
            logger.warning(f"UnifiedIngestion: No events found from /events for {sport_key}. Proceeding with potential extraction from /odds.")
            events_raw = []

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

        if not odds_raw:
            logger.warning(f"UnifiedIngestion: No odds (bulk or props) found for {sport_key}.")
            odds_raw = []

        # 2c. Backfill metadata_map if get_events() was empty/stale
        for game in odds_raw:
            eid = game.get('id')
            if eid and eid not in metadata_map:
                metadata_map[eid] = {
                    'home_team': game.get('home_team'),
                    'away_team': game.get('away_team'),
                    'game_time': datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00')) if game.get('commence_time') else None
                }

        # 2d. Fetch Player Props (Requires per-event calls)
        PROP_MARKETS_BY_SPORT = {
            "basketball_nba": "player_points,player_rebounds,player_assists,player_threes,player_blocks,player_steals,player_turnovers,player_points_rebounds_assists,player_points_rebounds,player_points_assists,player_rebounds_assists",
            "americanfootball_nfl": "player_pass_tds,player_pass_yds,player_rush_yds,player_rec_yds,player_anytime_td",
            "icehockey_nhl": "player_points,player_power_play_points,player_shots_on_goal",
            "baseball_mlb": "player_strikeouts,player_hits,player_home_runs"
        }

        if sport_key in PROP_MARKETS_BY_SPORT:
            # Use metadata_map keys if events_raw was empty
            event_ids = [e['id'] for e in events_raw] if events_raw else list(metadata_map.keys())
            
            # Filter to events starting in the next 48 hours to save quota
            now_ts = datetime.now(timezone.utc).timestamp()
            limit_ts = now_ts + (48 * 3600)
            
            active_events = []
            for eid in event_ids:
                meta = metadata_map.get(eid, {})
                gt = meta.get('game_time')
                if gt and gt.timestamp() <= limit_ts:
                    active_events.append(eid)
            
            # Limit to 20 events per run per sport to keep within 100k tier limits
            active_events = active_events[:20] 
            
            logger.info(f"UnifiedIngestion: Fetching player props for {len(active_events)} {sport_key} events...")
            
            prop_counts = 0
            for eid in active_events:
                try:
                    event_props = await odds_api_client.get_player_props(
                        sport=sport_key,
                        event_id=eid,
                        markets=PROP_MARKETS_BY_SPORT[sport_key]
                    )
                    if event_props and "bookmakers" in event_props:
                        odds_raw.append(event_props)
                        prop_counts += 1
                except Exception as e:
                    logger.error(f"UnifiedIngestion: Failed to fetch props for event {eid}: {e}")
            logger.info(f"UnifiedIngestion: Successfully fetched props for {prop_counts} events for {sport_key}")

        # 3. Normalize into PropRecords
        records = odds_mapper.map_theodds_props_to_records(odds_raw, metadata_map, sport_key)
        
        # 3b. Market Intelligence: Best Odds, Soft/Sharp flagging
        records = self.enrich_with_market_intel(records)
        metrics["odds_count"] = len(records)
        
        # 4. Standardized Persistence
        if sport_key in PROP_MARKETS_BY_SPORT:
            await delete_props_for_sport(sport_key)
            
        await upsert_props_live(records)
        await insert_props_history(records)
        metrics["rows_upserted"] = len(records)
        logger.info(f"UnifiedIngestion: Persisted {len(records)} prop records for {sport_key}")
        
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

    def enrich_with_market_intel(self, records: List[PropRecord]) -> List[PropRecord]:
        """
        Flag Best Book and Sharp/Soft categorization.
        """
        if not records: return []
        
        # Grouping by (game_id, market_key, player_name, line)
        groups: Dict[tuple, List[PropRecord]] = {}
        for r in records:
            # We use float(line) to group different Representations of the same numeric line
            safe_line = float(r.line) if r.line is not None else None
            key = (r.game_id, r.market_key, r.player_name, safe_line)
            if key not in groups: groups[key] = []
            groups[key].append(r)
            
        for key, prop_group in groups.items():
            # Best Over (Max price / Min Implied)
            best_over = max((r.odds_over for r in prop_group if r.odds_over is not None), default=None)
            # Best Under (Max price / Min Implied)
            best_under = max((r.odds_under for r in prop_group if r.odds_under is not None), default=None)
            
            for r in prop_group:
                if best_over is not None and r.odds_over == best_over:
                    r.is_best_over = True
                if best_under is not None and r.odds_under == best_under:
                    r.is_best_under = True
                
                # Book category
                book_lower = r.book.lower()
                r.is_sharp_book = any(s in book_lower for s in settings.SHARP_BOOKMAKERS)
                r.is_soft_book = any(s in book_lower for s in settings.SOFT_BOOKMAKERS)
                
                # Simple confidence metric based on book counts for this line
                r.confidence = float(min(len(prop_group) / 10.0, 1.0))
                
        return records

unified_ingestion = UnifiedIngestionService()
