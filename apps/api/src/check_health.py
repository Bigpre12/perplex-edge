
import asyncio
import os
from sqlalchemy import text
from apps.api.src.db.session import AsyncSessionLocal

async def check():
    print("Checking production heartbeats...")
    async with AsyncSessionLocal() as db:
        try:
            res = await db.execute(text("SELECT feed_name, status, last_success_at FROM heartbeats ORDER BY last_success_at DESC LIMIT 10"))
            rows = res.fetchall()
            for r in rows:
                print(f"Feed: {r[0]} | Status: {r[1]} | Last Success: {r[2]}")
            
            res = await db.execute(text("SELECT COUNT(*) FROM ev_signals WHERE created_at > NOW() - INTERVAL '24 hours'"))
            count = res.scalar()
            print(f"Recent EV Signals: {count}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
