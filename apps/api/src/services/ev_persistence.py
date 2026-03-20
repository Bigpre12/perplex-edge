# services/ev_persistence.py
from datetime import datetime, timezone
from typing import List, Dict, Any
from services.db import db

async def insert_edges_ev_history(ev_rows: List[Dict[str, Any]]) -> None:
    if not ev_rows:
        return
    now = datetime.now(timezone.utc)
    for r in ev_rows:
        r.setdefault("snapshot_at", now)
        r.setdefault("source", "brain_ev")
        r.setdefault("run_id", None)

    query = """
    insert into public.edges_ev_history (
      sport, league, game_id, game_start_time,
      player_id, player_name, team,
      market_key, market_label, line,
      book, side, odds,
      model_prob, implied_prob, edge_pct,
      snapshot_at, source, run_id
    )
    values (
      :sport, :league, :game_id, :game_start_time,
      :player_id, :player_name, :team,
      :market_key, :market_label, :line,
      :book, :side, :odds,
      :model_prob, :implied_prob, :edge_pct,
      :snapshot_at, :source, :run_id
    );
    """
    await db.executemany(query, ev_rows)
