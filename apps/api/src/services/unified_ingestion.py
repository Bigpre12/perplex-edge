# apps/api/src/services/unified_ingestion.py
import logging
import asyncio
import json
import traceback
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Any, Optional

from db.session import async_session_maker # type: ignore
from schemas.props import PropRecord # type: ignore
from services.odds_mapping import odds_mapper # type: ignore
from core.config import settings # type: ignore
from services.brains import sharp_money_brain, brain_clv_tracker, injury_impact_brain, brain_advanced_service # type: ignore
from services.unified_odds_persistence import upsert_unified_odds # type: ignore
from services.heartbeat_service import HeartbeatService # type: ignore
from services.odds_api_client import odds_api_client # type: ignore
from services.persistence_helpers import upsert_props_live, insert_props_history, delete_props_for_sport # type: ignore
from real_sports_api import _real_sports_api_instance # type: ignore
from real_data_connector import real_data_connector # type: ignore
from services.alert_writer import run_alert_detection # type: ignore
from services.ev_writer import run_ev_grader # type: ignore

logger = logging.getLogger(__name__)

class UnifiedIngestionService:
    @staticmethod
    def american_to_implied(american: int) -> Decimal:
        if american > 0:
            return Decimal(100) / Decimal(american + 100)
        return Decimal(abs(american)) / Decimal(abs(american) + 100)

    async def run(self, sport_key: str):
        start_time = datetime.now(timezone.utc)
        source_name = "primary"
        from workers.ev_engine import ev_engine # type: ignore
        errors: List[str] = []
        metrics: Dict[str, Any] = {
            "sport": sport_key,
            "status": "started",
            "events_count": 0,
            "odds_count": 0,
            "rows_upserted": 0,
            "errors": errors
        }
        
        # 1. Fetch metadata (Teams and Times) — Attempt key rotation ingest
        try:
            # Task 1: Use key-rotating instance
            odds_raw = await _real_sports_api_instance.fetch_odds_from_theodds(sport_key)
            
            # Task 2: Waterfall Fallback
            if not odds_raw or (isinstance(odds_raw, dict) and "error" in odds_raw) or len(odds_raw) < 2:
                logger.info(f"UnifiedIngestion: Waterfall fallback triggered for {sport_key}")
                fallback_data = await real_data_connector.fetch_games_by_sport(sport_key)
                if fallback_data:
                    source_name = f"waterfall({fallback_data[0].get('source', 'unknown')})"
                    # Map fallback format to Odds API style for the mapper
                    odds_raw = []
                    for g in fallback_data:
                        odds_raw.append({
                            "id": g.get("id"),
                            "sport_key": sport_key,
                            "home_team": g.get("home_team"),
                            "away_team": g.get("away_team"),
                            "commence_time": g.get("start_time").isoformat() if isinstance(g.get("start_time"), datetime) else None,
                            "bookmakers": g.get("raw_bookmakers_data", [])
                        })
                else:
                    odds_raw = []
            
            metrics["events_count"] = len(odds_raw)
            logger.info(f"UnifiedIngestion: Fetched {metrics['events_count']} events from {source_name} for {sport_key}")
        except Exception as e:
            metrics["errors"].append(f"Ingest Fetch: {str(e)}")
            logger.error(f"UnifiedIngestion: Failed to fetch data: {e}")
            odds_raw = []

        # Map event_id -> metadata
        metadata_map = {}
        for e in odds_raw:
            eid = e.get('id')
            if not eid: continue
            
            commence_time = e.get('commence_time')
            game_time = None
            if isinstance(commence_time, str):
                game_time = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
            
            metadata_map[eid] = {
                'home_team': e.get('home_team'),
                'away_team': e.get('away_team'),
                'game_time': game_time
            }

        # 2d. Fetch Player Props (Requires per-event calls)
        PROP_MARKETS_BY_SPORT = {
            "basketball_nba": "player_points,player_rebounds,player_assists,player_threes",
            "americanfootball_nfl": "player_pass_tds,player_pass_yds,player_rush_yds,player_rec_yds,player_anytime_td",
            "icehockey_nhl": "player_points,player_power_play_points,player_shots_on_goal",
            "baseball_mlb": "pitcher_strikeouts,batter_hits,batter_home_runs"
        }

        if sport_key in PROP_MARKETS_BY_SPORT:
            event_ids = list(metadata_map.keys())
            # type: ignore (Pyre inference fail on list slice)
            # Quota Protection: Cap at 25 events per cycle to prevent credit drain
            active_events = event_ids[:20] 
            
            logger.info(f"UnifiedIngestion: Fetching player props for {len(active_events)} {sport_key} events...")
            
            prop_counts: int = 0
            for eid in active_events:
                try:
                    # Attempt primary prop fetch
                    event_props = await odds_api_client.get_player_props(
                        sport=sport_key,
                        event_id=eid,
                        markets=PROP_MARKETS_BY_SPORT[sport_key]
                    )
                    
                    # Task 3: Per-event prop fallback
                    if not event_props or not event_props.get("bookmakers"):
                        logger.info(f"UnifiedIngestion: Prop fallback for event {eid}")
                        fallback_props = await real_data_connector.fetch_player_props(sport_key, eid)
                        if fallback_props:
                            # Map fallback to bookmaker format
                            bm_map = {}
                            for p in fallback_props:
                                bk = p.get("sportsbook_key", "unknown")
                                if bk not in bm_map:
                                    bm_map[bk] = {"key": bk, "title": p.get("sportsbook"), "markets": []}
                                
                                mkt_key = f"player_{p.get('stat_type')}"
                                mkt = next((m for m in bm_map[bk]["markets"] if m["key"] == mkt_key), None)
                                if not mkt:
                                    outcomes: List[Dict[str, Any]] = []
                                    mkt = {"key": mkt_key, "outcomes": outcomes}
                                    bm_map[bk]["markets"].append(mkt)
                                
                                # type: ignore (Inference fail on outcome list)
                                mkt["outcomes"].append({
                                    "name": "Over", "description": p.get("player_name"),
                                    "price": p.get("over_odds"), "point": p.get("line")
                                })
                                # type: ignore (Inference fail on outcome list)
                                mkt["outcomes"].append({
                                    "name": "Under", "description": p.get("player_name"),
                                    "price": p.get("under_odds"), "point": p.get("line")
                                })
                            
                            event_props = {"id": eid, "sport_key": sport_key, "bookmakers": list(bm_map.values())}

                    if event_props:
                        # type: ignore (Inference fail on odds_raw)
                        odds_raw.append(event_props)
                        # type: ignore (Inference fail on int increment)
                        prop_counts += 1
                except Exception as e:
                    logger.error(f"UnifiedIngestion: Failed to fetch props for event {eid}: {e}")
            logger.info(f"UnifiedIngestion: Successfully fetched props for {prop_counts} events for {sport_key}")

        # Task 4: Merge Betstack Props
        betstack_records = []
        try:
            logger.info(f"UnifiedIngestion: Fetching Betstack props for {sport_key}")
            # Normalize sport key for Betstack (e.g., basketball_nba -> nba)
            betstack_sport = "nba" if "nba" in sport_key else sport_key
            betstack_raw = await _real_sports_api_instance.fetch_props_from_betstack(betstack_sport)
            if betstack_raw and isinstance(betstack_raw, list):
                for p in betstack_raw:
                    # Normalize Betstack into PropRecord
                    betstack_records.append(PropRecord(
                        sport=sport_key,
                        game_id=p.get("game_id"),
                        player_name=p.get("player_name"),
                        market_key=p.get("market_key"),
                        book="betstack",
                        line=Decimal(str(p.get("line", 0))),
                        odds_over=Decimal(str(p.get("odds_over", -110))),
                        odds_under=Decimal(str(p.get("odds_under", -110))),
                        source_ts=datetime.now(timezone.utc)
                    ))
                logger.info(f"UnifiedIngestion: Merged {len(betstack_records)} Betstack records.")
        except Exception as e:
            logger.error(f"UnifiedIngestion: Betstack fetch failed: {e}")

        # 3. Normalize into PropRecords
        records = odds_mapper.map_theodds_props_to_records(odds_raw, metadata_map, sport_key)
        
        # Merge logic (Betstack + Primary)
        combined_records = records + betstack_records
        
        # Normalize player_name for all records to avoid NULLs breaking filters/constraints
        for r in combined_records:
            if not r.player_name:
                r.player_name = r.home_team or "Matchup"
        
        # 3b. Market Intelligence: Best Odds, Soft/Sharp flagging
        records = self.enrich_with_market_intel(combined_records)
        metrics["odds_count"] = len(records)
        
        # 4. Standardized Persistence
        if sport_key in PROP_MARKETS_BY_SPORT:
            await delete_props_for_sport(sport_key)
            
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
                "player_name": r.player_name, # Already normalized above
                "bookmaker": r.book,
                "line": float(r.line) if r.line is not None else None,
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

        # Task 6: Diagnostic Logging for Unified Odds (instrumented per user request)
        if unified_rows:
            try:
                logger.info(f"UnifiedIngestion: preparing to write {len(unified_rows)} unified odds rows for {sport_key}")
                await upsert_unified_odds(unified_rows)
                logger.info(f"UnifiedIngestion: successfully wrote unified odds rows for {sport_key}")
                metrics["rows_upserted"] = len(unified_rows)
            except Exception as e:
                logger.error(f"UnifiedIngestion: upsert_unified_odds failed for {sport_key}: {e}", exc_info=True)
                metrics["errors"].append(f"Unified Odds Persistence: {str(e)}")
        else:
            logger.warning(f"UnifiedIngestion: No unified rows generated for {sport_key}")

        # 5. Trigger Brain & EV
        secondary_tasks = [
            ("Sharp Money", lambda: sharp_money_brain.detect_signals(sport_key)),
            ("CLV Tracker", lambda: brain_clv_tracker.record_opening_line(records)),
            ("Injury Impact", lambda: injury_impact_brain.analyze_impacts(sport_key)),
            ("EV Engine", lambda: ev_engine.run_ev_cycle(sport_key)),
            ("Alert Writer", lambda: run_alert_detection(sport_key)),
            ("EV Writer", lambda: run_ev_grader(sport_key)),
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
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(f"INFO: [{sport_key}] Ingest complete — {metrics['events_count']} odds events, {metrics['rows_upserted']} props upserted, source: {source_name}, elapsed: {elapsed:.1f}s")
        
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
                
                # Standardized confidence metric: capped at 0.95, 4 decimal precision
                raw_conf = float(len(prop_group) / 10.0)
                r.confidence = round(min(raw_conf, 0.95), 4)
                
        return records

unified_ingestion = UnifiedIngestionService()
