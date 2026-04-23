"""
Optional Postgres audit trail for TheOddsAPI quota (api_quota_usage, quota_alerts).
Works alongside odds_api_usage header sync; failures are non-fatal.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import DATABASE_URL

logger = logging.getLogger(__name__)


def _is_sqlite() -> bool:
    return "sqlite" in (DATABASE_URL or "").lower()


async def append_usage_row(
    session: AsyncSession,
    *,
    sport: Optional[str],
    market: Optional[str],
    endpoint_path: Optional[str],
    requests_used: Optional[int],
    requests_remaining: Optional[int],
    month_key: str,
) -> None:
    """INSERT into api_quota_usage; caller commits. No-op on sqlite / missing table."""
    if _is_sqlite():
        return
    await session.execute(
        text(
            """
            INSERT INTO api_quota_usage (
              sport, market, endpoint_path, requests_used, requests_remaining, month_key
            ) VALUES (
              :sport, :market, :endpoint_path, :requests_used, :requests_remaining, :month_key
            )
            """
        ),
        {
            "sport": (sport or "")[:64] or None,
            "market": (market or "")[:256] or None,
            "endpoint_path": endpoint_path,
            "requests_used": requests_used,
            "requests_remaining": requests_remaining,
            "month_key": month_key,
        },
    )


async def maybe_append_alert(
    session: AsyncSession,
    *,
    prev_pct: float,
    new_pct: float,
    used: int,
    remaining: int,
    limit: int,
) -> None:
    """INSERT quota_alerts on threshold cross; caller commits."""
    if _is_sqlite() or limit <= 0:
        return

    warn = float(os.getenv("ODDS_API_WARN_PCT") or os.getenv("ODDS_API_USAGE_WARN_PCT", "0.8"))
    critical = float(os.getenv("ODDS_API_HARD_STOP_PCT", "0.95"))
    try:
        res = await session.execute(
            text("SELECT warn_pct, critical_pct, hard_stop_pct FROM api_quota_config WHERE id = 1")
        )
        row = res.mappings().first()
        if row:
            if row.get("warn_pct") is not None:
                warn = float(row["warn_pct"])
            if row.get("critical_pct") is not None:
                critical = float(row["critical_pct"])
            hp = row.get("hard_stop_pct")
            hard_stop = float(hp) if hp is not None else critical
        else:
            hard_stop = critical
    except Exception:
        hard_stop = critical

    level: Optional[str] = None
    msg: Optional[str] = None
    if prev_pct < 1.0 and new_pct >= 1.0:
        level, msg = "HARD_STOP", "Monthly quota exhausted (100%+ used vs limit)."
    elif prev_pct < hard_stop and new_pct >= hard_stop:
        level, msg = "HARD_STOP", f"TheOddsAPI usage at or above hard-stop threshold (~{hard_stop:.0%})."
    elif prev_pct < critical and new_pct >= critical:
        level, msg = "CRITICAL", f"TheOddsAPI usage at or above critical threshold (~{critical:.0%})."
    elif prev_pct < warn and new_pct >= warn:
        level, msg = "WARNING", f"TheOddsAPI usage at or above warning threshold (~{warn:.0%})."

    if not level:
        return

    await session.execute(
        text(
            """
            INSERT INTO quota_alerts (level, message, pct_used, requests_used, requests_remaining, monthly_limit)
            VALUES (:level, :message, :pct_used, :requests_used, :requests_remaining, :monthly_limit)
            """
        ),
        {
            "level": level,
            "message": msg,
            "pct_used": new_pct,
            "requests_used": used,
            "requests_remaining": remaining,
            "monthly_limit": limit,
        },
    )
    logger.warning("[QUOTA_ALERT] %s — %s (pct=%.4f used=%s/%s)", level, msg, new_pct, used, limit)


async def try_fetch_monthly_summary_json(session: AsyncSession) -> Optional[Dict[str, Any]]:
    if _is_sqlite():
        return None
    try:
        res = await session.execute(text("SELECT get_monthly_quota_summary() AS j"))
        raw = res.scalar_one_or_none()
        if raw is None:
            return None
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, str):
            return json.loads(raw)
        return dict(raw) if hasattr(raw, "keys") else None
    except Exception as e:
        logger.debug("get_monthly_quota_summary unavailable: %s", e)
        return None
