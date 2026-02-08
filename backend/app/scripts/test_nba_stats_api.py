"""
Test script for NBA Stats API - verify it can fetch actual player stats
Run this after Railway deployment to test grading functionality
"""

import asyncio
import sys
from datetime import datetime, timezone

sys.path.append('/app')

async def test_nba_stats_api():
    """Test NBA Stats API with a known player and game."""
    
    print("TESTING NBA STATS API INTEGRATION")
    print("=" * 50)
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print()
    
    try:
        from app.services.results_api import nba_stats_api
        
        # Test with a well-known player
        test_cases = [
            ("LeBron James", "2026-02-06"),  # Yesterday's game
            ("Kevin Durant", "2026-02-06"),
            ("Stephen Curry", "2026-02-06"),
        ]
        
        for player_name, game_date in test_cases:
            print(f"Testing: {player_name} on {game_date}")
            
            try:
                stats = await nba_stats_api.fetch_player_game_stats(player_name, game_date)
                
                if stats:
                    print(f"  ✅ SUCCESS:")
                    print(f"     Points: {stats.get('pts')}")
                    print(f"     Rebounds: {stats.get('reb')}")
                    print(f"     Assists: {stats.get('ast')}")
                    print(f"     Minutes: {stats.get('min')}")
                else:
                    print(f"  ❌ No stats found (game may not have been played)")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
            
            print()
        
        print("TEST COMPLETE")
        print()
        print("Next steps:")
        print("1. If tests pass: Grading pipeline should work")
        print("2. If tests fail: Check NBA Stats API availability")
        print("3. Verify with actual games from today (2026-02-07)")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_nba_stats_api())
