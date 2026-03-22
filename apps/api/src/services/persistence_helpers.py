# apps/api/src/services/persistence_helpers.py
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from db.session import async_session_maker, engine
from models import PropLive, PropHistory, EdgeEVHistory
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

            query = """
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
            ON CONFLICT (sport, game_id, player_name, market_key, book)
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
            
            await session.execute(text(query), rows)
            await session.commit()
            logger.info(f"Persistence: Successfully upserted {len(records)} props to props_live using raw SQL")
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
            
            rows = []
            for r in records:
                row = r.dict(exclude_none=True)
                row.pop("last_updated_at", None)
                row["snapshot_at"] = now
                row["source"] = source
                row["run_id"] = run_id
                rows.append(row)
                
            await session.execute(ins_obj.values(rows))
            await session.commit()
            logger.info(f"Persistence: Appended {len(records)} records to props_history.")
        except Exception as e:
            await session.rollback()
            logger.error(f"Persistence: props_history append failed: {e}")

async def insert_edges_ev_history(ev_rows: List[Dict]):
    """Standardized append into public.edges_ev_history."""
    if not ev_rows: return
    
    async with async_session_maker() as session:
        try:
            is_sqlite = "sqlite" in str(engine.url)
            ins_obj = sqlite_insert(EdgeEVHistory) if is_sqlite else pg_insert(EdgeEVHistory)
            await session.execute(ins_obj.values(ev_rows))
            await session.commit()
            logger.info(f"Persistence: Inserted {len(ev_rows)} edges into edges_ev_history.")
        except Exception as e:
            await session.rollback()
            logger.error(f"Persistence: edges_ev_history insert failed: {e}")

async def insert_whale_moves(moves: List[Dict]):
    if not moves: return
    async with async_session_maker() as session:
        try:
            is_sqlite = "sqlite" in str(engine.url)
            ins_obj = sqlite_insert(WhaleMove) if is_sqlite else pg_insert(WhaleMove)
            await session.execute(ins_obj.values(moves))
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Persistence: whale_moves insert failed: {e}")

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
