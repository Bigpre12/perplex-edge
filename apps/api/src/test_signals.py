import asyncio
from db.session import async_session_maker
from sqlalchemy import text

async def check_signals():
    async with async_session_maker() as session:
        print("Checking signal tables...")
        
        tables = ['whale_moves', 'steam_events', 'sharp_alerts', 'clv_trades', 'ev_signals']
        
        for table in tables:
            try:
                res = await session.execute(text(f"SELECT sport, count(*) FROM {table} GROUP BY sport"))
                print(f"{table.upper()}: {res.all()}")
            except Exception as e:
                print(f"Error querying {table}: {e}")

if __name__ == "__main__":
    asyncio.run(check_signals())
