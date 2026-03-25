import asyncio
import os
import sys

sys.path.append(os.getcwd() + '/apps/api/src')
from db.session import async_session_maker
from sqlalchemy import select, func
from models import PropLive, UnifiedOdds

async def run():
    async with async_session_maker() as s:
        res = await s.execute(select(PropLive.market_key, func.count(PropLive.id)).group_by(PropLive.market_key))
        print("PropLive markets:", res.all())
        res2 = await s.execute(select(UnifiedOdds.market_key, func.count(UnifiedOdds.id)).group_by(UnifiedOdds.market_key))
        print("UnifiedOdds markets:", res2.all())

if __name__ == "__main__":
    asyncio.run(run())
