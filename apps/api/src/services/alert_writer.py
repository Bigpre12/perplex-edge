import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, insert
from models.brain import WhaleMove, SteamEvent, SharpSignal
from services.heartbeat_service import HeartbeatService
from core.config import settings

logger = logging.getLogger(__name__)

# Sharp books for move detection
SHARP_BOOKS = ['pinnacle', 'bookmaker', 'lowvig', 'draftkings', 'fanduel']

async def run_alert_detection(sport: str, db: Optional[AsyncSession] = None) -> int:
    """Entry point for intelligence generation after an ingestion cycle."""
    if not db:
        from db.session import async_session_maker # type: ignore
        async with async_session_maker() as session:
            return await _run_detection(sport, session)
    else:
        return await _run_detection(sport, db)

async def _run_detection(sport: str, db: AsyncSession) -> int:
    try:
        logger.info(f"🔍 [INTELLIGENCE ENGINE] Detecting signals for {sport}")
        
        total_inserted = 0
        
        # 1. WHALE DETECTION (Consensus Discrepancy)
        # Identify books priced significantly far from the sharp-weighted consensus.
        # We use the existing unified_odds table which was just refreshed.
        whale_sql = text("""
            WITH consensus AS (
                SELECT 
                    event_id, market_key, outcome_key, player_name, line,
                    AVG(price) as avg_price,
                    COUNT(DISTINCT bookmaker) as book_count
                FROM unified_odds
                WHERE sport = :sport AND player_name IS NOT NULL
                GROUP BY event_id, market_key, outcome_key, player_name, line
                HAVING COUNT(DISTINCT bookmaker) >= 3
            )
            SELECT 
                u.event_id, u.player_name, u.market_key, u.outcome_key,
                u.line, u.bookmaker, u.price, c.avg_price,
                u.home_team, u.away_team
            FROM unified_odds u
            JOIN consensus c 
                ON u.event_id = c.event_id 
                AND u.market_key = c.market_key 
                AND u.outcome_key = c.outcome_key 
                AND u.player_name = c.player_name
                AND (u.line = c.line OR (u.line IS NULL AND c.line IS NULL))
            WHERE ABS(u.price - c.avg_price) >= 25
              AND u.sport = :sport
        """)
        
        whale_result = await db.execute(whale_sql, {"sport": sport})
        whales = whale_result.mappings().all()
        
        for w in whales:
            severity = 'High' if abs(w["price"] - w["avg_price"]) >= 40 else 'Medium'
            whale_label = "🐋 WHALE ENTRY" if severity == 'High' else "🌊 SIGNIFICANT MOVE"
            
            # Persist to whale_moves
            await db.execute(insert(WhaleMove).values(
                sport=sport,
                event_id=w["event_id"],
                player_name=w["player_name"],
                market_key=w["market_key"],
                selection=w["outcome_key"],
                bookmaker=w["bookmaker"],
                line=w["line"],
                price_after=float(w["price"]),
                price_before=float(w["avg_price"]),
                severity=severity,
                whale_label=whale_label,
                move_type="Outlier",
                books_involved=w["bookmaker"],
                amount_estimate=float(abs(w["price"] - w["avg_price"]) * 10),
                created_at=datetime.now(timezone.utc)
            ))
            total_inserted += 1

        # 2. STEAM DETECTION (Rapid Line Velocity)
        # Compare current props against 15 min ago in props_history.
        # Look for moves >= 0.5 points or >= 15 cents in odds across 2+ sharp books.
        steam_sql = text("""
            WITH current_batch AS (
                SELECT game_id, player_name, market_key, book, line, odds_over, odds_under, source_ts
                FROM props_history
                WHERE sport = :sport AND snapshot_at >= NOW() - INTERVAL '5 minutes'
            ),
            historical_batch AS (
                SELECT game_id, player_name, market_key, book, line, odds_over, odds_under, snapshot_at
                FROM props_history
                WHERE sport = :sport 
                  AND snapshot_at BETWEEN NOW() - INTERVAL '20 minutes' AND NOW() - INTERVAL '10 minutes'
            )
            SELECT 
                c.game_id, c.player_name, c.market_key, c.book,
                c.line as cur_line, h.line as hist_line,
                c.odds_over as cur_over, h.odds_over as hist_over,
                c.odds_under as cur_under, h.odds_under as hist_under
            FROM current_batch c
            JOIN historical_batch h 
              ON c.game_id = h.game_id 
              AND c.player_name = h.player_name 
              AND c.market_key = h.market_key 
              AND c.book = h.book
            WHERE c.book = ANY(:sharp_books)
        """)
        
        steam_result = await db.execute(steam_sql, {
            "sport": sport, 
            "sharp_books": SHARP_BOOKS
        })
        steams = steam_result.mappings().all()
        
        # Group by (game, player, market) to detect multi-book moves
        market_moves = {}
        for s in steams:
            key = (s["game_id"], s["player_name"], s["market_key"])
            if key not in market_moves:
                market_moves[key] = {"over_books": [], "under_books": [], "line": s["cur_line"]}
            
            # Logic: If odds moved >= 15 American points on Over
            if s["cur_over"] and s["hist_over"] and (s["cur_over"] <= s["hist_over"] - 15):
                market_moves[key]["over_books"].append(s["book"])
            # Logic: If odds moved >= 15 American points on Under
            if s["cur_under"] and s["hist_under"] and (s["cur_under"] <= s["hist_under"] - 15):
                market_moves[key]["under_books"].append(s["book"])
                
        for key, moves in market_moves.items():
            game_id, p_name, m_key = key
            
            if len(moves["over_books"]) >= 2:
                await db.execute(insert(SteamEvent).values(
                    sport=sport,
                    player_name=p_name,
                    stat_type=m_key,
                    side="over",
                    line=moves["line"],
                    movement=15.0, # Approximate odds delta
                    book_count=len(moves["over_books"]),
                    severity=min(10.0, len(moves["over_books"]) * 2.0),
                    description=f"Rapid Steam: {len(moves['over_books'])} books pushed OVER odds for {p_name}",
                    timestamp=datetime.now(timezone.utc)
                ))
                total_inserted += 1
            elif len(moves["under_books"]) >= 2:
                await db.execute(insert(SteamEvent).values(
                    sport=sport,
                    player_name=p_name,
                    stat_type=m_key,
                    side="under",
                    line=moves["line"],
                    movement=15.0,
                    book_count=len(moves["under_books"]),
                    severity=min(10.0, len(moves["under_books"]) * 2.0),
                    description=f"Rapid Steam: {len(moves['under_books'])} books pushed UNDER odds for {p_name}",
                    timestamp=datetime.now(timezone.utc)
                ))
                total_inserted += 1

        # 3. LEGACY COMPATIBILITY: Also write to sharp_alerts for the live feed
        if whales or steams:
            from datetime import timedelta
            # Ensure the table exists or handle mapping. 
            # Given the SQL in regions/alerts.py, we just use a raw INSERT.
            for w in whales:
                await db.execute(text("""
                    INSERT INTO sharp_alerts (player_name, market_key, sport, alert_type, direction, line, book, confidence, home_team, away_team, created_at)
                    VALUES (:player_name, :market_key, :sport, :alert_type, :direction, :line, :book, :confidence, :home_team, :away_team, :created_at)
                """), {
                    "player_name": w["player_name"],
                    "market_key": w["market_key"],
                    "sport": sport,
                    "alert_type": "WHALE",
                    "direction": "OVER" if w["price"] > w["avg_price"] else "UNDER", # Heuristic
                    "line": w["line"],
                    "book": w["bookmaker"],
                    "confidence": 1.0 if abs(w["price"] - w["avg_price"]) >= 40 else 0.7,
                    "home_team": w["home_team"],
                    "away_team": w["away_team"],
                    "created_at": datetime.now(timezone.utc)
                })
            
            # (Steam events follow same logic)
            for s in steams:
                # Pivot to alert format
                await db.execute(text("""
                    INSERT INTO sharp_alerts (player_name, market_key, sport, alert_type, direction, line, book, confidence, created_at)
                    VALUES (:player_name, :market_key, :sport, :alert_type, :direction, :line, :book, :confidence, :created_at)
                """), {
                    "player_name": s["player_name"],
                    "market_key": s["market_key"],
                    "sport": sport,
                    "alert_type": "STEAM",
                    "direction": "OVER" if s["cur_over"] < s["hist_over"] else "UNDER",
                    "line": s["cur_line"],
                    "book": s["book"],
                    "confidence": 0.8,
                    "created_at": datetime.now(timezone.utc)
                })

        # 4. Heartbeat Integration
        if total_inserted > 0:
            logger.info(f"✅ [INTELLIGENCE ENGINE] Generated {total_inserted} signals for {sport} across Whales and Steam.")
            await HeartbeatService.log_heartbeat(db, f"intelligence_{sport}", status="ok", rows_written=total_inserted)
        else:
            await HeartbeatService.log_heartbeat(db, f"intelligence_{sport}", status="idle", rows_written=0)
            
        await db.commit()
        return total_inserted
    except Exception as e:
        err = str(e)
        if "whale_moves.market_key" in err or ("whale_moves" in err and "does not exist" in err):
            logger.error(
                "❌ [INTELLIGENCE ENGINE] Whale schema mismatch. Run SQL hotfix: "
                "ALTER TABLE whale_moves ADD COLUMN IF NOT EXISTS market_key TEXT; "
                "Error: %s",
                err,
                exc_info=True,
            )
        else:
            logger.error(f"❌ [INTELLIGENCE ENGINE] Signal detection failure: {err}", exc_info=True)
        await db.rollback()
        return 0
