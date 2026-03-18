import asyncio
from sqlalchemy import select
from db.session import get_db
from models.prop import PropLine, GameLine
from datetime import datetime, timezone

async def check():
    async for db in get_db():
        now = datetime.now(timezone.utc)
        
        props_stmt = select(PropLine).limit(10)
        props = (await db.execute(props_stmt)).scalars().all()
        print(f"PropLines: {len(props)}")
        
        games_stmt = select(GameLine).limit(10)
        games = (await db.execute(games_stmt)).scalars().all()
        print(f"GameLines: {len(games)}")
        
        for g in games:
            print(f"  Game: {g.home_team} vs {g.away_team} | {g.commence_time}")
            
        break

if __name__ == "__main__":
    asyncio.run(check())
