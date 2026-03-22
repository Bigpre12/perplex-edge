# services/unified_odds_persistence.py
from datetime import datetime, timezone
from typing import List, Dict, Any
from services.db import db

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
    
    query = f"""
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
    ON CONFLICT (sport, event_id, market_key, outcome_key, bookmaker)
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
    try:
        await db.executemany(query, rows)
    except Exception as e:
        # If the unique constraint is missing, we might need to handle it differently or just log.
        import logging
        logging.getLogger(__name__).error(f"UnifiedOdds: Upsert failed: {e}")
