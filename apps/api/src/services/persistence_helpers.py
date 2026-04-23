# apps/api/src/services/persistence_helpers.py
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from db.session import async_session_maker, engine
from models import PropLive, PropHistory, EdgeEVHistory
from services.market_labeling import derive_market_label
from models.brain import WhaleMove, CLVRecord, InjuryImpactEvent
from schemas.props import PropRecord
from sqlalchemy import text

logger = logging.getLogger(__name__)

async def upsert_props_live(records: List[PropRecord]):
    """Standardized upsert into public.props_live using raw SQL for robustness."""
    if not records: 
        return
    
    async with async_session_maker() as session:
        try:
            now = datetime.now(timezone.utc)
            rows = []
            for r in records:
                # Include all fields, even None, to satisfy SQLAlchemy bound parameters
                row = r.dict()
                row.setdefault("ingested_ts", now)
                row.setdefault("last_updated_at", now)
                rows.append(row)

            player_rows = [r for r in rows if r.get("player_name")]
            team_rows = [r for r in rows if not r.get("player_name")]

            base_insert = """
            INSERT INTO props_live (
                sport, league, game_id, game_start_time, player_id, player_name, 
                team, market_key, market_label, line, book, odds_over, odds_under,
                implied_over, implied_under, source_ts, ingested_ts, is_best_over,
                is_best_under, is_soft_book, is_sharp_book, confidence, last_updated_at,
                home_team, away_team
            )
            VALUES (
                :sport, :league, :game_id, :game_start_time, :player_id, :player_name,
                :team, :market_key, :market_label, :line, :book, :odds_over, :odds_under,
                :implied_over, :implied_under, :source_ts, :ingested_ts, :is_best_over,
                :is_best_under, :is_soft_book, :is_sharp_book, :confidence, :last_updated_at,
                :home_team, :away_team
            )
            """

            update_clause = """
            DO UPDATE SET
                league = EXCLUDED.league,
                line = EXCLUDED.line,
                odds_over = EXCLUDED.odds_over,
                odds_under = EXCLUDED.odds_under,
                implied_over = EXCLUDED.implied_over,
                implied_under = EXCLUDED.implied_under,
                is_best_over = EXCLUDED.is_best_over,
                is_best_under = EXCLUDED.is_best_under,
                is_soft_book = EXCLUDED.is_soft_book,
                is_sharp_book = EXCLUDED.is_sharp_book,
                confidence = EXCLUDED.confidence,
                source_ts = EXCLUDED.source_ts,
                ingested_ts = EXCLUDED.ingested_ts,
                last_updated_at = EXCLUDED.last_updated_at,
                home_team = EXCLUDED.home_team,
                away_team = EXCLUDED.away_team;
            """
            
            if player_rows:
                logger.debug(
                    "upsert_props_live: %s player rows (ON CONFLICT player_name IS NOT NULL)",
                    len(player_rows),
                )
                q_player = base_insert + " ON CONFLICT (sport, game_id, player_name, market_key, book) WHERE player_name IS NOT NULL " + update_clause
                await session.execute(text(q_player), player_rows)
            
            if team_rows:
                logger.debug(
                    "upsert_props_live: %s team rows (ON CONFLICT player_name IS NULL)",
                    len(team_rows),
                )
                q_team = base_insert + " ON CONFLICT (sport, game_id, market_key, book) WHERE player_name IS NULL " + update_clause
                await session.execute(text(q_team), team_rows)
                
            await session.commit()
            logger.debug("Persistence: upserted %s props to props_live", len(records))
        except Exception as e:
            await session.rollback()
            logger.error(f"Persistence: props_live upsert failed: {e}", exc_info=True)
            raise e

async def delete_props_for_sport(sport: str):
    """Clears all live props for a given sport to allow a fresh ingest."""
    async with async_session_maker() as session:
        try:
            from sqlalchemy import delete
            stmt = delete(PropLive).where(PropLive.sport == sport)
            await session.execute(stmt)
            await session.commit()
            logger.info(f"Persistence: Cleared props_live for sport={sport}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Persistence: Failed to clear props for {sport}: {e}")

async def insert_props_history(records: List[PropRecord], source: str = 'live_ingest', run_id: Optional[str] = None):
    """Appends records to props_history."""
    if not records: 
        return
    
    now = datetime.now(timezone.utc)
    async with async_session_maker() as session:
        try:
            is_sqlite = "sqlite" in str(engine.url)
            ins_obj = sqlite_insert(PropHistory) if is_sqlite else pg_insert(PropHistory)
            
            # Get valid columns from PropHistory model
            valid_cols = {c.key for c in PropHistory.__table__.columns}
            
            # Filter to only include columns that exist in PropHistory
            history_rows = []
            for r in records:
                row_data = r.dict()
                row_data["snapshot_at"] = now
                row_data["source"] = source
                row_data["run_id"] = run_id
                history_row = {k: v for k, v in row_data.items() if k in valid_cols and k != 'id'}
                history_rows.append(history_row)
            
            # Chunk inserts to avoid asyncpg parameter limit (32767)
            batch_size = 500
            for i in range(0, len(history_rows), batch_size):
                batch = history_rows[i:i + batch_size]
                await session.execute(ins_obj.values(batch))
                
            await session.commit()
            logger.info(f"Persistence: Appended {len(records)} records to props_history in batches.")
        except Exception as e:
            await session.rollback()
            logger.error(f"Persistence: props_history append failed: {e}")

