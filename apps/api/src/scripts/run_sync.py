import asyncio
import logging
import os
from dotenv import load_dotenv

# Ensure .env is loaded from the parent api/ directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from jobs.ingestion_service import ingest_all_odds

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("🚀 Starting manual data ingestion...")
    try:
        await ingest_all_odds()
        logger.info("✅ Manual ingestion complete!")
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
