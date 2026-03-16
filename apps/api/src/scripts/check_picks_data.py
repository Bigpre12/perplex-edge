import asyncio
from sqlalchemy import select
from db.session import SessionLocal, get_async_db
from models.brain import ModelPick

from models.prop import PropLine
from datetime import datetime, timezone

async def check_data():
    async for db in get_async_db():
        now = datetime.now(timezone.utc)
        print(f"Current UTC time: {now}")
        
        stmt = select(PropLine).where(PropLine.start_time > now).limit(5)
        result = await db.execute(stmt)
        lines = result.scalars().all()
        print(f"--- Found {len(lines)} future games in PropLine ---")
        for l in lines:
            print(f"GameID: {l.game_id}, Start: {l.start_time}, Team: {l.team} vs {l.opponent}")
        
        stmt = select(ModelPick).limit(10)
        result = await db.execute(stmt)
        picks = result.scalars().all()
        print(f"--- Recent ModelPicks ---")
        for p in picks:
             print(f"ID: {p.id}, Player: {p.player_name}, GameID: {p.game_id}")
        break

if __name__ == "__main__":
    asyncio.run(check_data())
