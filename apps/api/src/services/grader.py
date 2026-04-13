import logging
from db.session import async_session_maker
from sqlalchemy import text

logger = logging.getLogger(__name__)

async def grade_props_live(session):
    """
    For every row in props_live, compute:
    - implied_probability from odds
    - ev_percentage = model_prob - implied_prob  
    - confidence score
    - steam_signal (price moved > threshold across books)
    - sharp_conflict (sharp books disagree with soft books)
    - whale_signal (large line move with high confidence)
    """
    logger.info("📡 [Grader] Running grade_props_live SQL update...")
    query = """
        UPDATE props_live SET
            ev_percentage = CASE 
                WHEN implied_over IS NOT NULL AND implied_over > 0 
                THEN ROUND((CAST(1 AS NUMERIC) / implied_over - implied_over) * 100, 2)
                ELSE 0 
            END,
            confidence = CASE
                WHEN is_sharp_book = true THEN 0.85
                WHEN is_best_over = true AND is_best_under = true THEN 0.70
                WHEN is_best_over = true OR is_best_under = true THEN 0.55
                ELSE 0.40
            END,
            steam_signal = CASE WHEN ABS(odds_over) > 150 AND is_sharp_book = true THEN true ELSE false END,
            whale_signal = CASE WHEN is_sharp_book = true AND is_best_over = true THEN true ELSE false END,
            sharp_conflict = CASE WHEN is_sharp_book = true AND is_soft_book = false THEN true ELSE false END
        WHERE last_updated_at > NOW() - INTERVAL '24 hours'
    """
    try:
        await session.execute(text(query))
        await session.commit()
        logger.info("📡 [Grader] Successfully graded props_live")
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ [Grader] Failed grade_props_live: {e}")


async def compute_ev_signals(session):
    """
    Insert graded props into ev_signals table for EV+ tab
    """
    logger.info("📡 [Grader] Generating ev_signals from graded props_live...")
    query = """
        INSERT INTO ev_signals (
            sport, event_id, player_name, market_key, outcome_key,
            line, bookmaker, edge_percent, confidence, created_at, engine_version
        )
        SELECT 
            sport, game_id, COALESCE(player_name, home_team), market_key, 'over',
            line, book, ev_percentage, confidence, NOW(), 'v2'
        FROM props_live
        WHERE ev_percentage != 0
          AND last_updated_at > NOW() - INTERVAL '24 hours'
        ON CONFLICT (sport, event_id, player_name, market_key, outcome_key, bookmaker, engine_version) WHERE player_name IS NOT NULL DO NOTHING
    """
    query_team = """
        INSERT INTO ev_signals (
            sport, event_id, market_key, outcome_key,
            line, bookmaker, edge_percent, confidence, created_at, engine_version
        )
        SELECT 
            sport, game_id, market_key, 'over',
            line, book, ev_percentage, confidence, NOW(), 'v2'
        FROM props_live
        WHERE ev_percentage != 0
          AND player_name IS NULL
          AND last_updated_at > NOW() - INTERVAL '24 hours'
        ON CONFLICT (sport, event_id, market_key, outcome_key, bookmaker, engine_version) WHERE player_name IS NULL DO NOTHING
    """
    try:
        await session.execute(text(query))
        await session.commit()
        
        await session.execute(text(query_team))
        await session.commit()
        
        logger.info("📡 [Grader] Successfully generated ev_signals")
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ [Grader] Failed compute_ev_signals: {e}")

async def run_full_grading_pipeline():
    """Runs the full post-ingest SQL EV and grading pipeline."""
    async with async_session_maker() as session:
        await grade_props_live(session)
        await compute_ev_signals(session)
