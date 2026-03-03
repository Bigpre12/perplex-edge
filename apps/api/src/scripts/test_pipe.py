import asyncio
import os
import sys
import logging

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from services.odds.fetchers import fetch_props_for_sport
from jobs.ingestion_service import transform_odds_api_props
from app.antigravity_engine import apply_antigravity_filter
from services.brain_odds_scout import brain_odds_scout

logging.basicConfig(level=logging.INFO)

async def test_pipeline():
    sport_id = 30 # NBA
    print(f"--- Testing Pipeline for Sport ID {sport_id} ---")
    
    # 1. Fetch
    data = await fetch_props_for_sport(sport_id)
    print(f"STEP 1: API Fetch returned {len(data) if data else 0} events")
    if not data:
        return

    # 2. Transform
    all_transformed = []
    for event in data:
        t = transform_odds_api_props([event], event)
        all_transformed.extend(t)
    print(f"STEP 2: Transformation produced {len(all_transformed)} props")
    if not all_transformed:
        return

    # 3. Filter
    filtered = await apply_antigravity_filter(all_transformed)
    print(f"STEP 3: Antigravity Filter passed {len(filtered)} props")
    
    # 4. Persistence
    if all_transformed:
        print(f"STEP 4: Attempting to persist {len(all_transformed)} raw props to DB...")
        await brain_odds_scout.analyze_and_persist(all_transformed, "basketball_nba")
        print("STEP 4: Persistence call complete.")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
