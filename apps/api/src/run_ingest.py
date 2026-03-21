import asyncio
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.append(os.getcwd())

from db.session import async_session_maker, engine
from sqlalchemy import select, func
from models import PropLive, UnifiedOdds

async def run_test_ingest():
    sport = "basketball_nba"
    try:
        from services.unified_ingestion import unified_ingestion
        await unified_ingestion.run(sport)
        logger.info("Ingestion completed.")
        
        # Check counts immediately
        async with async_session_maker() as s:
            res1 = await s.execute(select(func.count()).select_from(PropLive))
            res2 = await s.execute(select(func.count()).select_from(UnifiedOdds))
            logger.info(f"VERIFICATION: PropLive: {res1.scalar()}, UnifiedOdds: {res2.scalar()}")
            
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_test_ingest())
