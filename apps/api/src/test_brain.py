import asyncio
import os
import sys

# Add src to path
sys.path.append('src')

from services.brain_service import brain_service

async def test():
    print("Testing score_and_recommend...")
    mock_props = [
        {
            "player_name": "LeBron James",
            "stat_type": "Points",
            "edge": 0.05,
            "is_sharp": True,
            "side": "over"
        }
    ]
    try:
        result = await brain_service.score_and_recommend(mock_props)
        print("Success!")
        print(result)
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
