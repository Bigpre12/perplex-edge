"""
Snapshots of TheOddsAPI-shaped odds into line_movement_history (Postgres).
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import DATABASE_URL

logger = logging.getLogger(__name__)

_MAX_ROWS = max(100, int(os.getenv("INGEST_LINE_SNAPSHOT_MAX_ROWS", "8000")))


def _flatten_odds_rows(sport: str, odds_raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for event in odds_raw:
        if not isinstance(event, dict):
            continue
        eid = event.get("id")
        if not eid:
            continue
        for bookmaker in event.get("bookmakers") or []:
            book = bookmaker.get("key")
            if not book:
                continue
            for market in bookmaker.get("markets") or []:
                mkt = market.get("key")
                if not mkt:
                    continue
                for outcome in market.get("outcomes") or []:
                    name = outcome.get("name")
                    price = outcome.get("price")
                    if name is None or price is None:
                        continue
                    pt = outcome.get("point")
                    line_val = float(pt) if pt is not None else None
                    try:
                        odds_i = int(price)
                    except (TypeError, ValueError):
                        continue
                    rows.append(
                        {
                            "event_id": str(eid),
                            "sport": sport,
                            "market": str(mkt),
                            "outcome": str(name),
                            "bookmaker": str(book),
                            "odds": odds_i,
                            "line": line_val,
                        }
                    )
    return rows


async def snapshot_lines_from_odds_api(session: AsyncSession, sport: str, odds_raw: List[Dict[str, Any]]) -> int:
    """Bulk insert snapshots; returns rows inserted (best effort)."""
    if not odds_raw or "sqlite" in (DATABASE_URL or "").lower():
        return 0
    flat = _flatten_odds_rows(sport, odds_raw)[:_MAX_ROWS]
    if not flat:
        return 0
    try:
        stmt = text(
            """
            INSERT INTO line_movement_history
              (event_id, sport, market, outcome, bookmaker, odds, line, recorded_at)
            VALUES
              (:event_id, :sport, :market, :outcome, :bookmaker, :odds, :line, NOW())
            """
        )
        batch = 400
        total = 0
        for i in range(0, len(flat), batch):
            chunk = flat[i : i + batch]
            for row in chunk:
                await session.execute(stmt, row)
                total += 1
        await session.commit()
        logger.info("line_tracker: inserted %s snapshot rows for %s", total, sport)
        return total
    except Exception as e:
        await session.rollback()
        logger.debug("line_tracker snapshot skipped: %s", e)
        return 0


async def cleanup_old_snapshots(session: AsyncSession, hours: int = 48) -> None:
    if "sqlite" in (DATABASE_URL or "").lower():
        return
    h = max(1, int(hours))
    try:
        await session.execute(
            text(
                f"DELETE FROM line_movement_history WHERE recorded_at < NOW() - INTERVAL '{h} hours'"
            )
        )
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.debug("line_tracker cleanup: %s", e)


async def get_movement_for_sport(session: AsyncSession, sport: str, hours: int = 24) -> List[Dict[str, Any]]:
    """Open vs current odds where spread >= 3 (American odds points)."""
    if "sqlite" in (DATABASE_URL or "").lower():
        return []
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    try:
        q = text(
            """
            WITH w AS (
              SELECT event_id, sport, market, outcome, bookmaker, odds, recorded_at,
                ROW_NUMBER() OVER (
                  PARTITION BY event_id, market, outcome, bookmaker
                  ORDER BY recorded_at ASC
                ) AS rn_asc,
                ROW_NUMBER() OVER (
                  PARTITION BY event_id, market, outcome, bookmaker
                  ORDER BY recorded_at DESC
                ) AS rn_desc
              FROM line_movement_history
              WHERE sport = :sport AND recorded_at >= :since
            )
            SELECT
              o.event_id,
              o.sport,
              o.market,
              o.outcome,
              o.bookmaker,
              o.odds AS odds_open,
              c.odds AS odds_current,
              c.recorded_at AS last_seen
            FROM w o
            JOIN w c
              ON o.event_id = c.event_id
             AND o.market = c.market
             AND o.outcome = c.outcome
             AND o.bookmaker = c.bookmaker
            WHERE o.rn_asc = 1 AND c.rn_desc = 1
              AND o.odds IS NOT NULL AND c.odds IS NOT NULL
              AND ABS(c.odds - o.odds) >= 3
            ORDER BY c.recorded_at DESC
            LIMIT 100
            """
        )
        res = await session.execute(q, {"sport": sport, "since": since})
        return [dict(r._mapping) for r in res.fetchall()]
    except Exception as e:
        logger.warning("get_movement_for_sport: %s", e)
        return []
