import asyncio
from database import async_session_maker
from models.props import PropLine, PropOdds
from sqlalchemy import select
from datetime import datetime, timezone

async def check():
    async with async_session_maker() as s:
        res = await s.execute(select(PropLine).limit(10))
        proplines = res.scalars().all()
        print(f"PropLines COUNT: {len(proplines)}")
        for p in proplines:
            odds_res = await s.execute(select(PropOdds).where(PropOdds.prop_line_id == p.id))
            odds = odds_res.scalars().all()
            print(f"- {p.player_name}: {p.stat_type} | Odds Count: {len(odds)} | Start: {p.start_time}")

if __name__ == "__main__":
    asyncio.run(check())