def _sanitize_ev_history_row(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Validate and normalize a row before insert into edges_ev_history.
    Always assigns market_label via derive_market_label at the persistence boundary.
    """
    sport = raw.get("sport")
    game_id = raw.get("game_id")
    market_key = raw.get("market_key")
    book = raw.get("book")
    side = raw.get("side")
    if not sport or not game_id or not market_key or not book or not side:
        return None
    out = dict(raw)
    out["market_label"] = derive_market_label(out)[:512]
    # edges_ev_history.line is NOT NULL in many deployments
    if out.get("line") is None:
        out["line"] = 0.0
    else:
        try:
            out["line"] = float(out["line"])
        except (TypeError, ValueError):
            out["line"] = 0.0
    ep = out.get("edge_pct", raw.get("edge_pct", raw.get("edge_percent")))
    try:
        out["edge_pct"] = float(ep) if ep is not None else 0.0
    except (TypeError, ValueError):
        out["edge_pct"] = 0.0
    try:
        out["odds"] = float(out.get("odds"))
        out["implied_prob"] = float(out.get("implied_prob"))
    except (TypeError, ValueError):
        return None
    if out.get("model_prob") is not None:
        try:
            out["model_prob"] = float(out["model_prob"])
        except (TypeError, ValueError):
            out["model_prob"] = None
    # Postgres bulk insert may omit server_default; many deployments enforce NOT NULL on snapshot_at.
    if out.get("snapshot_at") is None:
        out["snapshot_at"] = datetime.now(timezone.utc)
    return out


async def insert_edges_ev_history(ev_rows: List[Dict]):
    """Standardized append into public.edges_ev_history (app code should use this path only)."""
    if not ev_rows:
        return

    cleaned = []
    skipped = 0
    for r in ev_rows:
        norm = _sanitize_ev_history_row(r)
        if norm:
            cleaned.append(norm)
        else:
            skipped += 1
    if skipped:
        logger.warning("Persistence: edges_ev_history skipped %s invalid rows (DLQ-style log)", skipped)
    if not cleaned:
        return

    async with async_session_maker() as session:
        try:
            is_sqlite = "sqlite" in str(engine.url)
            ins_obj = sqlite_insert(EdgeEVHistory) if is_sqlite else pg_insert(EdgeEVHistory)

            batch_size = 500
            for i in range(0, len(cleaned), batch_size):
                batch = cleaned[i : i + batch_size]
                await session.execute(ins_obj.values(batch))

            await session.commit()
            logger.info(
                "Persistence: Inserted %s edges into edges_ev_history (%s skipped).",
                len(cleaned),
                skipped,
            )
        except Exception as e:
            await session.rollback()
            logger.error(f"Persistence: edges_ev_history insert failed: {e}")

async def insert_whale_moves(moves: List[Dict]):
    if not moves:
        return
    is_sqlite = "sqlite" in str(engine.url)
    async with async_session_maker() as session:
        try:
            ins_obj = sqlite_insert(WhaleMove) if is_sqlite else pg_insert(WhaleMove)
            await session.execute(ins_obj.values(moves))
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Persistence: whale_moves insert failed: {e}")
            return

    if is_sqlite:
        return
    async with async_session_maker() as session:
        try:
            for m in moves:
                po = m.get("price_after")
                try:
                    odds_i = int(round(float(po))) if po is not None else None
                except (TypeError, ValueError):
                    odds_i = None
                try:
                    await session.execute(
                        text(
                            """
                            INSERT INTO whale_signals (
                              event_id, sport, player, market, line, bookmaker, odds,
                              trust_level, signal_type, is_sharp_money, detected_at
                            ) VALUES (
                              :event_id, :sport, :player, :market, :line, :bookmaker, :odds,
                              :trust_level, :signal_type, :is_sharp_money, NOW()
                            )
                            """
                        ),
                        {
                            "event_id": m.get("event_id"),
                            "sport": m.get("sport"),
                            "player": (m.get("player_name") or m.get("selection") or "")[:100],
                            "market": (m.get("market_key") or "")[:50],
                            "line": m.get("line_after"),
                            "bookmaker": (m.get("bookmaker") or "")[:50],
                            "odds": odds_i,
                            "trust_level": m.get("whale_rating"),
                            "signal_type": (m.get("move_size") or m.get("move_type") or "whale")[
                                :50
                            ],
                            "is_sharp_money": False,
                        },
                    )
                except Exception as sig_err:
                    logger.debug("whale_signals dual-write skipped: %s", sig_err)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.debug("Persistence: whale_signals batch: %s", e)

async def insert_clv_trades(records: List[Dict]):
    """Persists CLV records to clv_trades table."""
    if not records: return
    async with async_session_maker() as session:
        try:
            is_sqlite = "sqlite" in str(engine.url)
            ins_obj = sqlite_insert(CLVRecord) if is_sqlite else pg_insert(CLVRecord)
            await session.execute(ins_obj.values(records))
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Persistence: clv_tracking insert failed: {e}")

async def insert_injury_events(events: List[Dict]):
    if not events: return
    async with async_session_maker() as session:
        try:
            is_sqlite = "sqlite" in str(engine.url)
            ins_obj = sqlite_insert(InjuryImpactEvent) if is_sqlite else pg_insert(InjuryImpactEvent)
            await session.execute(ins_obj.values(events))
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Persistence: injury_impact_events insert failed: {e}")

async def upsert_injuries(sport: str, rows: List[Dict]):
    if not rows: return
    async with async_session_maker() as session:
        try:
            from models.injury import Injury
            from sqlalchemy import delete
            # Full refresh for the sport to ensure we don't have stale injury records
            await session.execute(delete(Injury).where(Injury.sport == sport))
            
            is_sqlite = "sqlite" in str(engine.url)
            ins_obj = sqlite_insert(Injury) if is_sqlite else pg_insert(Injury)
            await session.execute(ins_obj.values(rows))
            await session.commit()
            logger.info(f"Persistence: Refreshed {len(rows)} injuries for {sport}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Persistence: Injury upsert failed: {e}")
