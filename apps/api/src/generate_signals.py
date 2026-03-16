# apps/api/src/generate_signals.py
import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.getcwd())

from db.session import engine, async_session_maker, DATABASE_URL
from workers.ev_engine import ev_engine
from sqlalchemy import text

async def run():
    print("--- SIGNAL GENERATION CYCLE ---")
    print(f"DEBUG: Using DATABASE_URL: {DATABASE_URL}")
    
    # 1. Check Odds Count
    async with async_session_maker() as session:
        res = await session.execute(text("SELECT count(*) FROM odds"))
        odds_count = res.scalar()
        print(f"Current Odds Count: {odds_count}")
        
        if odds_count == 0:
            print("ERROR: No odds found. Please run ingestion first.")
            return

    # 2. Run EV Engine
    print("Running EV Engine for basketball_nba...")
    await ev_engine.run_ev_cycle("basketball_nba")
    
    # 3. Verify Signals
    async with async_session_maker() as session:
        res = await session.execute(text("SELECT count(*) FROM ev_signals"))
        ev_count = res.scalar()
        print(f"Generated EV Signals: {ev_count}")
        
        if ev_count > 0:
            print("SUCCESS: Intel Intelligence populated!")
        else:
            print("WARNING: No EV signals found with current threshold.")

if __name__ == "__main__":
    asyncio.run(run())
