"""FIX #17: connections in finally blocks. FIX #18: pool replaces per-request connect."""
import os, asyncpg, logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)
_pool: Optional[asyncpg.Pool] = None

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            # Fallback for local dev if DATABASE_URL is missing
            db_url = "postgresql://postgres:postgres@localhost:5432/perplex"
            
        # Handle sqlite URLs by converting or warning (simplified for Postgres integration)
        if db_url.startswith("sqlite"):
            logger.warning("asyncpg pool does not support SQLite. Database features may be limited.")
            return None

        try:
            _pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
        except Exception as e:
            logger.error(f"Failed to create asyncpg pool: {e}")
            raise
    return _pool

class PicksService:
    async def get_picks(self, sport_id: int, hours: int = 24, limit: int = 50) -> List[Dict]:
        pool = await get_pool()
        if not pool:
            return []
            
        async with pool.acquire() as conn:  # FIX #17/#18: pool + context manager
            try:
                rows = await conn.fetch(
                    """
                    SELECT id, sport_id, game_id, player_id, market_id,
                           side, line_value, odds, model_probability,
                           implied_probability, expected_value, confidence_score,
                           generated_at,
                           COALESCE(closing_odds,0)           AS closing_odds,
                           COALESCE(clv_percentage,0)         AS clv_percentage,
                           COALESCE(roi_percentage,0)         AS roi_percentage,
                           COALESCE(opening_odds,0)           AS opening_odds,
                           COALESCE(line_movement,0)          AS line_movement,
                           COALESCE(sharp_money_indicator,0)  AS sharp_money_indicator,
                           COALESCE(best_book_odds,0)         AS best_book_odds,
                           COALESCE(best_book_name,'')        AS best_book_name,
                           COALESCE(ev_improvement,0)         AS ev_improvement
                    FROM modelpicks
                    WHERE sport_id=$1 AND expected_value>0 AND confidence_score>0.5
                      AND generated_at > NOW() - INTERVAL '1 hour' * $2
                    ORDER BY expected_value DESC LIMIT $3
                    """,
                    sport_id, hours, limit,
                )
                return [dict(r) for r in rows]
            except asyncpg.UndefinedColumnError:
                # Graceful fallback if CLV migration hasn't run yet
                logger.warning("CLV columns not found — running base query")
                try:
                    rows = await conn.fetch(
                        "SELECT * FROM modelpicks WHERE sport_id=$1 AND expected_value>0"
                        " ORDER BY expected_value DESC LIMIT $2",
                        sport_id, limit,
                    )
                    return [dict(r) for r in rows]
                except Exception as inner_e:
                    logger.error(f"Fallback query failed: {inner_e}")
                    return []
            except Exception as e:
                logger.error(f"picks_service error: {e}")
                return []

picks_service = PicksService()
