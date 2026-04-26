"""Periodic cleanup for stale operational market data tables."""
from __future__ import annotations

import asyncio
import logging

from sqlalchemy import text

from celery_app import celery_app
from db.session import DATABASE_URL, async_session_maker

logger = logging.getLogger(__name__)


async def _cleanup_stale_rows() -> int:
    if "sqlite" in (DATABASE_URL or "").lower():
        return 0

    total = 0
    statements = [
        "DELETE FROM odds_snapshots WHERE captured_at < NOW() - INTERVAL '21 days'",
        "DELETE FROM market_edges WHERE updated_at < NOW() - INTERVAL '7 days'",
        "DELETE FROM ev_opportunities WHERE updated_at < NOW() - INTERVAL '7 days'",
        "DELETE FROM player_props WHERE updated_at < NOW() - INTERVAL '3 days'",
    ]

    async with async_session_maker() as session:
        for stmt in statements:
            try:
                res = await session.execute(text(stmt))
                total += int(res.rowcount or 0)
            except Exception as e:
                logger.debug("stale_data_cleanup skipped statement: %s", e)
        await session.commit()
    return total


@celery_app.task(name="workers.stale_data_cleanup.stale_data_cleanup_task")
def stale_data_cleanup_task() -> None:
    removed = asyncio.run(_cleanup_stale_rows())
    if removed:
        logger.info("stale_data_cleanup: removed %s stale rows", removed)
