import logging
from sqlalchemy.dialects.postgresql import insert
from db.session import AsyncSessionLocal
from models.ev_signals import EvSignal

logger = logging.getLogger(__name__)

async def insert_edges_ev_history(edges: list[dict]) -> None:
    if not edges:
        return
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                for edge in edges:
                    stmt = insert(EvSignal).values(**edge).on_conflict_do_update(
                        index_elements=["player_name", "stat_type", "sportsbook", "sport"],
                        set_={
                            "edge_percent": edge.get("edge_percent"),
                            "true_prob": edge.get("true_prob"),
                            "sport": edge.get("sport"),
                        }
                    )
                    await session.execute(stmt)
        logger.info(f"ev_persistence: upserted {len(edges)} EV edges")
    except Exception as e:
        logger.error(f"ev_persistence insert error: {e}")
