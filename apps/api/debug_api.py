import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("THE_ODDS_API_KEY") or os.getenv("ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4"
REGIONS = "us"
SPORT = "basketball_nba"

async def debug_props():
    if not API_KEY:
        print("Error: No API key found")
        return

    async with httpx.AsyncClient() as client:
        # 1. Get events
        print(f"Fetching events for {SPORT}...")
        res = await client.get(f"{BASE_URL}/sports/{SPORT}/events", params={"apiKey": API_KEY})
        if res.status_code != 200:
            print(f"Error fetching events: {res.status_code} {res.text}")
            return
        
        events = res.json()
        if not events:
            print("No events found")
            return
        
        # Try to find a game with props
        for event in events[:5]:
            event_id = event["id"]
            print(f"\nChecking event: {event['home_team']} vs {event['away_team']} ({event_id})")

            # 2. Get props
            from config.sports_config import PLAYER_PROP_MARKETS
            markets = PLAYER_PROP_MARKETS.get(SPORT, ["player_points"])
            print(f"Fetching props for markets: {markets[:10]}...")
            res = await client.get(
                f"{BASE_URL}/sports/{SPORT}/events/{event_id}/odds",
                params={
                    "apiKey": API_KEY,
                    "regions": REGIONS,
                    "markets": ",".join(markets[:10]),
                    "oddsFormat": "american",
                }
            )
            
            if res.status_code != 200:
                print(f"Error fetching props: {res.status_code} {res.text}")
                continue
            
            data = res.json()
            bookmakers = data.get("bookmakers", [])
            print(f"Found {len(bookmakers)} bookmakers: {[b['key'] for b in bookmakers]}")
            
            all_markets = set()
            for book in bookmakers:
                for market in book.get("markets", []):
                    all_markets.add(market["key"])
            
            print(f"Available markets across all books: {sorted(list(all_markets))}")
            
            if bookmakers:
                # Just show first book's markets
                first_book = bookmakers[0]
                print(f"\nDetail for {first_book['title']}:")
                for market in first_book.get("markets", []):
                    outcomes = market.get("outcomes", [])
                    print(f"  - {market['key']}: {len(outcomes)} outcomes (e.g., {outcomes[0]['description'] if outcomes else 'N/A'})")
            
            if all_markets:
                break # Found one with data

if __name__ == "__main__":
    # Add src to path for config import
    import sys
    sys.path.append(os.path.join(os.getcwd(), "src"))
    asyncio.run(debug_props())
