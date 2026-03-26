import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

logger = logging.getLogger(__name__)

async def run_ev_grader(sport: str, db: Optional[AsyncSession] = None) -> int:
    """Returns count of ev_signals written."""
    if not db:
        from db.session import async_session_maker # type: ignore
        async with async_session_maker() as session:
            return await _run_ev_grader(sport, session)
    else:
        return await _run_ev_grader(sport, db)

async def _run_ev_grader(sport: str, db: AsyncSession) -> int:
    try:
        logger.info(f"📊 [EV WRITER] Running EV calculations for {sport}")
        
        # We find rows in props_live with positive confidence
        # Compute no-vig fair odds from over/under implied probs
        # EV% = (fair_prob x decimal_odds) - 1
        # If EV > 0.02 (2%), write to ev_signals
        
        sql = text("""
            WITH valid_props AS (
                 SELECT 
                     player_name, market_key, sport, book, line, game_id,
                     odds_over, odds_under, implied_over, implied_under, confidence
                 FROM props_live 
                 WHERE sport = :sport
                   AND confidence > 0 
                   AND player_name IS NOT NULL
                   AND implied_over IS NOT NULL 
                   AND implied_under IS NOT NULL
                   AND odds_over IS NOT NULL
                   AND odds_under IS NOT NULL
                   AND implied_over > 0
                   AND implied_under > 0
                   AND (implied_over + implied_under) BETWEEN 0.85 AND 1.15
            ),
            fair_probs AS (
                 SELECT 
                     *,
                     implied_over / (implied_over + implied_under) as fair_over_prob,
                     implied_under / (implied_over + implied_under) as fair_under_prob,
                     -- Convert American odds to Decimal
                     CASE 
                         WHEN odds_over > 0 THEN (odds_over / 100.0) + 1
                         ELSE (100.0 / ABS(odds_over)) + 1 
                     END as dec_over,
                     CASE 
                         WHEN odds_under > 0 THEN (odds_under / 100.0) + 1
                         ELSE (100.0 / ABS(odds_under)) + 1 
                     END as dec_under
                 FROM valid_props
            ),
            calculated_ev AS (
                 SELECT 
                     player_name, market_key, sport, book, line, game_id, confidence,
                     (fair_over_prob * dec_over) - 1 as ev_over,
                     (fair_under_prob * dec_under) - 1 as ev_under,
                     fair_over_prob, fair_under_prob
                 FROM fair_probs
            )
            SELECT * FROM calculated_ev 
            WHERE (ev_over > 0.02 OR ev_under > 0.02)
              AND ev_over < 0.20 AND ev_under < 0.20
        """)
        
        result = await db.execute(sql, {"sport": sport})
        edges = result.mappings().all()
        
        inserted_count = 0
        for edge in edges:
            if edge["ev_over"] > 0.02:
                inserted_count += await _upsert_ev_signal(
                    db, sport, edge, "OVER", edge["ev_over"], edge["fair_over_prob"]
                )
            if edge["ev_under"] > 0.02:
                inserted_count += await _upsert_ev_signal(
                    db, sport, edge, "UNDER", edge["ev_under"], edge["fair_under_prob"]
                )
        
        await db.commit()
        if inserted_count > 0:
            logger.info(f"✅ [EV WRITER] Generated {inserted_count} +EV signals for {sport}")
        return inserted_count
        
    except Exception as e:
        logger.error(f"❌ [EV WRITER] Failed EV generation for {sport}: {str(e)}", exc_info=True)
        await db.rollback()
        return 0

async def _upsert_ev_signal(db: AsyncSession, sport: str, row: dict, rec: str, ev_score: float, fair_prob: float) -> int:
    insert_sql = text("""
        INSERT INTO ev_signals 
            (player_name, market_key, sport, sport_key, event_id, outcome_key, bookmaker, line, ev_score, edge_percent, ev_percentage, recommendation, fair_prob, true_prob, market_prob, implied_prob, confidence, engine_version, created_at, updated_at)
        VALUES 
            (:player_name, :market_key, :sport, :sport, :event_id, :outcome_key, :bookmaker, :line, :ev_score, :edge_percent, :edge_percent, :recommendation, :fair_prob, :fair_prob, 0, 0, :confidence, 'v1-grader', NOW(), NOW())
        ON CONFLICT (sport, event_id, player_name, market_key, outcome_key, bookmaker, engine_version) WHERE player_name IS NOT NULL
        DO UPDATE SET 
            ev_score = EXCLUDED.ev_score,
            edge_percent = EXCLUDED.edge_percent,
            ev_percentage = EXCLUDED.ev_percentage,
            recommendation = EXCLUDED.recommendation,
            fair_prob = EXCLUDED.fair_prob,
            true_prob = EXCLUDED.true_prob,
            confidence = EXCLUDED.confidence,
            updated_at = NOW()
    """)
    try:
        await db.execute(insert_sql, {
            "player_name": row["player_name"],
            "market_key": row["market_key"],
            "sport": sport,
            "event_id": row["game_id"],
            "outcome_key": rec.lower(),
            "bookmaker": row["book"],
            "line": row["line"],
            "ev_score": round(float(ev_score), 4),
            "edge_percent": round(float(ev_score * 100), 2),
            "confidence": float(row.get("confidence") or 0.7),
            "recommendation": rec,
            "fair_prob": round(float(fair_prob), 4)
        })
        return 1
    except Exception as e:
        logger.warning(f"Error upserting EV for {row['player_name']}: {e}")
        return 0
