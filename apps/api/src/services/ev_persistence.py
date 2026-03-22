import logging
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from db.session import AsyncSessionLocal
from models.brain import UnifiedEVSignal

logger = logging.getLogger(__name__)

async def insert_edges_ev_history(edges: list[dict]) -> None:
    """
    Persists EV signals to the UnifiedEVSignal table.
    Ensures data keys match the schema and handles conflict resolution.
    """
    if not edges:
        return
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                for edge in edges:
                    # Map incoming scout/engine keys to UnifiedEVSignal column names
                    row = {
                        "sport": edge.get("sport"),
                        "event_id": edge.get("game_id") or edge.get("event_id"),
                        "market_key": edge.get("market_key"),
                        "outcome_key": edge.get("side") or edge.get("outcome_key"),
                        "player_name": edge.get("player_name"),
                        "bookmaker": edge.get("book") or edge.get("bookmaker"),
                        "price": float(edge.get("odds", 0)) if edge.get("odds") is not None else float(edge.get("price", 0)),
                        "line": float(edge.get("line")) if edge.get("line") is not None else None,
                        "true_prob": float(edge.get("model_prob", 0)) if edge.get("model_prob") is not None else float(edge.get("true_prob", 0)),
                        "edge_percent": float(edge.get("edge_pct", 0)) if edge.get("edge_pct") is not None else float(edge.get("edge_percent", 0)),
                        "implied_prob": float(edge.get("implied_prob", 0)),
                        "engine_version": edge.get("engine_version", "v1-scout")
                    }
                    
                    stmt = insert(UnifiedEVSignal).values(row).on_conflict_do_update(
                        index_elements=["sport", "event_id", "market_key", "outcome_key", "bookmaker", "engine_version"],
                        set_={
                            "price": row["price"],
                            "line": row["line"],
                            "true_prob": row["true_prob"],
                            "edge_percent": row["edge_percent"],
                            "implied_prob": row["implied_prob"],
                            "updated_at": func.now()
                        }
                    )
                    await session.execute(stmt)
        logger.info(f"ev_persistence: upserted {len(edges)} EV edges")
    except Exception as e:
        logger.error(f"ev_persistence insert error: {e}")
