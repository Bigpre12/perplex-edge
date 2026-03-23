import asyncio
import os
import logging
from sqlalchemy import text
from db.session import async_session_maker, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_data():
    async with async_session_maker() as session:
        try:
            res_odds = await session.execute(text("SELECT sport, count(*) FROM unified_odds GROUP BY sport"))
            odds_counts = res_odds.all()
            logger.info(f"Unified Odds Counts: {odds_counts}")

            res_ev = await session.execute(text("SELECT sport, count(*) FROM ev_signals GROUP BY sport"))
            ev_counts = res_ev.all()
            logger.info(f"EV Signal Counts: {ev_counts}")

            res_props = await session.execute(text("SELECT sport, count(*) FROM props_live GROUP BY sport"))
            props_counts = res_props.all()
            logger.info(f"Props Live Counts: {props_counts}")

        except Exception as e:
            logger.error(f"Error checking data: {e}")

if __name__ == "__main__":
    asyncio.run(check_data())
