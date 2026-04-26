# apps/api/src/services/unified_ingestion.py
"""
Unified odds/props ingestion — staged pipeline vs external providers.

Layers (conceptual)::

    [1] Odds board — ``waterfall_router.get_data(..., data_type="odds", skip_cache=True)``
        walks ``core.waterfall_config`` (The Odds API, BetStack, TheRundown, SportsGameOdds,
        iSports, API-Sports, …) until a provider returns events. Player props still use
        ``odds_api_client`` when keys exist (no multi-provider props client in-repo yet).
    [2] BetStack consensus — ``_real_sports_api_instance.fetch_props_from_betstack``: extra
        consensus rows where configured (see ``LUCRIX_TO_BETSTACK_LEAGUE``).
    [3] Optional Kalshi — cross-signal / contract context when tier flags allow
        (not wired as the primary American-odds waterfall slot).
    [4] Persistence — ``upsert_props_live``, ``upsert_unified_odds``, props history,
        heartbeats, downstream EV/grader hooks.

``real_data_connector.fetch_games_by_sport`` (schedule-shaped waterfall) is used only when
the odds chain returns no events. See ``docs/WATERFALL_PROVIDER_MATRIX.md``.
"""
import logging
import asyncio
import json
import os
import traceback
from datetime import datetime, timedelta, timezone
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
from services.waterfall_router import waterfall_router # type: ignore
from services.commence_time import (  # type: ignore
    event_commence_utc,
    reject_absurd_future,
    parse_commence_to_utc,
)
from brain.engine import brain_governor  # type: ignore
from services.ingestion_job_guard import try_start_job, finish_job

logger = logging.getLogger(__name__)


def _is_auth_failure_error(err: Exception) -> bool:
    msg = str(err).lower()
    return "authentication" in msg or "password authentication failed" in msg


def _is_transient_retryable_error(err: Exception) -> bool:
    msg = str(err).lower()
    transient_markers = (
        "timeout",
        "temporarily unavailable",
        "connection reset",
        "connection refused",
        "network",
    )
    return any(marker in msg for marker in transient_markers)

