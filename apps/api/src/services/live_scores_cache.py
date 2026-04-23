"""Cache live scoreboard rows in ``live_scores`` (Postgres upsert)."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import DATABASE_URL

logger = logging.getLogger(__name__)


def _is_sqlite() -> bool:
    return "sqlite" in (DATABASE_URL or "").lower()


def _score_int(v: Any) -> int:
    try:
        if v is None:
            return 0
        return int(float(str(v).replace(",", "")))
    except (TypeError, ValueError):
        return 0


def _norm_game_row(sport: str, g: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    eid = g.get("id") or g.get("external_game_id") or g.get("game_id")
    if not eid:
        return None
    home = g.get("home_team") or g.get("home_team_name") or ""
    away = g.get("away_team") or g.get("away_team_name") or ""
    period = g.get("period", "")
    if period is not None and not isinstance(period, str):
        period = str(period)
    return {
        "event_id": str(eid),
        "sport": sport,
        "home_team": str(home)[:100] if home else "Home",
        "away_team": str(away)[:100] if away else "Away",
        "home_score": _score_int(g.get("home_score")),
        "away_score": _score_int(g.get("away_score")),
        "status": str(g.get("status") or "scheduled")[:50],
        "period": period[:20] if period else "",
        "clock": str(g.get("clock") or "")[:20],
        "home_abbr": str(g.get("home_abbr") or g.get("home_team_abbr") or "")[:10],
        "away_abbr": str(g.get("away_abbr") or g.get("away_team_abbr") or "")[:10],
    }


async def upsert_live_scores_from_games(session: AsyncSession, sport: str, games: List[Dict[str, Any]]) -> int:
    if _is_sqlite() or not games:
        return 0
    stmt = text(
        """
        INSERT INTO live_scores (
          event_id, sport, home_team, away_team, home_score, away_score,
          status, period, clock, home_abbr, away_abbr, last_updated
        ) VALUES (
          :event_id, :sport, :home_team, :away_team, :home_score, :away_score,
          :status, :period, :clock, :home_abbr, :away_abbr, NOW()
        )
        ON CONFLICT (event_id) DO UPDATE SET
          sport = EXCLUDED.sport,
          home_team = EXCLUDED.home_team,
          away_team = EXCLUDED.away_team,
          home_score = EXCLUDED.home_score,
          away_score = EXCLUDED.away_score,
          status = EXCLUDED.status,
          period = EXCLUDED.period,
          clock = EXCLUDED.clock,
          home_abbr = EXCLUDED.home_abbr,
          away_abbr = EXCLUDED.away_abbr,
          last_updated = NOW()
        """
    )
    n = 0
    try:
        for g in games:
            if not isinstance(g, dict):
                continue
            row = _norm_game_row(sport, g)
            if not row:
                continue
            await session.execute(stmt, row)
            n += 1
        await session.commit()
        return n
    except Exception as e:
        await session.rollback()
        logger.debug("live_scores upsert skipped: %s", e)
        return 0


async def cache_freshness_seconds(session: AsyncSession, sport: str) -> Optional[float]:
    """Seconds since newest ``last_updated`` for sport; None if no rows."""
    if _is_sqlite():
        return None
    try:
        q = text(
            """
            SELECT MAX(last_updated) AS mx FROM live_scores WHERE sport = :sport
            """
        )
        res = await session.execute(q, {"sport": sport})
        row = res.mappings().first()
        if not row or row["mx"] is None:
            return None
        mx: datetime = row["mx"]
        if mx.tzinfo is None:
            mx = mx.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - mx).total_seconds()
    except Exception:
        return None


async def fetch_cached_games(session: AsyncSession, sport: str) -> List[Dict[str, Any]]:
    if _is_sqlite():
        return []
    try:
        q = text(
            """
            SELECT event_id, sport, home_team, away_team, home_score, away_score,
                   status, period, clock, home_abbr, away_abbr, last_updated
            FROM live_scores
            WHERE sport = :sport
            ORDER BY last_updated DESC
            """
        )
        res = await session.execute(q, {"sport": sport})
        return [dict(r._mapping) for r in res.fetchall()]
    except Exception:
        return []


async def read_cache_or_stale(
    session: AsyncSession, sport: str, max_age_sec: float = 60.0
) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Returns (rows, is_fresh). When is_fresh, caller should use rows without hitting ESPN.
    When not fresh, rows may still be returned for optional use; caller should refresh externally.
    """
    age = await cache_freshness_seconds(session, sport)
    rows = await fetch_cached_games(session, sport)
    if age is None or not rows:
        return [], False
    return rows, age <= max_age_sec
