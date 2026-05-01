# services/unified_odds_persistence.py
from datetime import datetime, timezone
from typing import List, Dict, Any
import logging
import os
from services.db import db

logger = logging.getLogger(__name__)
UNIFIED_ODDS_DIAGNOSTICS = os.getenv("UNIFIED_ODDS_DIAGNOSTICS", "false").strip().lower() == "true"

async def upsert_unified_odds(rows: List[Dict[str, Any]]) -> None:
    """
    Upsert odds into the unified_odds table.
    This table feeds the SharpMoneyBrain and CLV tracker.
    """
    if not rows:
        return

    now = datetime.now(timezone.utc)
    for r in rows:
        r.setdefault("created_at", now)

    # Detection for SQLite vs Postgres
    is_sqlite = "sqlite" in str(db.engine.url) if hasattr(db, "engine") else True 
    # Actually DBWrapper uses engine from db.session
    from db.session import engine as db_engine
    is_sqlite = "sqlite" in str(db_engine.url)

    table_name = "unified_odds" # Remove 'public.' for SQLite compatibility
    
    base_insert = f"""
    INSERT INTO {table_name} (
      sport, event_id, market_key, outcome_key, bookmaker,
      line, price, implied_prob, player_name,
      league, game_time, home_team, away_team, created_at
    )
    VALUES (
      :sport, :event_id, :market_key, :outcome_key, :bookmaker,
      :line, :price, :implied_prob, :player_name,
      :league, :game_time, :home_team, :away_team, :created_at
    )
    """

    update_clause = """
    DO UPDATE SET
      line = EXCLUDED.line,
      price = EXCLUDED.price,
      implied_prob = EXCLUDED.implied_prob,
      league = EXCLUDED.league,
      game_time = EXCLUDED.game_time,
      home_team = EXCLUDED.home_team,
      away_team = EXCLUDED.away_team,
      created_at = EXCLUDED.created_at;
    """

    player_rows = [r for r in rows if r.get("player_name")]
    team_rows = [r for r in rows if not r.get("player_name")]

    try:
        if player_rows:
            if UNIFIED_ODDS_DIAGNOSTICS:
                logger.debug(
                    "[DIAGNOSTIC] upsert_unified_odds player_rows=%s conflict_key=(sport,event_id,player_name,market_key,outcome_key,bookmaker) where player_name is not null",
                    len(player_rows),
                )
            q_player = base_insert + " ON CONFLICT (sport, event_id, player_name, market_key, outcome_key, bookmaker) WHERE player_name IS NOT NULL " + update_clause
            await db.executemany(q_player, player_rows)
            
        if team_rows:
            if UNIFIED_ODDS_DIAGNOSTICS:
                logger.debug(
                    "[DIAGNOSTIC] upsert_unified_odds team_rows=%s conflict_key=(sport,event_id,market_key,outcome_key,bookmaker) where player_name is null",
                    len(team_rows),
                )
            q_team = base_insert + " ON CONFLICT (sport, event_id, market_key, outcome_key, bookmaker) WHERE player_name IS NULL " + update_clause
            await db.executemany(q_team, team_rows)
        if UNIFIED_ODDS_DIAGNOSTICS:
            logger.debug(
                "[DIAGNOSTIC] upsert_unified_odds summary total=%s player=%s team=%s",
                len(rows),
                len(player_rows),
                len(team_rows),
            )
    except Exception as e:
        error_msg = f"UnifiedOdds: Upsert failed with ON CONFLICT, attempting DELETE+INSERT fallback: {e}"
        logger.warning(error_msg)
        try:
            delete_sql_player = f"DELETE FROM {table_name} WHERE sport = :sport AND event_id = :event_id AND player_name = :player_name AND market_key = :market_key AND outcome_key = :outcome_key AND bookmaker = :bookmaker"
            delete_sql_team = f"DELETE FROM {table_name} WHERE sport = :sport AND event_id = :event_id AND player_name IS NULL AND market_key = :market_key AND outcome_key = :outcome_key AND bookmaker = :bookmaker"
            
            if player_rows:
                await db.executemany(delete_sql_player, player_rows)
                await db.executemany(base_insert, player_rows)
            if team_rows:
                await db.executemany(delete_sql_team, team_rows)
                await db.executemany(base_insert, team_rows)
            logger.info(f"UnifiedOdds: Successfully used DELETE+INSERT fallback for {len(rows)} rows")
        except Exception as fallback_e:
            logger.error(f"UnifiedOdds: Fallback DELETE+INSERT also failed: {fallback_e}")
            if rows:
                logger.debug(f"Sample row causing failure: {rows[0]}")
