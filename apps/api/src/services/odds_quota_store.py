"""
DB persistence for TheOddsAPI quota (authoritative x-requests-* headers).
Used by OddsApiClient — do not call TheOddsAPI from here.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.odds_quota import OddsApiUsage
from db.session import DATABASE_URL

logger = logging.getLogger(__name__)

USAGE_WARN_THRESHOLD = float(
    os.getenv("ODDS_API_WARN_PCT") or os.getenv("ODDS_API_USAGE_WARN_PCT", "0.8")
)
# Block outbound TheOddsAPI calls when this fraction of the monthly limit is used (reserve tail).
HARD_STOP_PCT = float(os.getenv("ODDS_API_HARD_STOP_PCT", "0.95"))


def _month_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def monthly_limit() -> int:
    raw = os.getenv("ODDS_API_MONTHLY_LIMIT") or os.getenv("THE_ODDS_API_MAX_CALLS_PER_MONTH", "20000")
    try:
        n = int(raw)
        return max(0, n)
    except ValueError:
        return 20_000


async def get_row(session: AsyncSession, month: Optional[str] = None) -> Optional[OddsApiUsage]:
    m = month or _month_key()
    res = await session.execute(select(OddsApiUsage).where(OddsApiUsage.month == m))
    return res.scalar_one_or_none()


async def is_quota_exhausted(session: AsyncSession) -> bool:
    row = await get_row(session)
    if row is None:
        return False
    return bool(row.quota_exhausted)


async def apply_quota_headers(
    session: AsyncSession,
    *,
    remaining_header: Optional[str],
    used_header: Optional[str],
    sport: Optional[str] = None,
    market: Optional[str] = None,
    endpoint_path: Optional[str] = None,
) -> None:
    """
    Upsert monthly row from API response headers.
    When remaining hits 0, set quota_exhausted (hard stop for workers until reset / manual clear).
    """
    if remaining_header is None:
        return
    try:
        remaining = int(remaining_header)
    except (TypeError, ValueError):
        return

    limit = monthly_limit()
    used_from_header: Optional[int] = None
    if used_header is not None:
        try:
            used_from_header = int(used_header)
        except (TypeError, ValueError):
            pass

    if limit > 0:
        used_calc = max(0, limit - remaining)
    else:
        used_calc = used_from_header if used_from_header is not None else 0

    used_store = used_from_header if used_from_header is not None else used_calc
    exhausted = remaining <= 0

    month = _month_key()
    now = datetime.now(timezone.utc)
    is_sqlite = "sqlite" in (DATABASE_URL or "").lower()

    prev_row = await get_row(session, month)
    prev_used = int(prev_row.requests_used or 0) if prev_row else 0
    prev_pct = (prev_used / limit) if limit > 0 else 0.0

    if is_sqlite:
        if prev_row:
            prev_row.requests_used = used_store
            prev_row.requests_remaining = remaining
            prev_row.quota_exhausted = exhausted
            prev_row.last_updated = now
        else:
            session.add(
                OddsApiUsage(
                    month=month,
                    requests_used=used_store,
                    requests_remaining=remaining,
                    quota_exhausted=exhausted,
                )
            )
    else:
        stmt = (
            pg_insert(OddsApiUsage)
            .values(
                month=month,
                requests_used=used_store,
                requests_remaining=remaining,
                quota_exhausted=exhausted,
            )
            .on_conflict_do_update(
                index_elements=["month"],
                set_={
                    "requests_used": used_store,
                    "requests_remaining": remaining,
                    "quota_exhausted": exhausted,
                    "last_updated": now,
                },
            )
        )
        await session.execute(stmt)

    new_pct = (used_store / limit) if limit > 0 else 0.0
    if not is_sqlite:
        try:
            from services.api_quota_db import append_usage_row, maybe_append_alert

            await append_usage_row(
                session,
                sport=sport,
                market=market,
                endpoint_path=endpoint_path,
                requests_used=used_store,
                requests_remaining=remaining,
                month_key=month,
            )
            await maybe_append_alert(
                session,
                prev_pct=prev_pct,
                new_pct=new_pct,
                used=used_store,
                remaining=remaining,
                limit=limit,
            )
        except Exception as e:
            logger.debug("api_quota_usage / quota_alerts side effects skipped: %s", e)

    await session.commit()

    logger.info(
        "[QUOTA_HEADERS_APPLIED] month=%s used=%s remaining=%s limit=%s pct_used=%.4f prev_pct=%.4f sport=%s market=%s path=%s",
        month,
        used_store,
        remaining,
        limit,
        new_pct,
        prev_pct,
        sport or "-",
        market or "-",
        endpoint_path or "-",
    )

    if limit > 0:
        pct = used_store / limit if limit else 0
        if pct >= USAGE_WARN_THRESHOLD:
            logger.warning(
                "ODDS API usage ~%.0f%% (%s / %s used, %s remaining)",
                pct * 100,
                used_store,
                limit,
                remaining,
            )
    if exhausted:
        logger.critical(
            "TheOddsAPI quota exhausted (x-requests-remaining=0). Ingestion calls will be skipped until the next billing cycle or manual reset."
        )


async def fetch_usage_summary(session: AsyncSession) -> Dict[str, Any]:
    """For /health and admin widgets."""
    limit = monthly_limit()
    row = await get_row(session)
    if row is None:
        return {
            "month": _month_key(),
            "used": 0,
            "remaining": limit,
            "limit": limit,
            "percent_used": 0.0,
            "is_exhausted": False,
            "is_warning": False,
        }
    used = int(row.requests_used or 0)
    rem = row.requests_remaining
    if rem is None and limit > 0:
        rem = max(0, limit - used)
    pct = (used / limit * 100) if limit > 0 else 0.0
    return {
        "month": row.month,
        "used": used,
        "remaining": rem,
        "limit": limit,
        "percent_used": round(pct, 1),
        "is_exhausted": bool(row.quota_exhausted),
        "is_warning": bool(limit > 0 and pct / 100.0 >= USAGE_WARN_THRESHOLD),
    }


async def raise_if_quota_blocked(session: AsyncSession) -> Tuple[bool, Optional[str]]:
    """
    Returns (blocked, reason). When blocked, OddsApiClient must not send HTTP requests.
    """
    row = await get_row(session)
    if row and row.quota_exhausted:
        return True, "odds_api_quota_exhausted"
    limit = monthly_limit()
    if limit > 0 and row and row.requests_remaining is not None and row.requests_remaining <= 0:
        return True, "odds_api_quota_exhausted"
    if limit > 0 and row:
        used = int(row.requests_used or 0)
        if used / limit >= HARD_STOP_PCT:
            return True, "odds_api_quota_hard_stop_pct"
    return False, None
