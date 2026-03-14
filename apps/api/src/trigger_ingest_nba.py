import asyncio
import logging
import sys
import os

from jobs.ingestion_service import fetch_props_for_sport, write_props_to_db, write_lines_to_db, fetch_lines_for_sport

async def run():
    sport_id = 30 # NBA
    print(f"Starting manual ingestion for NBA (30)...")
    
    # Force fresh fetch by bypassing cache if possible (or just wait)
    props = await fetch_props_for_sport(sport_id)
    print(f"Fetched props: {len(props) if props else 'None'}")
    
    if props:
        await write_props_to_db(sport_id, props)
    
    lines = await fetch_lines_for_sport(sport_id)
    print(f"Fetched lines: {len(lines) if lines else 'None'}")
    if lines:
        await write_lines_to_db(sport_id, lines)
        
    print("Manual ingestion complete.")

if __name__ == "__main__":
    asyncio.run(run())
