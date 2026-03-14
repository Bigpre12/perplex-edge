import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Add src to path
import sys
sys.path.append(os.path.join(os.getcwd(), "src"))

from services.props_service import get_all_props

async def test_get_all_props():
    print("Fetching all props for NBA (Grouped)...")
    props = await get_all_props(sport_filter="basketball_nba")
    print(f"Total market cards: {len(props)}")
    
    if props:
        print("\nFirst 10 Market Cards:")
        for p in props[:10]:
            over = p.get('best_over')
            under = p.get('best_under')
            over_str = f"Over {over['line']} @ {over['odds']} ({over['book']})" if over else "N/A"
            under_str = f"Under {under['line']} @ {under['odds']} ({under['book']})" if under else "N/A"
            print(f"- {p['player_name']} | {p['stat_type']} | {over_str} / {under_str}")
            
        stats = {}
        for p in props:
            stats[p['stat_type']] = stats.get(p['stat_type'], 0) + 1
            
        print("\nMarket Distribution (Cards):")
        for market, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            print(f"- {market}: {count}")

if __name__ == "__main__":
    asyncio.run(test_get_all_props())
