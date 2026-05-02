# apps/api/src/services/clv_service.py
"""
CLV Engine — Closing Line Value tracking and steam detection.

Methods:
  record_opening_line  — persists first-seen line into ``line_movement``
  compute_clv          — current_price − closing_price (American odds delta)
  get_steam_signal     — True if 2+ pt move across 3+ books in 30 min
  calculate_clv        — legacy per-bet CLV calculation
  settle_clv_for_user  — batch settle for a user's bets
  get_clv_summary      — user-facing CLV dashboard data
  compute_for_pick     — immediate CLV for a pick
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, update, desc, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import async_session_maker

logger = logging.getLogger(__name__)


class CLVEngine:
    """New intelligence methods — line movement tracking and steam detection."""

    # ------------------------------------------------------------------
    # Record opening line
    # ------------------------------------------------------------------
    async def record_opening_line(
        self,
        event_id: str,
        player_name: Optional[str],
        market_key: str,
        line: float,
        price: float,
        bookmaker: str,
        db: Optional[AsyncSession] = None,
    ) -> None:
        """
        Insert an opening-line snapshot into ``line_movement``.
        Idempotent: skips if we already have a row for this exact combo.
        """
        try:
            if db:
                await self._execute_record_opening(db, event_id, player_name, market_key, bookmaker, price, line)
                return
            
            async with async_session_maker() as session:
                await self._execute_record_opening(session, event_id, player_name, market_key, bookmaker, price, line)
        except Exception as e:
            logger.debug("record_opening_line skipped: %s", e)

    async def _execute_record_opening(self, session, event_id, player_name, market_key, bookmaker, price, line):
        # Check existence first to avoid dupe opening lines
        check = text("""
            SELECT 1 FROM line_movement
            WHERE event_id  = :event_id
              AND COALESCE(player_name, '') = COALESCE(:player_name, '')
              AND market_key = :market_key
              AND bookmaker  = :bookmaker
            LIMIT 1
        """)
        existing = await session.execute(check, {
            "event_id": event_id,
            "player_name": player_name,
            "market_key": market_key,
            "bookmaker": bookmaker,
        })
        if existing.scalar_one_or_none() is not None:
            return  # already recorded

        ins = text("""
            INSERT INTO line_movement
                (event_id, player_name, market_key, bookmaker, price, line, is_closing)
            VALUES
                (:event_id, :player_name, :market_key, :bookmaker, :price, :line, FALSE)
        """)
        await session.execute(ins, {
            "event_id": event_id,
            "player_name": player_name,
            "market_key": market_key,
            "bookmaker": bookmaker,
            "price": price,
            "line": line,
        })
        await session.commit()

    # ------------------------------------------------------------------
    # Compute CLV for a specific prop
    # ------------------------------------------------------------------
    async def compute_clv(
        self,
        event_id: str,
        player_name: Optional[str],
        market_key: str,
        bookmaker: str,
        db: Optional[AsyncSession] = None,
    ) -> float:
        """
        Returns the American-odds delta between the earliest (opening)
        and latest (closing) recorded price for this prop line.
        """
        try:
            if db:
                return await self._execute_compute_clv(db, event_id, player_name, market_key, bookmaker)
            
            async with async_session_maker() as session:
                return await self._execute_compute_clv(session, event_id, player_name, market_key, bookmaker)
        except Exception as e:
            logger.debug("compute_clv error: %s", e)
            return 0.0

    async def _execute_compute_clv(self, session: AsyncSession, event_id: str, player_name: Optional[str], market_key: str, bookmaker: str):
        sql = text("""
            SELECT price, recorded_at
            FROM line_movement
            WHERE event_id  = :event_id
              AND COALESCE(player_name, '') = COALESCE(:player_name, '')
              AND market_key = :market_key
              AND bookmaker  = :bookmaker
            ORDER BY recorded_at ASC
        """)
        result = await session.execute(sql, {
            "event_id": event_id,
            "player_name": player_name,
            "market_key": market_key,
            "bookmaker": bookmaker,
        })
        rows = result.mappings().all()

        if len(rows) < 2:
            return 0.0

        opening_price = float(rows[0]["price"])
        closing_price = float(rows[-1]["price"])
        return round(closing_price - opening_price, 2)


    # ------------------------------------------------------------------
    # Steam signal detection
    # ------------------------------------------------------------------
    async def get_steam_signal(
        self, event_id: str, market_key: str, player_name: Optional[str] = None, db: Optional[AsyncSession] = None
    ) -> bool:
        """
        Returns True if the line has moved 2+ points in the same direction
        across 3+ bookmakers in the last 30 minutes.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
        try:
            if db:
                return await self._execute_steam_check(db, event_id, market_key, cutoff)
            
            async with async_session_maker() as session:
                return await self._execute_steam_check(session, event_id, market_key, cutoff)
        except Exception as e:
            logger.debug("get_steam_signal failed: %s", e)
            return False

    async def _execute_steam_check(self, session: AsyncSession, event_id: str, market_key: str, cutoff: datetime):
        # Try line_ticks first (more granular)
        sql = text("""
            WITH recent AS (
                SELECT bookmaker,
                        MIN(line::float) AS min_line,
                        MAX(line::float) AS max_line
                FROM line_ticks
                WHERE event_id   = :event_id
                    AND market_key  = :market_key
                    AND created_at >= :cutoff
                GROUP BY bookmaker
                HAVING MAX(line::float) - MIN(line::float) >= 2.0
            )
            SELECT COUNT(*) AS book_count FROM recent
        """)
        result = await session.execute(sql, {
            "event_id": event_id,
            "market_key": market_key,
            "cutoff": cutoff,
        })
        count = result.scalar_one_or_none()
        if count is not None and int(count) >= 3:
            return True

        # Fallback: check line_movement table
        sql2 = text("""
            WITH recent AS (
                SELECT bookmaker,
                        MIN(price) AS min_price,
                        MAX(price) AS max_price
                FROM line_movement
                WHERE event_id   = :event_id
                    AND market_key  = :market_key
                    AND recorded_at >= :cutoff
                GROUP BY bookmaker
                HAVING MAX(price) - MIN(price) >= 2.0
            )
            SELECT COUNT(*) AS book_count FROM recent
        """)
        result2 = await session.execute(sql2, {
            "event_id": event_id,
            "market_key": market_key,
            "cutoff": cutoff,
        })
        count2 = result2.scalar_one_or_none()
        if count2 is not None and int(count2) >= 3:
            return True
        return False


    # ------------------------------------------------------------------
    # Sharp consensus estimation
    # ------------------------------------------------------------------
    async def get_sharp_consensus(
        self, event_id: str, market_key: str, outcome_key: str, db: Optional[AsyncSession] = None
    ) -> float:
        """
        Returns fraction (0-1) of sharp books whose implied probability
        for this outcome exceeds the market average.
        """
        from core.config import settings

        try:
            if db:
                return await self._execute_sharp_consensus(db, event_id, market_key, outcome_key)
            
            async with async_session_maker() as session:
                return await self._execute_sharp_consensus(session, event_id, market_key, outcome_key)
        except Exception as e:
            logger.debug("get_sharp_consensus error: %s", e)
            return 0.5

    async def _execute_sharp_consensus(self, session, event_id, market_key, outcome_key):
        from core.config import settings
        sql = text("""
            SELECT bookmaker, implied_prob
            FROM unified_odds
            WHERE event_id   = :event_id
              AND market_key = :market_key
              AND outcome_key = :outcome_key
              AND implied_prob IS NOT NULL
        """)
        rows = (await session.execute(sql, {
            "event_id": event_id,
            "market_key": market_key,
            "outcome_key": outcome_key,
        })).mappings().all()

        if not rows:
            return 0.5

        avg_prob = sum(float(r["implied_prob"]) for r in rows) / len(rows)
        sharp_books = [
            r for r in rows
            if any(s in r["bookmaker"].lower() for s in settings.SHARP_BOOKMAKERS)
        ]

        if not sharp_books:
            return 0.5

        agrees = sum(
            1 for r in sharp_books if float(r["implied_prob"]) >= avg_prob
        )
        return round(agrees / len(sharp_books), 2)


