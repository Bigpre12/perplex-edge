
import asyncio
import os
from sqlalchemy import text
from db.session import engine

async def check_data():
    async with engine.connect() as conn:
        # Check overall counts
        res = await conn.execute(text("SELECT count(*) FROM unified_odds"))
        total = res.scalar()
        print(f"Total UnifiedOdds: {total}")
        
        # Check by sport
        res = await conn.execute(text("SELECT sport, count(*) FROM unified_odds GROUP BY sport"))
        for row in res:
            print(f"Sport: {row[0]}, Count: {row[1]}")
            
        # Check sample rows for NBA
        res = await conn.execute(text("SELECT sport, market_key, player_name, outcome_key FROM unified_odds LIMIT 10"))
        print("\nSample Rows:")
        for row in res:
            print(row)

if __name__ == "__main__":
    asyncio.run(check_data())
