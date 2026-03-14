import asyncio
import logging
import sys
import os

# Set up logging to stdout
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "apps", "api", "src"))
os.environ["DEVELOPMENT_MODE"] = "1"

from jobs.ingestion_service import ingest_all_odds
from database import engine, Base

async def diagnose():
    print("🚀 Starting Ingestion Diagnosis...")
    # Trigger one sport only for speed
    from services.odds.fetchers import SPORT_KEY_MAP
    # NBA is 30
    print(f"Mapping: {SPORT_KEY_MAP}")
    
    await ingest_all_odds()
    print("✅ Ingestion diagnosis complete.")

if __name__ == "__main__":
    asyncio.run(diagnose())