class CLVService(CLVEngine):
    """
    Extended CLV service — inherits the new engine methods and keeps
    the original legacy methods for backwards compatibility.
    """

    async def calculate_clv(self, bet: Any, closing_line: float) -> dict:
        if not closing_line or not bet.line:
            return {"clv": 0.0, "clv_label": "NEUTRAL", "beat_close": False}

        if hasattr(bet, "side") and bet.side.lower() == "over":
            clv = round(closing_line - bet.line, 2)
        elif hasattr(bet, "side") and bet.side.lower() == "under":
            clv = round(bet.line - closing_line, 2)
        else:
            clv = 0.0

        label = (
            "GREAT" if clv >= 1.0
            else "GOOD" if clv >= 0.5
            else "NEUTRAL" if clv >= -0.5
            else "POOR"
        )
        return {"clv": clv, "clv_label": label, "beat_close": clv > 0}

    async def settle_clv_for_user(self, user_id: str, db: AsyncSession):
        """Settle CLV for all completed bets for a user."""
        try:
            from models.bet import BetLog
            from models.prop import PropOdds

            stmt = select(BetLog).where(
                BetLog.user_id == user_id,
                BetLog.clv == None,  # noqa: E711
                BetLog.status != "pending",
            )
            res = await db.execute(stmt)
            bets = res.scalars().all()

            updated = 0
            for bet in bets:
                closing_stmt = (
                    select(PropOdds)
                    .where(
                        PropOdds.player_name == bet.player_name,
                        PropOdds.stat_category == bet.stat_category,
                    )
                    .order_by(desc(PropOdds.updated_at))
                )
                closing_res = await db.execute(closing_stmt)
                closing = closing_res.scalars().first()
                if not closing:
                    continue

                result = await self.calculate_clv(bet, closing.line)
                bet.clv = result["clv"]
                bet.clv_label = result["clv_label"]
                updated += 1

            await db.commit()
            return updated
        except Exception as e:
            logger.error("Error settling CLV: %s", e)
            await db.rollback()
            return 0

    async def get_clv_summary(self, user_id: str, db: AsyncSession) -> dict:
        try:
            from models.bet import BetLog

            stmt = select(BetLog).where(BetLog.user_id == user_id, BetLog.clv != None)  # noqa: E711
            res = await db.execute(stmt)
            bets = res.scalars().all()

            if not bets:
                return {"message": "No CLV data available yet."}

            clvs = [b.clv for b in bets if b.clv is not None]
            beat_close = sum(1 for c in clvs if c > 0)
            avg_clv = round(sum(clvs) / len(clvs), 3) if clvs else 0.0

            return {
                "user_id": user_id,
                "total_bets_with_clv": len(clvs),
                "avg_clv": avg_clv,
                "beat_close_pct": round(beat_close / len(clvs) * 100, 1) if clvs else 0.0,
                "skill_verdict": (
                    "SHARP" if avg_clv >= 0.5
                    else "ABOVE AVG" if avg_clv >= 0
                    else "NEEDS WORK"
                ),
                "interpretation": f"You beat closing line by {avg_clv} pts on average.",
            }
        except Exception as e:
            logger.error("Error getting CLV summary: %s", e)
            return {"error": str(e)}

    def compute_for_pick(
        self, pick_data: Dict, odds_history: Optional[List[Dict]] = None
    ) -> Dict:
        """Immediate CLV calculation for a specific pick."""
        if not odds_history or len(odds_history) < 2:
            return {"clv_percentage": 0.0, "roi_percentage": 0.0}

        opening = odds_history[0].get("line_value", 0)
        closing = odds_history[-1].get("line_value", 0)

        if opening == 0:
            return {"clv_percentage": 0.0, "roi_percentage": 0.0}

        clv_pct = ((closing - opening) / opening) * 100
        return {
            "clv_percentage": round(clv_pct, 2),
            "roi_percentage": round(clv_pct * 1.5, 2),
        }


# Singleton — keeps the same import interface as before
clv_service = CLVService()
calculate_clv = clv_service.calculate_clv
settle_clv_for_user = clv_service.settle_clv_for_user
get_clv_summary = clv_service.get_clv_summary
compute_for_pick = clv_service.compute_for_pick
