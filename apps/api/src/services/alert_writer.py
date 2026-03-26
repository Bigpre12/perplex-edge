import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

SHARP_BOOK_LIST = ['draftkings', 'fanduel', 'betmgm', 'williamhill_us', 'betrivers', 'pointsbetus']

async def run_alert_detection(sport: str, db: Optional[AsyncSession] = None) -> int:
    if not db:
        from db.session import async_session_maker # type: ignore
        async with async_session_maker() as session:
            return await _run_detection(sport, session)
    else:
        return await _run_detection(sport, db)

async def _run_detection(sport: str, db: AsyncSession) -> int:
    try:
        logger.info(f"🔍 [ALERT WRITER] Running sharp/steam detection for {sport}")
        
        # 1. WHALE ALERT (Consensus Outlier)
        # Find books with odds >20 cents different from the consensus of all other books 
        # on the same market.
        whale_sql = text("""
            WITH consensus AS (
                SELECT 
                    event_id, market_key, outcome_key, player_name, line,
                    AVG(price) as avg_price,
                    COUNT(DISTINCT bookmaker) as book_count
                FROM unified_odds
                WHERE sport = :sport AND player_name IS NOT NULL
                GROUP BY event_id, market_key, outcome_key, player_name, line
                HAVING COUNT(DISTINCT bookmaker) > 3
            )
            SELECT 
                u.event_id, u.player_name, u.market_key, u.outcome_key as direction,
                u.line, u.bookmaker as book, u.price, c.avg_price,
                u.home_team, u.away_team
            FROM unified_odds u
            JOIN consensus c 
                ON u.event_id = c.event_id 
                AND u.market_key = c.market_key 
                AND u.outcome_key = c.outcome_key 
                AND u.player_name = c.player_name
                AND (u.line = c.line OR (u.line IS NULL AND c.line IS NULL))
            WHERE ABS(u.price - c.avg_price) >= 20
              AND u.sport = :sport
        """)
        
        whale_result = await db.execute(whale_sql, {"sport": sport})
        whales = whale_result.mappings().all()

        inserted: int = 0
        for w in whales:
            inserted += await _insert_alert_if_fresh(
                db, 
                sport=sport,
                player_name=w["player_name"],
                market_key=w["market_key"],
                alert_type="whale",
                direction=w["direction"],
                line=w["line"],
                book=w["book"],
                confidence=float(min(abs(w["price"] - w["avg_price"]) / 100.0, 1.0)),
                home_team=w.get("home_team"),
                away_team=w.get("away_team")
            )

        # 2. STEAM MOVE
        # Compare current against 30 min ago using props_history. 
        # Line moved >= 0.5 points or odds moved >= 15 cents across 2+ sharp books in the same direction.
        time_threshold = datetime.now(timezone.utc) - timedelta(minutes=30)
        
        steam_sql = text("""
            WITH current_props AS (
                 SELECT game_id, player_name, market_key, book, line, odds_over, odds_under, source_ts
                 FROM props_history
                 WHERE sport = :sport AND source_ts >= NOW() - INTERVAL '5 minutes'
            ),
            historical_props AS (
                 SELECT game_id, player_name, market_key, book, line, odds_over, odds_under, source_ts
                 FROM props_history
                 WHERE sport = :sport AND source_ts BETWEEN NOW() - INTERVAL '35 minutes' AND NOW() - INTERVAL '25 minutes'
            )
            SELECT 
                c.game_id, c.player_name, c.market_key, c.book, c.source_ts,
                c.line as cur_line, h.line as hist_line,
                c.odds_over as cur_over, h.odds_over as hist_over,
                c.odds_under as cur_under, h.odds_under as hist_under
            FROM current_props c
            JOIN historical_props h 
              ON c.game_id = h.game_id 
              AND c.player_name = h.player_name 
              AND c.market_key = h.market_key 
              AND c.book = h.book
            WHERE c.book = ANY(:sharp_books)
        """)
        
        steam_result = await db.execute(steam_sql, {
            "sport": sport, 
            "sharp_books": SHARP_BOOK_LIST
        })
        steams = steam_result.mappings().all()
        
        # Group by market and detect if 2+ sharp books moved in same direction
        market_moves = {}
        for s in steams:
            key = (s["game_id"], s["player_name"], s["market_key"])
            if key not in market_moves:
                market_moves[key] = {"over_moves": [], "under_moves": [], "line_moves": []}
                
            # Line move > 0.5
            if s["cur_line"] and s["hist_line"]:
                if s["cur_line"] > s["hist_line"] + 0.4:
                    market_moves[key]["line_moves"].append(("over", s["book"], s["cur_line"]))
                elif s["cur_line"] < s["hist_line"] - 0.4:
                    market_moves[key]["line_moves"].append(("under", s["book"], s["cur_line"]))
                    
            # Odds move >= 15 cents
            if s["cur_over"] and s["hist_over"] and s["cur_over"] <= s["hist_over"] - 15:
                market_moves[key]["over_moves"].append(s["book"])
            if s["cur_under"] and s["hist_under"] and s["cur_under"] <= s["hist_under"] - 15:
                market_moves[key]["under_moves"].append(s["book"])

        for key, moves in market_moves.items():
            _, p_name, m_key = key
            # If 2+ sharp books moved odds
            if len(moves["over_moves"]) >= 2:
                inserted += await _insert_alert_if_fresh(db, sport, p_name, m_key, "steam", "over", None, ",".join(moves["over_moves"]), 0.9)
            elif len(moves["under_moves"]) >= 2:
                inserted += await _insert_alert_if_fresh(db, sport, p_name, m_key, "steam", "under", None, ",".join(moves["under_moves"]), 0.9)
                
            # If 2+ sharp books moved line
            over_lines = [b for dir, b, l in moves["line_moves"] if dir == "over"]
            under_lines = [b for dir, b, l in moves["line_moves"] if dir == "under"]
            if len(over_lines) >= 2:
                inserted += await _insert_alert_if_fresh(db, sport, p_name, m_key, "steam", "over", None, ",".join(over_lines), 0.95)
            elif len(under_lines) >= 2:
                inserted += await _insert_alert_if_fresh(db, sport, p_name, m_key, "steam", "under", None, ",".join(under_lines), 0.95)

        if inserted > 0:
            logger.info(f"✅ [ALERT WRITER] Inserted {inserted} new shape/steam alerts for {sport}!")

        await db.commit()
        return inserted
    except Exception as e:
        logger.error(f"❌ [ALERT WRITER] Failure running detection for {sport}: {str(e)}", exc_info=True)
        await db.rollback()
        return 0

