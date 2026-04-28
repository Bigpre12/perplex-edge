import logging
from db.session import async_session_maker
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError, DBAPIError

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
                WHEN ev_percentage >= 10 THEN 0.95
                WHEN ev_percentage >= 7 THEN 0.90
                WHEN ev_percentage >= 5 THEN 0.85
                WHEN ev_percentage >= 3 THEN 0.80
                WHEN ev_percentage >= 1 THEN 0.75
                ELSE 0.60
            END,
            steam_signal = CASE WHEN ABS(odds_over) > 150 AND is_sharp_book = true THEN true ELSE false END,
            whale_signal = CASE WHEN is_sharp_book = true AND is_best_over = true THEN true ELSE false END,
            sharp_conflict = CASE WHEN is_sharp_book = true AND is_soft_book = false THEN true ELSE false END
        WHERE 1=1
    """
    try:
        await _execute_with_pgbouncer_retry(session, query, "grade_props_live")
        await session.commit()
        logger.info("📡 [Grader] Successfully graded props_live")
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ [Grader] Failed grade_props_live: {e}")


async def _execute_with_pgbouncer_retry(session, sql: str, op_name: str):
    """Retry once when PgBouncer invalidates asyncpg prepared statement handles."""
    try:
        return await session.execute(text(sql))
    except DBAPIError as e:
        msg = str(e)
        if "InvalidSQLStatementNameError" in msg:
            await session.rollback()
            logger.warning(
                "Grader DBAPI retry (%s): invalid prepared statement handle detected; retrying once.",
                op_name,
            )
            return await session.execute(text(sql))
        raise


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
        await _execute_with_pgbouncer_retry(session, query, "compute_ev_signals_player")
        await session.commit()
    except ProgrammingError as e:
        await session.rollback()
        logger.warning("Grader ON CONFLICT path unavailable; using NOT EXISTS fallback: %s", e)
        await session.execute(text(fallback_query))
        await session.commit()

    try:
        await _execute_with_pgbouncer_retry(session, query_team, "compute_ev_signals_team")
        await session.commit()
    except ProgrammingError as e:
        await session.rollback()
        logger.warning("Grader team ON CONFLICT path unavailable; using NOT EXISTS fallback: %s", e)
        await session.execute(text(fallback_query_team))
        await session.commit()

    logger.info("📡 [Grader] Successfully generated ev_signals")

async def grade_model_picks_from_scores(session):
    """
    Grades ModelPicks for game totals/results using live_scores table.
    This handles non-player-prop picks (where player_name is NULL).
    """
    logger.info("📡 [Grader] Joining live_scores to model_picks for game-level settlement...")
    
    # 1. Grade Game Totals (stat_type = 'totals')
    query_totals = """
        UPDATE model_picks mp
        SET 
            actual_value = (ls.home_score + ls.away_score),
            won = CASE 
                WHEN mp.side = 'over' THEN (ls.home_score + ls.away_score) > mp.line
                WHEN mp.side = 'under' THEN (ls.home_score + ls.away_score) < mp.line
                ELSE NULL
            END,
            profit_loss = CASE
                WHEN (mp.side = 'over' AND (ls.home_score + ls.away_score) > mp.line) OR 
                     (mp.side = 'under' AND (ls.home_score + ls.away_score) < mp.line) THEN
                    CASE WHEN mp.odds < 0 THEN 100.0 / ABS(mp.odds) ELSE mp.odds / 100.0 END
                WHEN (mp.side = 'over' AND (ls.home_score + ls.away_score) < mp.line) OR 
                     (mp.side = 'under' AND (ls.home_score + ls.away_score) > mp.line) THEN -1.0
                ELSE 0.0
            END,
            status = 'settled',
            updated_at = NOW()
        FROM live_scores ls
        WHERE mp.game_id = ls.event_id
          AND ls.status IN ('STATUS_FINAL', 'COMPLETED', 'Final')
          AND mp.status = 'active'
          AND mp.player_name IS NULL
          AND mp.stat_type = 'totals'
          AND ls.home_score IS NOT NULL AND ls.away_score IS NOT NULL
    """

    # 2. Grade Moneylines (stat_type = 'h2h')
    # Note: side for h2h is usually the team name or 'home'/'away'
    query_h2h = """
        UPDATE model_picks mp
        SET 
            actual_value = CASE WHEN ls.home_score > ls.away_score THEN 1 ELSE 0 END, -- 1 for home win
            won = CASE 
                WHEN (mp.side = ls.home_team OR mp.side = 'home') THEN ls.home_score > ls.away_score
                WHEN (mp.side = ls.away_team OR mp.side = 'away') THEN ls.away_score > ls.home_score
                ELSE NULL
            END,
            profit_loss = CASE
                WHEN ((mp.side = ls.home_team OR mp.side = 'home') AND ls.home_score > ls.away_score) OR 
                     ((mp.side = ls.away_team OR mp.side = 'away') AND ls.away_score > ls.home_score) THEN
                    CASE WHEN mp.odds < 0 THEN 100.0 / ABS(mp.odds) ELSE mp.odds / 100.0 END
                WHEN ((mp.side = ls.home_team OR mp.side = 'home') AND ls.home_score < ls.away_score) OR 
                     ((mp.side = ls.away_team OR mp.side = 'away') AND ls.away_score < ls.home_score) THEN -1.0
                ELSE 0.0
            END,
            status = 'settled',
            updated_at = NOW()
        FROM live_scores ls
        WHERE mp.game_id = ls.event_id
          AND ls.status IN ('STATUS_FINAL', 'COMPLETED', 'Final')
          AND mp.status = 'active'
          AND mp.player_name IS NULL
          AND mp.stat_type = 'h2h'
          AND ls.home_score IS NOT NULL AND ls.away_score IS NOT NULL
    """

    # 3. Grade Spreads (stat_type = 'spreads')
    query_spreads = """
        UPDATE model_picks mp
        SET 
            actual_value = (ls.home_score - ls.away_score),
            won = CASE 
                WHEN (mp.side = ls.home_team OR mp.side = 'home') THEN (ls.home_score + mp.line) > ls.away_score
                WHEN (mp.side = ls.away_team OR mp.side = 'away') THEN (ls.away_score + mp.line) > ls.home_score
                ELSE NULL
            END,
            profit_loss = CASE
                WHEN ((mp.side = ls.home_team OR mp.side = 'home') AND (ls.home_score + mp.line) > ls.away_score) OR 
                     ((mp.side = ls.away_team OR mp.side = 'away') AND (ls.away_score + mp.line) > ls.home_score) THEN
                    CASE WHEN mp.odds < 0 THEN 100.0 / ABS(mp.odds) ELSE mp.odds / 100.0 END
                WHEN ((mp.side = ls.home_team OR mp.side = 'home') AND (ls.home_score + mp.line) < ls.away_score) OR 
                     ((mp.side = ls.away_team OR mp.side = 'away') AND (ls.away_score + mp.line) < ls.home_score) THEN -1.0
                ELSE 0.0
            END,
            status = 'settled',
            updated_at = NOW()
        FROM live_scores ls
        WHERE mp.game_id = ls.event_id
          AND ls.status IN ('STATUS_FINAL', 'COMPLETED', 'Final')
          AND mp.status = 'active'
          AND mp.player_name IS NULL
          AND mp.stat_type = 'spreads'
          AND ls.home_score IS NOT NULL AND ls.away_score IS NOT NULL
    """

    try:
        await _execute_with_pgbouncer_retry(session, query_totals, "grade_model_picks_totals")
        await _execute_with_pgbouncer_retry(session, query_h2h, "grade_model_picks_h2h")
        await _execute_with_pgbouncer_retry(session, query_spreads, "grade_model_picks_spreads")
        await session.commit()
        logger.info("📡 [Grader] Successfully graded game-level picks from scores")
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ [Grader] Failed grade_model_picks_from_scores: {e}")

async def run_full_grading_pipeline():
    """Runs the full post-ingest SQL EV and grading pipeline."""
    async with async_session_maker() as session:
        await grade_props_live(session)
        await compute_ev_signals(session)
        await grade_model_picks_from_scores(session)
