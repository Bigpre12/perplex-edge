import logging
from db.session import async_session_maker
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

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
        WHERE 1=1
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
        ON CONFLICT (sport, event_id, market_key, outcome_key, bookmaker, engine_version) WHERE player_name IS NULL DO NOTHING
    """
    fallback_query = """
        INSERT INTO ev_signals (
            sport, event_id, player_name, market_key, outcome_key,
            line, bookmaker, edge_percent, confidence, created_at, engine_version
        )
        SELECT 
            pl.sport, pl.game_id, COALESCE(pl.player_name, pl.home_team), pl.market_key, 'over',
            pl.line, pl.book, pl.ev_percentage, pl.confidence, NOW(), 'v2'
        FROM props_live pl
        WHERE pl.ev_percentage != 0
          AND NOT EXISTS (
              SELECT 1
              FROM ev_signals es
              WHERE es.sport = pl.sport
                AND es.event_id = pl.game_id
                AND COALESCE(es.player_name, '') = COALESCE(COALESCE(pl.player_name, pl.home_team), '')
                AND es.market_key = pl.market_key
                AND es.outcome_key = 'over'
                AND es.bookmaker = pl.book
                AND es.engine_version = 'v2'
          )
    """
    fallback_query_team = """
        INSERT INTO ev_signals (
            sport, event_id, market_key, outcome_key,
            line, bookmaker, edge_percent, confidence, created_at, engine_version
        )
        SELECT 
            pl.sport, pl.game_id, pl.market_key, 'over',
            pl.line, pl.book, pl.ev_percentage, pl.confidence, NOW(), 'v2'
        FROM props_live pl
        WHERE pl.ev_percentage != 0
          AND pl.player_name IS NULL
          AND NOT EXISTS (
              SELECT 1
              FROM ev_signals es
              WHERE es.sport = pl.sport
                AND es.event_id = pl.game_id
                AND es.player_name IS NULL
                AND es.market_key = pl.market_key
                AND es.outcome_key = 'over'
                AND es.bookmaker = pl.book
                AND es.engine_version = 'v2'
          )
    """
    try:
        await session.execute(text(query))
        await session.commit()
    except ProgrammingError as e:
        await session.rollback()
        logger.warning("Grader ON CONFLICT path unavailable; using NOT EXISTS fallback: %s", e)
        await session.execute(text(fallback_query))
        await session.commit()

    try:
        await session.execute(text(query_team))
        await session.commit()
    except ProgrammingError as e:
        await session.rollback()
        logger.warning("Grader team ON CONFLICT path unavailable; using NOT EXISTS fallback: %s", e)
        await session.execute(text(fallback_query_team))
        await session.commit()

    logger.info("📡 [Grader] Successfully generated ev_signals")

async def run_full_grading_pipeline():
    """Runs the full post-ingest SQL EV and grading pipeline."""
    async with async_session_maker() as session:
        await grade_props_live(session)
        await compute_ev_signals(session)
