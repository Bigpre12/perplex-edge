import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def check():
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL not found")
        return
    
    # Simple fix for postgres:// vs postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://")
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://")
        
    engine = create_async_engine(url)
    async with engine.connect() as conn:
        print("--- Table Counts ---")
        for table in ["props_live", "ev_signals", "unified_odds", "props_history", "heartbeats"]:
            try:
                res = await conn.execute(text(f"SELECT count(*) FROM {table}"))
                print(f"{table}: {res.scalar()}")
            except Exception as e:
                print(f"Error checking {table}: {e}")
        
        print("\n--- Recent Heartbeats ---")
        try:
            res = await conn.execute(text("SELECT service_name, status, last_heartbeat, error_count FROM heartbeats ORDER BY last_heartbeat DESC LIMIT 10"))
            for row in res:
                print(f"{row[0]} | {row[1]} | {row[2]} | Errors: {row[3]}")
        except Exception as e:
            print(f"Error checking heartbeats: {e}")

if __name__ == "__main__":
    asyncio.run(check())
