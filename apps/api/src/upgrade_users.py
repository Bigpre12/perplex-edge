import asyncio
import os
import sys

# Add src to path
sys.path.append(os.getcwd())

from db.session import async_session_maker
from models.user import User
from sqlalchemy import update

async def upgrade_users():
    try:
        async with async_session_maker() as db:
            await db.execute(update(User).values(subscription_tier="elite"))
            await db.commit()
            print("Successfully upgraded all users to 'elite' tier.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(upgrade_users())
