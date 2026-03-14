import asyncio
from database import async_session_maker
from app.models.modelpick import ModelPick
from sqlalchemy import select, func

async def check():
    async with async_session_maker() as session:
        count = await session.execute(select(func.count(ModelPick.id)))
        print(f"ModelPicks: {count.scalar()}")

if __name__ == "__main__":
    asyncio.run(check())
