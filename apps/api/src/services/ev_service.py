# apps/api/src/services/ev_service.py
import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy import select, func, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from db.session import async_session_maker, engine
from models import UnifiedOdds, UnifiedEVSignal
from services.heartbeat_service import HeartbeatService
from services.persistence_helpers import insert_edges_ev_history
from core.config import settings

logger = logging.getLogger(__name__)

class EVService:
    def __init__(self):
        self.version = "v2-sharp-weighted"

    async def run_ev_cycle(self, sport: str):
        try:
            async with async_session_maker() as session:
                # 1. Load odds via Raw SQL for total visibility (bypassing model mapping issues)
                res = await session.execute(text("SELECT * FROM unified_odds"))
                all_records = res.mappings().all()
                
                # Filter for sport keywords in Python
                keywords = [sport.lower()]
                if "_" in sport: keywords.append(sport.split('_')[-1].lower())
                
                all_odds = [o for o in all_records if any(k in (o.get("sport") or "").lower() for k in keywords)]
                
                logger.info(f"EVService: Visibility Check — Total DB Rows={len(all_records)}, Matches for {sport}={len(all_odds)}")
                
                if not all_odds:
                    logger.info(f"EVService: No odds found in unified_odds for sport={sport}")
                    await HeartbeatService.log_heartbeat(session, f"ev_grader_{sport}", status="idle_no_data", rows_written=0)
                    return

                logger.info(f"EVService: Processing {len(all_odds)} rows for sport={sport}")

                # Grouping: (eid, mkey, line, p_name) -> outcome -> book -> (price, imp)
                grouped = {}
                meta_map = {} # eid -> (league, game_time)
                for o in all_odds:
                    meta_map[o.event_id] = (o.league, o.game_time)
                    key = (o.event_id, o.market_key, float(o.line) if o.line is not None else 0.0, o.player_name)
                    outcome_lower = o.outcome_key.lower()
                    if key not in grouped: grouped[key] = {}
                    if outcome_lower not in grouped[key]: grouped[key][outcome_lower] = {}
                    
                    price = float(o.price or 0)
                    prob = float(o.implied_prob or 0)
                    
                    if price > 0 and prob > 0:
                        grouped[key][o.outcome_key][o.bookmaker] = (price, prob)

                # 2. Compute Signals
                signals = []
                for (eid, mkey, line, p_name), outcomes in grouped.items():
                    if len(outcomes) < 2: continue # Need both sides (over/under)
                    
                    # Compute Weighted Fair Price
                    # Logic: Sharp books get higher weight (e.g. 3.0x) vs Soft books (1.0x)
                    fair_probs = self._calculate_sharp_weighted_fair_probs(outcomes)
                    if not fair_probs: continue

                    # 3. Detect Edges against thresholds
                    for outcome, side_books in outcomes.items():
                        true_p = fair_probs.get(outcome, 0)
                        if true_p <= 0: continue

                        for book, (price, implied) in side_books.items():
                            edge = (true_p - implied) * 100
                            
                            # Only keep if edge > minimum threshold
                            if edge >= settings.EV_MIN_THRESHOLD:
                                signals.append({
                                    'sport': sport,
                                    'league': meta_map[eid][0],
                                    'game_start_time': meta_map[eid][1],
                                    'event_id': eid,
                                    'market_key': mkey,
                                    'outcome_key': outcome,
                                    'player_name': p_name,
                                    'bookmaker': book,
                                    'book': book, # Alias
                                    'price': price,
                                    'odds': price, # Alias
                                    'line': line,
                                    'true_prob': true_p,
                                    'fair_prob': true_p, # Legacy alias
                                    'edge_percent': edge,
                                    'ev_percent': edge, # Legacy alias
                                    'ev_percentage': edge, # Frontend expected
                                    'ev_score': edge / 100.0, # Decimal score
                                    'implied_prob': implied,
                                    'market_prob': implied, # Legacy alias
                                    'confidence': 0.7, # Default confidence for EV signals
                                    'recommendation': outcome.upper(),
                                    'engine_version': self.version
                                })

                if signals:
                    logger.info(f"EVService: Generated {len(signals)} edges for sport={sport}")
                    await self.upsert_ev_signals(signals)
                    await HeartbeatService.log_heartbeat(session, f"ev_grader_{sport}", status="ok", rows_written=len(signals))
                else:
                    # Lower threshold check
                    threshold = getattr(settings, "EV_MIN_THRESHOLD", 0.5)
                    logger.info(f"EVService: No edges exceeding {threshold}% found for sport={sport} (Found {len(grouped)} market groups)")
                    await HeartbeatService.log_heartbeat(session, f"ev_grader_{sport}", status="idle_no_edges", rows_written=0)
        except Exception as e:
            logger.error(f"EVService CRASH for {sport}: {e}")
            async with async_session_maker() as session:
                await HeartbeatService.log_heartbeat(session, f"ev_grader_{sport}", status="error", error_count=1)
            raise e

    def _calculate_sharp_weighted_fair_probs(self, outcomes: Dict[str, Dict[str, Tuple[float, float]]]) -> Dict[str, float]:
        """
        Logic:
        1. For each outcome, compute a weighted average of implied probabilities.
        2. Sharp books (Pinnacle, etc) get higher weight.
        3. Normalize result to sum to 1.0.
        """
        weights = {}
        weighted_probs = {}
        
        for outcome, books in outcomes.items():
            total_w = 0.0
            total_wp = 0.0
            for book, (price, prob) in books.items():
                # Sharp check
                is_sharp = any(s in book.lower() for s in settings.SHARP_BOOKMAKERS)
                weight = 3.0 if is_sharp else 1.0
                
                total_w += weight
                total_wp += (prob * weight)
            
            if total_w > 0:
                weighted_probs[outcome] = total_wp / total_w
            else:
                weighted_probs[outcome] = 0.0

        # Normalize (Remove Vig)
        total_market_prob = sum(weighted_probs.values())
        if total_market_prob <= 0: return {}
        
        return {o: p / total_market_prob for o, p in weighted_probs.items()}

    async def upsert_ev_signals(self, signals: List[Dict]):
        from sqlalchemy import text
        async with async_session_maker() as session:
            try:
                is_sqlite = "sqlite" in str(engine.url)

                # 1. UPSERT Live Signals
                for s in signals:
                    valid_cols = ["sport", "sport_key", "prop_type", "event_id", "market_key", "outcome_key", "player_name", 
                                  "bookmaker", "price", "line", "true_prob", "edge_percent", "ev_percentage",
                                  "implied_prob", "confidence", "engine_version"]
                    row = {k: v for k, v in s.items() if k in valid_cols}
                    row.setdefault("sport_key", s["sport"])
                    row.setdefault("ev_percentage", row.get("edge_percent", 0))
                    row.setdefault("prop_type", "unknown")
                    if row.get("prop_type") is None:
                        row["prop_type"] = "unknown"
                    # Ensure numeric fields are floats
                    for col in ["price", "line", "true_prob", "edge_percent", "implied_prob", "confidence"]:
                        if col in row and row[col] is not None:
                            row[col] = float(row[col])

                    if is_sqlite:
                        ins_obj = sqlite_insert(UnifiedEVSignal).values(row)
                        stmt = ins_obj.on_conflict_do_update(
                            index_elements=['sport', 'event_id', 'market_key', 'outcome_key', 'bookmaker', 'engine_version'],
                            set_={k: v for k, v in row.items() if k not in ['sport', 'event_id', 'market_key', 'outcome_key', 'bookmaker', 'engine_version', 'created_at']}
                        )
                        await session.execute(stmt)
                    else:
                        # Raw SQL fallback for Postgres as pg_insert is acting up with true_prob
                        row["recommendation"] = s.get("recommendation")
                        base_sql = """
                        INSERT INTO ev_signals (sport, sport_key, prop_type, event_id, market_key, outcome_key, player_name, bookmaker, price, line, true_prob, edge_percent, ev_percentage, implied_prob, confidence, engine_version, recommendation, created_at, updated_at)
                        VALUES (:sport, :sport_key, :prop_type, :event_id, :market_key, :outcome_key, :player_name, :bookmaker, :price, :line, :true_prob, :edge_percent, :ev_percentage, :implied_prob, :confidence, :engine_version, :recommendation, now(), now())
                        """
                        update_clause = """
                        DO UPDATE SET 
                            price = EXCLUDED.price, 
                            line = EXCLUDED.line, 
                            true_prob = EXCLUDED.true_prob, 
                            edge_percent = EXCLUDED.edge_percent, 
                            implied_prob = EXCLUDED.implied_prob, 
                            confidence = EXCLUDED.confidence,
                            recommendation = EXCLUDED.recommendation,
                            updated_at = now()
                        """
                        if row.get("player_name"):
                            sql = base_sql + " ON CONFLICT (sport, event_id, player_name, market_key, outcome_key, bookmaker, engine_version) WHERE player_name IS NOT NULL " + update_clause
                        else:
                            sql = base_sql + " ON CONFLICT (sport, event_id, market_key, outcome_key, bookmaker, engine_version) WHERE player_name IS NULL " + update_clause
                            
                        await session.execute(text(sql), row)
                
                # 2. Historical edges_ev_history via shared persistence (market_label + validation)
                history_rows = []
                for s in signals:
                    ln = s.get("line")
                    try:
                        line_f = float(ln) if ln is not None else 0.0
                    except (TypeError, ValueError):
                        line_f = 0.0
                    history_rows.append(
                        {
                            "sport": s["sport"],
                            "league": s.get("league"),
                            "game_id": s["event_id"],
                            "game_start_time": s.get("game_start_time"),
                            "player_id": s.get("player_name") or "unknown",
                            "player_name": s.get("player_name"),
                            "team": s.get("team") or s.get("home_team") or s.get("away_team"),
                            "market_key": s["market_key"],
                            "line": line_f,
                            "book": s["bookmaker"],
                            "side": s["outcome_key"],
                            "odds": float(s["price"]),
                            "model_prob": float(s["true_prob"]),
                            "implied_prob": float(s["implied_prob"]),
                            "edge_pct": float(s["edge_percent"]),
                            "source": f"brain_ev_{self.version}",
                        }
                    )

                await session.commit()

                if history_rows:
                    await insert_edges_ev_history(history_rows)
            except Exception as e:
                await session.rollback()
                logger.error(f"EVService: Signal persistence failed: {e}")
                raise e

ev_service = EVService()
