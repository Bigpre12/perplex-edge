# apps/api/src/services/persistence_helpers.py
import logging
from typing import List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from db.session import async_session_maker, engine
from models.unified import PropLive, PropHistory, EdgeEVHistory
from models.brain import WhaleMove, CLVRecord, InjuryImpactEvent
from schemas.props import PropRecord

logger = logging.getLogger(__name__)

async def upsert_props_live(records: List[PropRecord]):
    """Standardized upsert into public.props_live."""
    if not records: return
    
    async with async_session_maker() as session:
        try:
            is_sqlite = "sqlite" in str(engine.url)
            ins_obj = sqlite_insert(PropLive) if is_sqlite else pg_insert(PropLive)
            
            rows = [r.dict(exclude_none=True) for r in records]
            stmt = ins_obj.values(rows)
            
            update_cols = {
                "line": ins_obj.excluded.line,
                "odds_over": ins_obj.excluded.odds_over,
                "odds_under": ins_obj.excluded.odds_under,
                "implied_over": ins_obj.excluded.implied_over,
                "implied_under": ins_obj.excluded.implied_under,
                "last_updated_at": ins_obj.excluded.last_updated_at
            }
            
            if is_sqlite:
                stmt = stmt.on_conflict_do_update(
                    index_elements=['sport', 'game_id', 'player_name', 'market_key', 'book'],
                    set_=update_cols
                )
            else:
                stmt = stmt.on_conflict_do_update(
                    constraint='uix_props_live_unique',
                    set_=update_cols
                )
            
            await session.execute(stmt)
            await session.commit()
            logger.info(f"Persistence: Upserted {len(records)} records into props_live.")
        except Exception as e:
            await session.rollback()
            logger.error(f"Persistence: props_live upsert failed: {e}")

async def insert_props_history(records: List[PropRecord], source: str = 'live_ingest', run_id: str = None):
    """Appends records to props_history."""
    if not records: return
    
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
