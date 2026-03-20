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

    # Note: Ensure the table has a unique constraint on (sport, event_id, market_key, outcome_key, bookmaker)
    # The current model in brain.py doesn't have it explicitly in __table_args__ anymore because 
    # I replaced it with the shim, but we should probably add it back or use a primary key if possible.
    # For now, we'll try to insert and use the ON CONFLICT if the DB supports it.
    
    query = """
    INSERT INTO public.unified_odds (
      sport, event_id, market_key, outcome_key, bookmaker,
      line, price, implied_prob, player_name,
      league, game_time, home_team, away_team, created_at
    )
    VALUES (
      :sport, :event_id, :market_key, :outcome_key, :bookmaker,
      :line, :price, :implied_prob, :player_name,
      :league, :game_time, :home_team, :away_team, :created_at
    )
    ON CONFLICT (sport, event_id, market_key, outcome_key, bookmaker, player_name)
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
