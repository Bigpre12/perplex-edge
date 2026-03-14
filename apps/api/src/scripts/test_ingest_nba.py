import asyncio, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv; load_dotenv()
from jobs.ingestion_service import ingest_all_odds
from services.odds.fetchers import SPORT_KEY_MAP
import logging

logging.basicConfig(level=logging.INFO)

async def test_nba():
    with open("nba_debug.log", "w", encoding="utf-8") as f:
        sys.stdout = f
        sys.stderr = f
        
        # Only keep NBA (30) in the map for this test
        keys = list(SPORT_KEY_MAP.keys())
        for k in keys:
            if k != 30:
                del SPORT_KEY_MAP[k]
        
        print(f"INGEST DEBUG: source file: {sys.modules['jobs.ingestion_service'].__file__}")
        print("Starting NBA-only ingestion test...")
        await ingest_all_odds()
        print("NBA-only ingestion test complete.")

if __name__ == "__main__":
    asyncio.run(test_nba())
