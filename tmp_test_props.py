import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "apps", "api", "src"))

from api.immediate_working import get_working_player_props_immediate
from database import SessionLocal
from models.props import PropLine, PropOdds

async def test_endpoint():
    print("Testing /working-player-props endpoint...")
    # Mocking Dependencies for standalone run if needed
    try:
        r = await get_working_player_props_immediate(sport_key="basketball_nba", limit=10)
        items = r.get("items", [])
        print(f"Total Props found: {len(items)}")
        if items:
            print(f"First Prop: {items[0]['player']} - {items[0]['market']['stat_type']} - {items[0]['line_value']}")
        else:
            print("No items found. Response:", r)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())
