import asyncio
import logging
import sys

# Configure logging to see output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

from jobs.ingestion_service import ingest_all_odds

async def run():
    print("Starting manual ingestion...")
    await ingest_all_odds()
    print("Manual ingestion complete.")

if __name__ == "__main__":
    asyncio.run(run())
