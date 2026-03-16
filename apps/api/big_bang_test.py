import asyncio
import os
import sys
import logging
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from database import engine, Base, SessionLocal, async_session_maker
import models
from services.unified_ingestion import unified_ingestion
from sqlalchemy import text

async def run_all():
    print("--- BIG BANG INGESTION TEST ---")
    
    # 1. Clean up
    db_file = os.path.abspath(os.path.join("src", "data", "perplex_local.db"))
    print(f"DEBUG: Target DB File: {db_file}")
    if os.path.exists(db_file):
        print(f"Deleting {db_file}...")
        os.remove(db_file)
    
    # 2. Recreate
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    # 3. Run Ingestion
    print("Running ingestion for basketball_nba...")
    await unified_ingestion.run("basketball_nba")
    
    # 4. Count
    print(f"DEBUG: Verifying count using engine: {engine.url}")
    print("Verifying count...")
    with engine.connect() as conn:
        count = conn.execute(text("SELECT count(*) FROM odds")).scalar()
        print(f"VERIFIED_COUNT: {count}")
    
    if count > 0:
        print("SUCCESS: Data persisted!")
    else:
        print("FAILURE: Count is still 0.")

if __name__ == "__main__":
    asyncio.run(run_all())
