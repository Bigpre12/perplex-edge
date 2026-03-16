import asyncio
import json
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "apps", "api", "src"))
os.environ["DEVELOPMENT_MODE"] = "1"

from jobs.ingestion_service import transform_odds_api_props
from services.brain_odds_scout import brain_odds_scout

async def seed():
    print("🌱 Seeding database from raw_props.json...")
    mock_file = "apps/api/data/raw_props.json"
    if not os.path.exists(mock_file):
        print(f"❌ Mock file not found at {mock_file}")
        return

    with open(mock_file, "r") as f:
        data = json.load(f)

    # Handle if data is a single dict or a list
    events = [data] if isinstance(data, dict) else data
    
    for event in events:
        if not isinstance(event, dict):
            print(f"⚠️ Skipping invalid event: {event}")
            continue
            
        sport_key = event.get("sport_key", "basketball_nba")
        home = event.get("home_team", "Home Team")
        away = event.get("away_team", "Away Team")
        
        print(f"Ingesting: {home} vs {away} ({sport_key})")
        # transform_odds_api_props expects (odds_events_list, game_info_dict, home, away)
        transformed = transform_odds_api_props([event], event, home, away)
        if transformed:
            print(f"✅ Transformed {len(transformed)} prop lines. Persisting...")
            await brain_odds_scout.analyze_and_persist(transformed, sport_key)
        else:
            print("❌ Transformation failed or returned no data.")
            
    print("✅ Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed())
