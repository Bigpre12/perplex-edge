import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))
load_dotenv()

import logging
logging.basicConfig(level=logging.ERROR, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

from jobs.ingestion_service import ingest_all_odds, SPORT_KEY_MAP
import jobs.ingestion_service
logger.error(f"DEBUG: ingestion_service file = {jobs.ingestion_service.__file__}")

async def test_single():
    # Only test NBA (30) to save rates
    original_map = SPORT_KEY_MAP.copy()
    SPORT_KEY_MAP.clear()
    SPORT_KEY_MAP[30] = original_map[30]
    
    print("🚀 Starting test ingestion for NBA (30)...")
    await ingest_all_odds()
    print("✅ Test ingestion complete.")

if __name__ == "__main__":
    asyncio.run(test_single())