async def _insert_alert_if_fresh(
    db: AsyncSession, sport: str, player_name: str, market_key: str, 
    alert_type: str, direction: str, line: Optional[float], book: str, confidence: float,
    home_team: Optional[str] = None, away_team: Optional[str] = None
) -> int:
    """Insert only if an alert for this player/market hasn't fired in the last 10 mins."""
    
    # Ensure columns exist (DB robust check)
    try:
        await db.execute(text("ALTER TABLE sharp_alerts ADD COLUMN IF NOT EXISTS home_team TEXT"))
        await db.execute(text("ALTER TABLE sharp_alerts ADD COLUMN IF NOT EXISTS away_team TEXT"))
        await db.commit()
    except Exception:
        await db.rollback()

    check_sql = text("""
        SELECT 1 FROM sharp_alerts 
        WHERE sport = :sport 
          AND player_name = :player_name 
          AND market_key = :market_key 
          AND alert_type = :alert_type
          AND created_at >= NOW() - INTERVAL '10 minutes'
        LIMIT 1
    """)
    res = await db.execute(check_sql, {
        "sport": sport, "player_name": player_name, 
        "market_key": market_key, "alert_type": alert_type
    })
    if res.scalar() is not None:
        return 0 # Skip duplicate

    insert_sql = text("""
        INSERT INTO sharp_alerts (sport, player_name, market_key, alert_type, direction, line, book, confidence, home_team, away_team, created_at)
        VALUES (:sport, :player_name, :market_key, :alert_type, :direction, :line, :book, :confidence, :home_team, :away_team, NOW())
    """)
    await db.execute(insert_sql, {
        "sport": sport, "player_name": player_name, "market_key": market_key,
        "alert_type": alert_type, "direction": direction, "line": line,
        "book": book, "confidence": confidence, "home_team": home_team, "away_team": away_team
    })
    return 1
