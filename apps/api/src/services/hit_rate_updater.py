# apps/api/src/services/hit_rate_updater.py
import logging
from sqlalchemy import text
from db.session import async_session_maker

logger = logging.getLogger(__name__)

async def recompute_all_hit_rates():
    """
    Aggregate all graded rows from staging and upsert into player_mc_hit_rates.
    This provides empirical priors for the Monte Carlo engine.
    """
    async with async_session_maker() as session:
        # 1. Aggregate hit rates per player/stat_type
        # We calculate the average of the 'hit' boolean column (Postgres treats bool as 1/0 in some contexts,
        # but here we use a CASE statement for clarity and cross-DB safety).
        agg_sql = text("""
            SELECT 
                player_name, 
                stat_type, 
                CAST(SUM(CASE WHEN hit = TRUE THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(*), 0) as hit_rate,
                COUNT(*) as sample_size
            FROM pp_projections_staging
            WHERE graded = TRUE
            GROUP BY player_name, stat_type
            HAVING COUNT(*) > 0
        """)
        
        try:
            result = await session.execute(agg_sql)
            aggregates = result.fetchall()
        except Exception as e:
            logger.error(f"Hit Rate Updater: Aggregation query failed: {e}")
            return
        
        if not aggregates:
            logger.info("Hit Rate Updater: No graded data found to aggregate.")
            return

        # 2. Upsert into player_mc_hit_rates
        # ON CONFLICT handles the case where we already have data for this player/stat.
        upsert_sql = text("""
            INSERT INTO player_mc_hit_rates (player_name, stat_type, hit_rate, sample_size, last_updated)
            VALUES (:player_name, :stat_type, :hit_rate, :sample_size, CURRENT_TIMESTAMP)
            ON CONFLICT (player_name, stat_type) DO UPDATE SET
                hit_rate = EXCLUDED.hit_rate,
                sample_size = EXCLUDED.sample_size,
                last_updated = CURRENT_TIMESTAMP
        """)
        
        count = 0
        for agg in aggregates:
            try:
                await session.execute(upsert_sql, {
                    "player_name": agg.player_name,
                    "stat_type": agg.stat_type,
                    "hit_rate": agg.hit_rate,
                    "sample_size": agg.sample_size
                })
                count += 1
            except Exception as e:
                logger.error(f"Hit Rate Updater: Error updating hit rate for {agg.player_name}: {e}")
                
        await session.commit()
        logger.info(f"Hit Rate Updater: Successfully updated {count} player empirical hit rates.")

async def run_hit_rate_update():
    """Entry point for the hit rate update task."""
    logger.info("Hit Rate Updater: Starting update cycle...")
    await recompute_all_hit_rates()
