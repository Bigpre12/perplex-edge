import asyncio
from database import async_session_maker
from models.props import PropLine, PropOdds
from sqlalchemy import select, func

async def check():
    async with async_session_maker() as s:
        l_count = await s.execute(select(func.count(PropLine.id)))
        o_count = await s.execute(select(func.count(PropOdds.id)))
        
        last_l = await s.execute(select(PropLine.created_at).order_by(PropLine.created_at.desc()).limit(1))
        last_o = await s.execute(select(PropOdds.updated_at).order_by(PropOdds.updated_at.desc()).limit(1))
        
        print(f"PropLines: {l_count.scalar()}")
        print(f"PropOdds: {o_count.scalar()}")
        print(f"Latest PropLine Created: {last_l.scalar()}")
        print(f"Latest PropOdds Updated: {last_o.scalar()}")

if __name__ == "__main__":
    asyncio.run(check())
