
import asyncio
import os
from sqlalchemy import text
from db.session import async_session_maker

async def check_nfl():
    async with async_session_maker() as session:
        # Check heartbeats
        res = await session.execute(text("SELECT * FROM heartbeats WHERE feed_name = 'ingest_americanfootball_nfl'"))
        hb = res.fetchone()
        print(f"NFL Heartbeat: {hb}")
        
        # Check props count
        res = await session.execute(text("SELECT COUNT(*) FROM props_live WHERE sport = 'americanfootball_nfl'"))
        count = res.scalar()
        print(f"NFL Props Count: {count}")

if __name__ == "__main__":
    asyncio.run(check_nfl())
