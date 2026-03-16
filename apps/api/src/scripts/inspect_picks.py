import asyncio
from database import async_session_maker
from models.brain import ModelPick
from sqlalchemy import select, func

async def check_picks():
    async with async_session_maker() as session:
        # Total count
        total_stmt = select(func.count(ModelPick.id))
        total_res = await session.execute(total_stmt)
        print(f"Total ModelPicks: {total_res.scalar()}")
        
        # Count by status
        status_stmt = select(ModelPick.status, func.count(ModelPick.id)).group_by(ModelPick.status)
        status_res = await session.execute(status_stmt)
        print(f"Stats by status: {status_res.all()}")
        
        # Check first few rows to see what sport keys look like
        sample_stmt = select(ModelPick).limit(5)
        sample_res = await session.execute(sample_stmt)
        samples = sample_res.scalars().all()
        for p in samples:
            print(f"Sample: ID={p.id}, Sport={p.sport_key}, Status={p.status}")

if __name__ == "__main__":
    asyncio.run(check_picks())
