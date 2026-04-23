"""Periodic cleanup of expired arbitrage_opportunities rows."""
from __future__ import annotations

import asyncio
import logging

from sqlalchemy import text

from celery_app import celery_app
from db.session import DATABASE_URL, async_session_maker

logger = logging.getLogger(__name__)


async def _delete_expired_arbs() -> int:
    if "sqlite" in (DATABASE_URL or "").lower():
        return 0
    async with async_session_maker() as session:
        res = await session.execute(
            text("DELETE FROM arbitrage_opportunities WHERE expires_at < NOW()")
        )
        n = res.rowcount if res.rowcount is not None else 0
        await session.commit()
        return int(n)


@celery_app.task(name="workers.arb_cleanup.arb_cleanup_task")
def arb_cleanup_task() -> None:
    n = asyncio.run(_delete_expired_arbs())
    if n:
        logger.info("arb_cleanup: removed %s expired arbitrage_opportunities rows", n)
