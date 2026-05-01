import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from services.heartbeat_service import HeartbeatService
from services.brains_service import brains_scorer

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
        
        # We pivot unified_odds (one row per outcome) to get over/under side-by-side
        # This is more robust as it uses the newly populated table.
        sql = text("""
            WITH pivoted AS (
                SELECT 
                    player_name, market_key, sport, bookmaker as book, line, event_id as game_id,
                    MAX(CASE WHEN outcome_key ILIKE 'over%' OR outcome_key = 'over' THEN price END) as odds_over,
                    MAX(CASE WHEN outcome_key ILIKE 'under%' OR outcome_key = 'under' THEN price END) as odds_under,
                    MAX(CASE WHEN outcome_key ILIKE 'over%' OR outcome_key = 'over' THEN implied_prob END) as implied_over,
                    MAX(CASE WHEN outcome_key ILIKE 'under%' OR outcome_key = 'under' THEN implied_prob END) as implied_under
                FROM unified_odds 
                WHERE sport = :sport
                  AND player_name IS NOT NULL
                  AND line IS NOT NULL
                GROUP BY player_name, market_key, sport, bookmaker, line, event_id
            ),
            fair_probs AS (
                SELECT 
                    *,
                    -- Normalizing no-vig prob
                    CASE 
                        WHEN (implied_over + implied_under) > 0 
                        THEN implied_over / (implied_over + implied_under) 
                        ELSE 0 
                    END as fair_over_prob,
                    -- American to Decimal conversion
                    CASE 
                        WHEN odds_over > 0 THEN (odds_over / 100.0) + 1
                        WHEN odds_over < 0 THEN (100.0 / ABS(odds_over)) + 1
                        ELSE 0
                    END as dec_over,
                    CASE 
                        WHEN odds_under > 0 THEN (odds_under / 100.0) + 1
                        WHEN odds_under < 0 THEN (100.0 / ABS(odds_under)) + 1
                        ELSE 0
                    END as dec_under
                FROM pivoted
                WHERE implied_over > 0 AND implied_under > 0
            ),
            calculated_ev AS (
                SELECT 
                    *,
                    (fair_over_prob * dec_over) - 1 as ev_over,
                    ((1 - fair_over_prob) * dec_under) - 1 as ev_under
                FROM fair_probs
            )
            SELECT * FROM calculated_ev 
            WHERE (ev_over > 0.02 OR ev_under > 0.02)
              AND (ev_over < 0.25 AND ev_under < 0.25)
        """)
        
        result = await db.execute(sql, {"sport": sport})
        edges = result.mappings().all()
        
        inserted_count = 0
        for edge in edges:
            if edge["ev_over"] > 0.02:
                # Route through Brains Scorer for confidence
                brain_over = brains_scorer.score_prop(
                    monte_carlo_prob=edge["fair_over_prob"],
                    implied_prob=float(edge.get("implied_over") or 0),
                    player_name=edge["player_name"] or "Matchup",
                    side="over",
                    line=float(edge.get("line") or 0),
                )
                inserted_count += await _upsert_ev_signal(
                    db, sport, edge, "OVER", edge["ev_over"], edge["fair_over_prob"],
                    confidence=brain_over["confidence"] / 100.0,
                    reason=brain_over["reason"],
                    tier=brain_over["tier"],
                    clv=brain_over["clv"],
                    steam=brain_over["steam"]
                )
            if edge["ev_under"] > 0.02:
                brain_under = brains_scorer.score_prop(
                    monte_carlo_prob=1.0 - edge["fair_over_prob"],
                    implied_prob=float(edge.get("implied_under") or 0),
                    player_name=edge["player_name"] or "Matchup",
                    side="under",
                    line=float(edge.get("line") or 0),
                )
                inserted_count += await _upsert_ev_signal(
                    db, sport, edge, "UNDER", edge["ev_under"], 1.0 - edge["fair_over_prob"],
                    confidence=brain_under["confidence"] / 100.0,
                    reason=brain_under["reason"],
                    tier=brain_under["tier"],
                    clv=brain_under["clv"],
                    steam=brain_under["steam"]
                )
        
        # Log Heartbeat before commit
        if inserted_count > 0:
            logger.info(f"✅ [EV WRITER] Generated {inserted_count} +EV signals for {sport}")
            await HeartbeatService.log_heartbeat(db, f"ev_grader_{sport}", status="ok", rows_written=inserted_count)
        else:
            await HeartbeatService.log_heartbeat(db, f"ev_grader_{sport}", status="idle", rows_written=0)

        await db.commit()
        return inserted_count
        
    except Exception as e:
        logger.error(f"❌ [EV WRITER] Failed EV generation for {sport}: {str(e)}", exc_info=True)
        await db.rollback()
        return 0

async def _upsert_ev_signal(db: AsyncSession, sport: str, row: dict, rec: str, ev_score: float, fair_prob: float, confidence: float = 0.7, reason: str = None, tier: str = None, clv: float = 0.0, steam: bool = False) -> int:
    insert_sql = text("""
        INSERT INTO ev_signals 
            (player_name, market_key, sport, sport_key, prop_type, event_id, outcome_key, bookmaker, line, ev_score, edge_percent, ev_percentage, recommendation, fair_prob, true_prob, market_prob, implied_prob, confidence, reason, tier, clv, steam, engine_version, created_at, updated_at)
        VALUES 
            (:player_name, :market_key, :sport, :sport, :prop_type, :event_id, :outcome_key, :bookmaker, :line, :ev_score, :edge_percent, :edge_percent, :recommendation, :fair_prob, :fair_prob, 0, 0, :confidence, :reason, :tier, :clv, :steam, 'v1-grader', NOW(), NOW())
        ON CONFLICT (sport, event_id, player_name, market_key, outcome_key, bookmaker, engine_version) WHERE player_name IS NOT NULL
        DO UPDATE SET 
            ev_score = EXCLUDED.ev_score,
            edge_percent = EXCLUDED.edge_percent,
            ev_percentage = EXCLUDED.ev_percentage,
            recommendation = EXCLUDED.recommendation,
            fair_prob = EXCLUDED.fair_prob,
            true_prob = EXCLUDED.true_prob,
            confidence = EXCLUDED.confidence,
            reason = EXCLUDED.reason,
            tier = EXCLUDED.tier,
            clv = EXCLUDED.clv,
            steam = EXCLUDED.steam,
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
            "confidence": float(confidence),
            "recommendation": rec,
            "fair_prob": round(float(fair_prob), 4),
            "reason": reason,
            "tier": tier,
            "clv": float(clv or 0),
            "steam": bool(steam)
        })
        return 1
    except Exception as e:
        logger.warning(f"Error upserting EV for {row['player_name']}: {e}")
        return 0
