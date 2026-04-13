import asyncio
import sys
import os
import logging
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.append(os.getcwd())

from services.odds_mapping import odds_mapper
from schemas.props import PropRecord

def test_mapper():
    dummy_odds = [{
        "id": "test_eid",
        "sport_key": "basketball_nba",
        "sport_title": "NBA",
        "commence_time": "2026-03-21T12:00:00Z",
        "bookmakers": [{
            "key": "fanduel",
            "last_update": "2026-03-21T11:55:00Z",
            "markets": [{
                "key": "player_points",
                "outcomes": [
                    {"name": "Over", "description": "LeBron James", "price": -110, "point": 25.5},
                    {"name": "Under", "description": "LeBron James", "price": -110, "point": 25.5}
                ]
            }]
        }]
    }]
    
    metadata_map = {
        "test_eid": {
            "home_team": "Lakers",
            "away_team": "Warriors",
            "game_time": datetime.now(timezone.utc)
        }
    }
    
    records = odds_mapper.map_theodds_props_to_records(dummy_odds, metadata_map, "basketball_nba")
    print(f"TEST RESULTS: Records count: {len(records)}")
    if records:
        print(f"FIRST RECORD: {records[0]}")

if __name__ == "__main__":
    test_mapper()
