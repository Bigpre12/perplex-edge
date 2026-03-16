import asyncio
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeepDive")

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from clients.odds_client import odds_api_client
from services.unified_ingestion import unified_ingestion
from database import engine, Base
import models

async def dive():
    sport = "basketball_nba"
    logger.info(f"--- DIVE START: {sport} ---")
    
    # 1. Direct fetch
    logger.info("Step 1: odds_api_client.fetch_events")
    events = await odds_api_client.fetch_events(sport)
    logger.info(f"Result: {len(events)} events found")
    
    if not events:
        logger.error("DIVE FAILED: Client returned 0 events.")
        return

    # 2. Ingestion service run
    logger.info("Step 2: unified_ingestion.run")
    await unified_ingestion.run(sport)
    
    # 3. Check DB
    logger.info("Step 3: Checking DB via sqlite3 directly")
    import sqlite3
    conn = sqlite3.connect('src/data/perplex_local.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM odds')
    count = cursor.fetchone()[0]
    logger.info(f"Final Count in odds table: {count}")
    conn.close()

if __name__ == "__main__":
    asyncio.run(dive())
