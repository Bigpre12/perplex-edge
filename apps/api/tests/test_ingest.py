import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

from services.cache import cache
from jobs.ingestion_service import ingest_all_odds

async def main():
    await cache.connect()
    await ingest_all_odds()

asyncio.run(main())