class UnifiedIngestionService:
    @staticmethod
    def american_to_implied(american: int) -> Decimal:
        if american > 0:
            return Decimal(100) / Decimal(american + 100)
        return Decimal(abs(american)) / Decimal(abs(american) + 100)

    @staticmethod
    def _event_commence_utc(event: Dict[str, Any]) -> Optional[datetime]:
        return event_commence_utc(event)

    @staticmethod
    def _filter_stale_odds_events(odds_raw: List[Any], sport_key: str) -> List[Dict[str, Any]]:
        """Drop odds-shaped events outside ingest window before any deeper processing."""
        max_days = int(os.getenv("INGEST_DROP_EVENTS_OLDER_THAN_DAYS", "10"))
        max_future_days = int(os.getenv("INGEST_MAX_FUTURE_GAME_DAYS", "21"))
        if max_days <= 0:
            return [e for e in odds_raw if isinstance(e, dict)]
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
        future_cutoff = datetime.now(timezone.utc) + timedelta(days=max_future_days)
        out: List[Dict[str, Any]] = []
        dropped_old = 0
        dropped_future = 0
        for e in odds_raw:
            if not isinstance(e, dict):
                continue
            t = UnifiedIngestionService._event_commence_utc(e)
            if t is None:
                out.append(e)
                continue
            if t < cutoff:
                dropped_old += 1
                continue
            if t > future_cutoff:
                dropped_future += 1
                continue
            if t >= cutoff:
                out.append(e)
        total_dropped = dropped_old + dropped_future
        if total_dropped:
            logger.warning(
                "UnifiedIngestion: skipped %s stale events outside ingest window for %s (old=%s future=%s)",
                total_dropped,
                sport_key,
                dropped_old,
                dropped_future,
            )
        return out

    @staticmethod
    def _build_metadata_map(odds_raw: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Per-event metadata for props mapping. Same event id can appear multiple times in
        odds_raw (board snapshot + per-event player props). Merge so a later row without
        commence_time does not wipe a valid game_time, and reject far-future placeholders.
        """
        metadata_map: Dict[str, Any] = {}
        for e in odds_raw:
            eid = e.get("id")
            if not eid:
                continue
            new_t = reject_absurd_future(event_commence_utc(e))
            ht = e.get("home_team")
            at = e.get("away_team")
            prev = metadata_map.get(eid)
            if prev:
                game_time = new_t or prev.get("game_time")
                home_team = ht or prev.get("home_team")
                away_team = at or prev.get("away_team")
            else:
                game_time = new_t
                home_team = ht
                away_team = at
            metadata_map[eid] = {
                "home_team": home_team,
                "away_team": away_team,
                "game_time": game_time,
            }
        return metadata_map

    async def run(self, sport_key: str):
        start_time = datetime.now(timezone.utc)
        logger.debug(f"=== WATERFALL STAGE 0: INIT for {sport_key} START ===")
        source_name = "none"
        from workers.ev_engine import ev_engine # type: ignore
        errors: List[str] = []
        metrics: Dict[str, Any] = {
            "sport": sport_key,
            "status": "started",
            "events_count": 0,
            "odds_count": 0,
            "rows_upserted": 0,
            "errors": errors,
            "odds_api_all_keys_cooldown": False,
        }

        # All Odds API keys in cooldown: skip this cycle (avoids waterfall/TOA hammer + log spam).
        if odds_api_client.is_configured and odds_api_client.all_keys_unavailable():
            logger.info(
                "UnifiedIngestion: All The Odds API keys cooling down — skipping full cycle for %s",
                sport_key,
            )
            metrics["status"] = "skipped"
            metrics["skipped_reason"] = "all_odds_keys_cooldown"
            metrics["odds_api_all_keys_cooldown"] = True
            skip_hb = os.getenv("SKIP_HEARTBEAT_WHEN_ODDS_KEYS_COOLDOWN", "true").strip().lower() in (
                "1",
                "true",
                "yes",
                "on",
            )
            if not skip_hb:
                try:
                    async with async_session_maker() as session:
                        await HeartbeatService.log_heartbeat(
                            session,
                            f"ingest_{sport_key}",
                            status="idle_no_data",
                            rows_written=0,
                            error_count=0,
                            meta={
                                "metrics": metrics,
                                "skipped_reason": "all_odds_keys_cooldown",
                            },
                        )
                except Exception as hb_err:
                    logger.warning(
                        "UnifiedIngestion: heartbeat after odds cooldown skip failed: %s",
                        hb_err,
                    )
            return metrics

        # 0b. Active Brain governor — skip network when quota is hard-stopped or cache is fresh enough
        async with async_session_maker() as _brain_sess:
            plan = await brain_governor.plan_ingest(_brain_sess, sport_key)
        async with async_session_maker() as _log_sess:
            await brain_governor.log_decision(_log_sess, plan)

        if plan.skip_network:
            logger.info(
                "[BRAIN] %s — skip_network (%s) quota_pct=%.3f cache_age_min=%s",
                sport_key,
                plan.reason,
                plan.quota_pct,
                plan.cache_age_minutes,
            )
            metrics["status"] = "skipped"
            metrics["skipped_reason"] = plan.reason
            metrics["brain"] = plan.to_metrics_dict()
            await self.run_intelligence_pipeline(sport_key, [])
            try:
                async with async_session_maker() as session:
                    await brain_advanced_service.generate_model_picks(sport_key, session)
            except Exception as e:
                metrics["errors"].append(f"ModelPick Promotion: {str(e)}")
                logger.error("UnifiedIngestion: ModelPick promotion failed (brain skip path): %s", e)
            async with async_session_maker() as session:
                await HeartbeatService.log_heartbeat(
                    session,
                    f"ingest_{sport_key}",
                    status="idle_no_data" if not plan.blocked_quota else "error",
                    rows_written=0,
                    error_count=len(metrics["errors"]),
                    meta={"metrics": metrics, "brain_skip": True},
                )
            return metrics
        
        # 1. Fetch odds-shaped events (multi-provider chain, not TOA-only)
        logger.debug(f"=== WATERFALL STAGE 1: FETCH ODDS for {sport_key} START ===")
        if not odds_api_client.is_configured:
            logger.info(
                "UnifiedIngestion: The Odds API keys not set — using odds waterfall only "
                "(BetStack / other configured providers); player props via TOA are skipped"
            )

        try:
            odds_raw = await waterfall_router.get_data(
                sport_key, data_type="odds", skip_cache=True
            )
            if not isinstance(odds_raw, list):
                odds_raw = []

            if odds_raw:
                prov = next(
                    (
                        e.get("source_provider")
                        for e in odds_raw
                        if isinstance(e, dict) and e.get("source_provider")
                    ),
                    None,
                )
                source_name = prov or "waterfall"

            if not odds_raw:
                logger.info(
                    "UnifiedIngestion: Odds waterfall returned no events for %s; trying schedule fallback",
                    sport_key,
                )
                fallback_data = await real_data_connector.fetch_games_by_sport(sport_key)
                if fallback_data:
                    fb0 = fallback_data[0] if fallback_data else {}
                    source_name = (
                        fb0.get("source_provider")
                        or fb0.get("source")
                        or "schedule_fallback"
                    )
                    odds_raw = []
                    for g in fallback_data:
                        st = g.get("start_time")
                        if isinstance(st, datetime):
                            dt = reject_absurd_future(parse_commence_to_utc(st))
                        else:
                            dt = reject_absurd_future(
                                parse_commence_to_utc(st) or parse_commence_to_utc(g.get("date"))
                            )
                        commence_iso = (
                            dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
                            if dt
                            else ""
                        )
                        odds_raw.append(
                            {
                                "id": g.get("id"),
                                "sport_key": sport_key,
                                "home_team": g.get("home_team"),
                                "away_team": g.get("away_team"),
                                "commence_time": commence_iso,
                                "bookmakers": g.get("raw_bookmakers_data", []),
                            }
                        )
                elif not odds_api_client.is_configured:
                    logger.warning(
                        "UnifiedIngestion: No odds events for %s and The Odds API not configured",
                        sport_key,
                    )

        except Exception as e:
            metrics["errors"].append(f"Ingest Fetch: {str(e)}")
            logger.error(f"UnifiedIngestion: Failed to fetch data: {e}")
            odds_raw = []

        odds_raw = UnifiedIngestionService._filter_stale_odds_events(odds_raw, sport_key)
        metadata_map = UnifiedIngestionService._build_metadata_map(odds_raw)
        metrics["events_count"] = len(odds_raw)
        logger.info(
            "UnifiedIngestion: %s events from %s for %s (after stale-event filter)",
            metrics["events_count"],
            source_name,
            sport_key,
        )

        if odds_raw:
            try:
                async with async_session_maker() as _oc:
                    await brain_governor.persist_odds_cache_snapshot(
                        _oc, sport_key, odds_raw, source_name
                    )
            except Exception as snap_err:
                logger.debug("odds_cache snapshot: %s", snap_err)
            try:
                from services.line_tracker import (
                    snapshot_lines_from_odds_api,
                    cleanup_old_snapshots,
                )
                from services.arb_calculator import find_and_store_arbs

                async with async_session_maker() as _lt:
                    await snapshot_lines_from_odds_api(_lt, sport_key, odds_raw)
                async with async_session_maker() as _cl:
                    await cleanup_old_snapshots(_cl, 48)
                async with async_session_maker() as _arb:
                    await find_and_store_arbs(_arb, sport_key, odds_raw)
            except Exception as post_err:
                logger.debug("post-odds snapshot/arb: %s", post_err)

        logger.debug(f"=== WATERFALL STAGE 1: FETCH ODDS for {sport_key} COMPLETE — {len(odds_raw)} events ===")
        # 2d. Fetch Player Props (Requires per-event calls)
        logger.debug(f"=== WATERFALL STAGE 2: FETCH PLAYER PROPS for {sport_key} START ===")
        PROP_MARKETS_BY_SPORT = {
            "basketball_nba": "player_points,player_rebounds,player_assists",
            "americanfootball_nfl": "player_pass_yds,player_rush_yds",
            "icehockey_nhl": "player_points,player_shots_on_goal",
            "baseball_mlb": "pitcher_strikeouts,batter_hits"
        }
        
        # Quota Safety: Only fetch props for sports currently in-season (March 2026)
        # NFL is in off-season, NHL/NBA/MLB are active.
        IN_SEASON_PROP_SPORTS = ["basketball_nba", "baseball_mlb", "icehockey_nhl"]

        quota_mode = "normal"
        try:
            from services.external_api_gateway import external_api_gateway
            quota_state = await external_api_gateway.quota_status("theoddsapi")
            quota_mode = str(quota_state.get("mode") or "normal")
        except Exception as quota_err:
            logger.debug("UnifiedIngestion: quota status unavailable: %s", quota_err)

        if (
            odds_api_client.is_configured
            and sport_key in PROP_MARKETS_BY_SPORT
            and sport_key in IN_SEASON_PROP_SPORTS
        ):
            # Quota: cap per-event TOA calls (INGEST_TOA_MAX_EVENTS_PER_CYCLE, default 15)
            max_events = max(1, int(os.getenv("INGEST_TOA_MAX_EVENTS_PER_CYCLE", "15")))
            if quota_mode in {"conservative", "protection"}:
                max_events = min(max_events, 6)
            elif quota_mode == "emergency_freeze":
                max_events = 0
            active_events: List[str] = []
            valid_event_ids = await odds_api_client.get_valid_event_ids(sport_key)
            for k in metadata_map.keys():
                if len(active_events) >= max_events:
                    break
                if not odds_api_client.is_valid_event_id(k):
                    logger.warning("UnifiedIngestion: skipping invalid TheOddsAPI event_id '%s'", k)
                    continue
                if valid_event_ids and k not in valid_event_ids:
                    logger.warning("UnifiedIngestion: skipping stale TheOddsAPI event_id '%s'", k)
                    continue
                active_events.append(k)

            toa_keys_cooldown = odds_api_client.all_keys_unavailable()
            metrics["odds_api_all_keys_cooldown"] = toa_keys_cooldown
            if toa_keys_cooldown:
                logger.info(
                    "UnifiedIngestion: All The Odds API keys cooling down — skipping TOA player props "
                    "for %s (%s events); waterfall/Betstack paths still run",
                    sport_key,
                    len(active_events),
                )
            else:
                logger.info(
                    "UnifiedIngestion: Fetching player props for %s %s events...",
                    len(active_events),
                    sport_key,
                )

            prop_counts: int = 0
            market_set = PROP_MARKETS_BY_SPORT[sport_key]
            if quota_mode in {"conservative", "protection"}:
                market_set = market_set.split(",")[0]
            for eid in ([] if toa_keys_cooldown else active_events):
                if odds_api_client.quota_conserve_player_props():
                    logger.info(
                        "UnifiedIngestion: Stopping TOA player props early (quota conserve / "
                        "THE_ODDS_API_MIN_REMAINING_BEFORE_STOP) for %s after %s events",
                        sport_key,
                        prop_counts,
                    )
                    break
                try:
                    # Attempt primary prop fetch
                    event_props = await odds_api_client.get_player_props(
                        sport=sport_key,
                        event_id=eid,
                        markets=market_set
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

        # Task 4: Merge BetStack consensus lines (free API: events + lines, no player props)
        betstack_records = []
        try:
            logger.info(f"UnifiedIngestion: Fetching Betstack lines for {sport_key}")
            betstack_raw = await _real_sports_api_instance.fetch_props_from_betstack(sport_key)
            if betstack_raw and isinstance(betstack_raw, list):
                now_ts = datetime.now(timezone.utc)
                for p in betstack_raw:
                    if not isinstance(p, dict) or not p.get("game_id"):
                        continue
                    gst = p.get("game_start_time")
                    if gst is not None and not isinstance(gst, datetime):
                        gst = None
                    betstack_records.append(
                        PropRecord(
                            sport=sport_key,
                            game_id=str(p["game_id"]),
                            player_name=p.get("player_name"),
                            home_team=p.get("home_team"),
                            away_team=p.get("away_team"),
                            game_start_time=gst,
                            market_key=p.get("market_key") or "totals",
                            book="betstack",
                            line=Decimal(str(p.get("line", 0))),
                            odds_over=Decimal(str(p.get("odds_over", -110))),
                            odds_under=Decimal(str(p.get("odds_under", -110))),
                            source_ts=now_ts,
                        )
                    )
                logger.info(f"UnifiedIngestion: Merged {len(betstack_records)} Betstack records.")
        except Exception as e:
            logger.warning("UnifiedIngestion: Betstack fetch failed (non-fatal): %s", e)

        odds_raw = UnifiedIngestionService._filter_stale_odds_events(odds_raw, sport_key)
        metadata_map = UnifiedIngestionService._build_metadata_map(odds_raw)

        logger.debug(f"=== WATERFALL STAGE 2: FETCH PLAYER PROPS for {sport_key} COMPLETE ===")
        # 3. Normalize into PropRecords
        logger.debug(f"=== WATERFALL STAGE 3: NORMALIZE & ENRICH for {sport_key} START ===")
        records = odds_mapper.map_theodds_props_to_records(odds_raw, metadata_map, sport_key)
        
        # Merge logic (Betstack + Primary)
        combined_records = records + betstack_records
        
        # Normalize player_name for all records to avoid NULLs breaking filters/constraints
        for r in combined_records:
            if not r.player_name:
                r.player_name = r.home_team or "Matchup"
            if r.game_start_time is not None and reject_absurd_future(r.game_start_time) is None:
                r.game_start_time = None

        # 3b. Market Intelligence: Best Odds, Soft/Sharp flagging
        records = self.enrich_with_market_intel(combined_records)
        metrics["odds_count"] = len(records)
        
        logger.debug(f"=== WATERFALL STAGE 3: NORMALIZE & ENRICH for {sport_key} COMPLETE — {len(records)} records ===")
        # 4. Standardized Persistence
        logger.debug(f"=== WATERFALL STAGE 4: PERSIST for {sport_key} START ===")
        # Only delete old data if we have a substantial replacement set (>=10 records).
        # This prevents partial API responses or exhausted keys from wiping the table.
        MIN_RECORDS_FOR_DELETE = 10
        if sport_key in PROP_MARKETS_BY_SPORT and len(records) >= MIN_RECORDS_FOR_DELETE:
            await delete_props_for_sport(sport_key)
        elif sport_key in PROP_MARKETS_BY_SPORT and 0 < len(records) < MIN_RECORDS_FOR_DELETE:
            logger.warning(f"UnifiedIngestion: Only {len(records)} records for {sport_key} — skipping delete to preserve existing data")
            
        if records:
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

        logger.debug(f"=== WATERFALL STAGE 4: PERSIST for {sport_key} COMPLETE — {metrics['rows_upserted']} rows ===")
        # 5. Trigger Unified Intelligence Pipeline
        logger.debug(f"=== WATERFALL STAGE 5: INTELLIGENCE PIPELINE for {sport_key} START ===")
        await self.run_intelligence_pipeline(sport_key, records)

        logger.debug(f"=== WATERFALL STAGE 5: INTELLIGENCE PIPELINE for {sport_key} COMPLETE ===")
        # 6. Promote EV signals to ModelPicks
        logger.debug(f"=== WATERFALL STAGE 6: MODEL PICK PROMOTION for {sport_key} START ===")
        try:
            async with async_session_maker() as session:
                await brain_advanced_service.generate_model_picks(sport_key, session)
            logger.info(f"UnifiedIngestion: Successfully promoted ModelPicks for {sport_key}")
        except Exception as e:
            metrics["errors"].append(f"ModelPick Promotion: {str(e)}")
            logger.error(f"UnifiedIngestion: ModelPick promotion failed: {e}")

        logger.debug(f"=== WATERFALL STAGE 6: MODEL PICK PROMOTION for {sport_key} COMPLETE ===")
        try:
            from services.props_service import get_all_props
            from services.arb_calculator import find_and_store_arb_from_props

            props_arb = await get_all_props(sport_filter=sport_key)
            async with async_session_maker() as _ab:
                n_arb = await find_and_store_arb_from_props(_ab, sport_key, props_arb)
            if n_arb:
                logger.info("UnifiedIngestion: stored %s prop-based arb rows for %s", n_arb, sport_key)
        except Exception as arb_err:
            logger.debug("UnifiedIngestion: prop arb persistence skipped: %s", arb_err)

        metrics["status"] = "completed" if not metrics["errors"] else "partial_success"
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(f"INFO: [{sport_key}] Ingest complete — {metrics['events_count']} odds events, {metrics['rows_upserted']} props upserted, source: {source_name}, elapsed: {elapsed:.1f}s")

        # Update system_sync_state timestamps
        try:
            from sqlalchemy import text as sa_text
            async with async_session_maker() as ss:
                await ss.execute(sa_text(
                    "UPDATE system_sync_state SET last_odds_sync = NOW(), updated_at = NOW() WHERE id = 1"
                ))
                await ss.commit()
        except Exception as sync_err:
            logger.warning(f"UnifiedIngestion: Failed to update sync state: {sync_err}")

        async with async_session_maker() as session:
            await HeartbeatService.log_heartbeat(
                session, 
                f"ingest_{sport_key}", 
                status="ok" if not metrics["errors"] else "error",
                rows_written=metrics.get("rows_upserted", 0),
                error_count=len(metrics["errors"]),
                meta={"metrics": metrics}
            )

        return metrics

    async def run_with_retries(self, sport_key: str, retries: int = 3):
        """Robust entrypoint with exponential backoff for transient API failures."""
        run_id = await try_start_job(f"ingest_{sport_key}")
        if run_id is None:
            logger.info("UnifiedIngestion: skip overlap for %s (already running)", sport_key)
            return
        for i in range(retries):
            try:
                metrics = await self.run(sport_key)
                await finish_job(
                    run_id,
                    status="ok",
                    rows_written=int((metrics or {}).get("rows_upserted", 0)),
                    error_message=None,
                )
                return
            except Exception as e:
                if _is_auth_failure_error(e):
                    logger.critical(
                        "UnifiedIngestion: AUTH failure for %s (no retry): %s",
                        sport_key,
                        e,
                    )
                    await finish_job(run_id, status="auth_failure", rows_written=0, error_message=str(e))
                    raise

                retryable = _is_transient_retryable_error(e)
                logger.error(f"UnifiedIngestion: Attempt {i+1}/{retries} failed for {sport_key}: {e}")
                if retryable and i < retries - 1:
                    wait = 2 ** i
                    logger.info(f"UnifiedIngestion: Retrying in {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    if not retryable:
                        logger.error(
                            "UnifiedIngestion: Non-transient failure for %s (no further retries).",
                            sport_key,
                        )
                    logger.critical(f"UnifiedIngestion: ALL ATTEMPTS FAILED for {sport_key}")
                    await finish_job(run_id, status="failed", rows_written=0, error_message=str(e))
                    async with async_session_maker() as session:
                        await HeartbeatService.log_heartbeat(
                            session, 
                            f"ingest_{sport_key}", 
                            status="pipeline_error",
                            meta={"error": str(e), "attempts": retries}
                        )

    async def run_intelligence_pipeline(self, sport: str, records: List[PropRecord]):
        """
        Single orchestrator for all post-ingestion scoring.
        Ensures data dependencies and standardized output.
        """
        logger.info(f"🚀 [INTELLIGENCE PIPELINE] Starting for {sport}...")
        
        try:
            # Step 1: EV Calculations (The Core)
            from services.ev_service import ev_service # type: ignore
            await ev_service.run_ev_cycle(sport)
            
            # Notify WebSocket clients
            from routers.ws_ev import notify_ev_update # type: ignore
            await notify_ev_update(sport)
            
            # Step 2: Signal Detection (Whales, Steam, Sharps)
            from services.alert_writer import run_alert_detection # type: ignore
            await run_alert_detection(sport)
            
            # Step 3–4: Analytical extras + news (explicit gather — all tasks are coroutines)
            from services.news_service import news_service

            extra_names = (
                "sharp_money",
                "clv_opening",
                "injury_impact",
                "news",
            )
            extras = await asyncio.gather(
                sharp_money_brain.detect_signals(sport),
                brain_clv_tracker.record_opening_line(records),
                injury_impact_brain.analyze_impacts(sport),
                news_service.get_news(sport),
                return_exceptions=True,
            )
            for name, res in zip(extra_names, extras):
                if isinstance(res, BaseException):
                    logger.error(
                        "❌ [INTELLIGENCE PIPELINE] extra task %s failed for %s: %s",
                        name,
                        sport,
                        res,
                        exc_info=(type(res), res, res.__traceback__),
                    )

            logger.info(f"✅ [INTELLIGENCE PIPELINE] Completed for {sport}")
        except Exception as e:
            logger.error(f"❌ [INTELLIGENCE PIPELINE] Failed for {sport}: {e}")

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
                raw_conf = len(prop_group) / 10.0
                r.confidence = round(float(min(raw_conf, 0.95)), 4)  # type: ignore (Stale/Inaccurate check)
                
        return records

unified_ingestion = UnifiedIngestionService()
