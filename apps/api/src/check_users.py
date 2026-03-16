import asyncio
import os
import sys

# Add src to path
sys.path.append(os.getcwd())

from db.session import async_session_maker
from models.user import User
from sqlalchemy import select

async def check():
    try:
        async with async_session_maker() as db:
            res = await db.execute(select(User))
            users = res.scalars().all()
            print(f"FOUND {len(users)} USERS:")
            for u in users:
                print(f"ID: {u.id} | Name: {u.username} | Email: {u.email} | Tier: {u.subscription_tier}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(check())
