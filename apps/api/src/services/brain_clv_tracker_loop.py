import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select, and_
from db.session import async_session_maker
from models.prop import PropLine
from services.brain_clv_tracker import brain_clv_tracker

logger = logging.getLogger("clv_tracker_loop")

async def clv_tracking_loop():
    """
    Background loop that scans for games that have started 
    and snapshots their closing lines for CLV analysis.
    """
    logger.info("CLV Tracking loop started.")
    while True:
        try:
            async with async_session_maker() as db:
                # 1. Find props where:
                #    - start_time has passed (or is very close)
                #    - closing_line is still NULL (needs tracking)
                now = datetime.now(timezone.utc)
                
                # We check for games that started in the last 24 hours to 
                # catch up on any missed during downtime.
                stmt = select(PropLine).where(
                    PropLine.closing_line == None,
                    PropLine.start_time != None,
                    PropLine.start_time <= now
                ).limit(50) # Batch process 
                
                result = await db.execute(stmt)
                props_to_track = result.scalars().all()
                
                if props_to_track:
                    logger.info(f"Found {len(props_to_track)} props entering CLV phase.")
                    
                    # Group by sport to potentially optimize, but for now process list
                    # track_closing_lines handles individual prop updates
                    # We pass the objects or dicts
                    await brain_clv_tracker.track_closing_lines(props_to_track, "multi") 
                    
                else:
                    logger.debug("No new props for CLV tracking.")
                    
        except Exception as e:
            logger.error(f"CLV Tracking loop error: {e}")
            
        # Run every 5 minutes
        await asyncio.sleep(300)

async def start_clv_tracker():
    """Entry point for main.py"""
    asyncio.create_task(clv_tracking_loop())
