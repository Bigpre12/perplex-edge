
import asyncio
import os
import sys
from sqlalchemy import select, text, func

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "apps", "api", "src"))

from db.session import AsyncSessionLocal
from models.brain import UnifiedOdds

async def diagnostic():
    async with AsyncSessionLocal() as session:
        print("--- DATABASE DIAGNOSTIC ---")
        
        # 1. Check total count
        res = await session.execute(select(func.count(UnifiedOdds.id)))
        total = res.scalar()
        print(f"Total UnifiedOdds rows: {total}")
        
        # 2. Check unique sports
        res = await session.execute(text("SELECT DISTINCT sport FROM unified_odds"))
        sports = [r[0] for r in res.all()]
        print(f"Unique sports in DB: {sports}")
        
        # 3. Sample NBA rows
        print("\n--- SAMPLE NBA ROWS ---")
        stmt = select(UnifiedOdds).where(UnifiedOdds.sport.ilike("%nba%")).limit(3)
        res = await session.execute(stmt)
        rows = res.scalars().all()
        for r in rows:
            print(f"ID: {r.id} | Sport: '{r.sport}' | Event: {r.event_id} | Player: {r.player_name} | Market: {r.market_key} | Outcome: {r.outcome_key}")

        # 4. Check EV Signals
        from models.brain import UnifiedEVSignal
        res = await session.execute(select(func.count(UnifiedEVSignal.id)))
        ev_total = res.scalar()
        print(f"\nTotal EV Signals: {ev_total}")

if __name__ == "__main__":
    asyncio.run(diagnostic())
