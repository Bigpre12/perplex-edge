import logging
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from db.session import AsyncSessionLocal
from models import UnifiedEVSignal, EdgeEVHistory

logger = logging.getLogger(__name__)

async def insert_edges_ev_history(edges: list[dict]) -> None:
    """
    Persists EV signals detected during ingestion to the live signals table 
    and the historical archive.
    """
    if not edges:
        return
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # 1. Upsert Live Signals (UnifiedEVSignal)
                for edge in edges:
                    # Map keys for UnifiedEVSignal schema
                    live_row = {
                        "sport": edge.get("sport"),
                        "event_id": edge.get("game_id"),
                        "market_key": edge.get("market_key"),
                        "outcome_key": edge.get("side"),
                        "player_name": edge.get("player_name"),
                        "bookmaker": edge.get("book"),
                        "price": float(edge.get("odds", 0)),
                        "line": float(edge.get("line")) if edge.get("line") is not None else None,
                        "true_prob": float(edge.get("model_prob", 0)),
                        "edge_percent": float(edge.get("edge_pct", 0)),
                        "implied_prob": float(edge.get("implied_prob", 0)),
                        "engine_version": "v1-scout"
                    }
                    
                    stmt = insert(UnifiedEVSignal).values(live_row).on_conflict_do_update(
                        index_elements=["sport", "event_id", "market_key", "outcome_key", "bookmaker", "engine_version"],
                        set_={
                            "price": live_row["price"],
                            "line": live_row["line"],
                            "true_prob": live_row["true_prob"],
                            "edge_percent": live_row["edge_percent"],
                            "implied_prob": live_row["implied_prob"],
                            "updated_at": func.now()
                        }
                    )
                    await session.execute(stmt)

                # 2. Add Historical Records (EdgeEVHistory)
                history_rows = []
                for edge in edges:
                    h_row = {
                        "sport": edge.get("sport"),
                        "league": edge.get("league"),
                        "game_id": edge.get("game_id"),
                        "game_start_time": edge.get("game_start_time"),
                        "player_id": edge.get("player_id"),
                        "player_name": edge.get("player_name"),
                        "team": edge.get("team"),
                        "market_key": edge.get("market_key"),
                        "market_label": edge.get("market_label"),
                        "line": edge.get("line"),
                        "book": edge.get("book"),
                        "side": edge.get("side"),
                        "odds": edge.get("odds"),
                        "model_prob": edge.get("model_prob"),
                        "implied_prob": edge.get("implied_prob"),
                        "edge_pct": edge.get("edge_pct"),
                        "snapshot_at": func.now(),
                        "source": "brain_scout_v1"
                    }
                    history_rows.append(h_row)
                
                if history_rows:
                    await session.execute(insert(EdgeEVHistory).values(history_rows))

        logger.info(f"ev_persistence: upserted {len(edges)} signals and history records")
    except Exception as e:
        logger.error(f"ev_persistence insert error: {e}")
