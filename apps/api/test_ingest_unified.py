import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from services.unified_ingestion import unified_ingestion
from database import engine, Base
import models # Load all models

async def test_ingest():
    print("Starting manual ingestion test for NBA...")
    try:
        # Ensure tables exist
        Base.metadata.create_all(bind=engine)
        print("DB tables verified/created.")
        
        await unified_ingestion.run("basketball_nba")
        print("Ingestion test completed successfully!")
    except Exception as e:
        print(f"Ingestion test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ingest())
