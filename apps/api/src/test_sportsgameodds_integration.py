import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

# Ensure env is loaded
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

from services.sportsgameodds_client import sportsgameodds_client

async def test_integration():
    print("Testing SportsGameOdds V2 Integration...")
    
    # 1. Test Client Availability
    if not sportsgameodds_client.available:
        print("FAIL: SportsGameOdds API key not found in environment.")
        return

    print(f"SUCCESS: API Key found: {sportsgameodds_client.api_key[:5]}...")

    # 2. Test Fetching NBA Events (v2)
    print("\nTesting NBA Events Fetch (v2)...")
    try:
        events = await sportsgameodds_client.get_events(league_id="NBA", odds_available=True)
        if events:
            print(f"SUCCESS: Fetched {len(events)} NBA events via SportsGameOdds V2")
            for i, e in enumerate(events[:3]):
                print(f"  - {e['away_team_name']} @ {e['home_team_name']} ({e['status']})")
        else:
            print("FAIL: No events returned. Check key/leagueID/oddsAvailable.")
    except Exception as e:
        print(f"ERROR during fetch: {e}")

    # 3. Test Fetching Teams (v2)
    print("\nTesting Teams Fetch (v2)...")
    try:
        teams = await sportsgameodds_client.get_teams(league_id="NBA")
        if teams:
            print(f"SUCCESS: Fetched {len(teams)} NBA teams via SportsGameOdds V2")
            for t in teams[:3]:
                print(f"  - {t.get('name', 'Unknown')}")
        else:
            print("FAIL: No teams returned.")
    except Exception as e:
        print(f"ERROR during teams fetch: {e}")

    # 4. Test Fetching Players (v2)
    print("\nTesting Players Fetch (v2)...")
    try:
        players = await sportsgameodds_client.get_players(league_id="NBA")
        if players:
            print(f"SUCCESS: Fetched {len(players)} NBA players via SportsGameOdds V2")
            for p in players[:3]:
                print(f"  - {p.get('name', 'Unknown')}")
        else:
            print("FAIL: No players returned.")
    except Exception as e:
        print(f"ERROR during players fetch: {e}")

    # 5. Test Fetching All Sports (v2)
    print("\nTesting All Sports Fetch (v2)...")
    try:
        sports = await sportsgameodds_client.get_sports()
        if sports:
            print(f"SUCCESS: Fetched {len(sports)} sports/leagues via SportsGameOdds V2")
            for s in sports[:5]:
                print(f"  - {s.get('name', s.get('leagueName', 'Unknown'))} (ID: {s.get('id', s.get('leagueID', 'N/A'))})")
        else:
            print("FAIL: No sports returned.")
    except Exception as e:
        print(f"ERROR during sports fetch: {e}")

    # 6. Test Fetching All Leagues (v2)
    print("\nTesting All Leagues Fetch (v2)...")
    try:
        leagues = await sportsgameodds_client.get_leagues()
        if leagues:
            print(f"SUCCESS: Fetched {len(leagues)} leagues via SportsGameOdds V2")
            for l in leagues[:5]:
                print(f"  - {l.get('name', 'Unknown')} (ID: {l.get('id', 'N/A')})")
        else:
            print("FAIL: No leagues returned.")
    except Exception as e:
        print(f"ERROR during leagues fetch: {e}")

    # 7. Test Fetching Stats (v2)
    print("\nTesting Stats Fetch (v2)...")
    try:
        # Testing with a generic fetch (actual IDs would be needed for a specific test)
        stats = await sportsgameodds_client.get_stats()
        if stats:
            print(f"SUCCESS: Fetched {len(stats)} stats entries via SportsGameOdds V2")
        else:
            print("INFO: No stats returned (likely requires specific eventID/playerID).")
    except Exception as e:
        print(f"ERROR during stats fetch: {e}")

    # 8. Test Fetching Markets (v2)
    print("\nTesting Markets Fetch (v2)...")
    try:
        markets = await sportsgameodds_client.get_markets(league_id="NBA")
        if markets:
            print(f"SUCCESS: Fetched {len(markets)} markets via SportsGameOdds V2")
            for m in markets[:3]:
                print(f"  - {m.get('name', 'Unknown')}")
        else:
            print("FAIL: No markets returned.")
    except Exception as e:
        print(f"ERROR during markets fetch: {e}")

    # 9. Test Fetching Account Usage (v2)
    print("\nTesting Account Usage Fetch (v2)...")
    try:
        usage = await sportsgameodds_client.get_account_usage()
        if usage:
            print("SUCCESS: Fetched account usage via SportsGameOdds V2")
            print(f"Details: {usage}")
        else:
            print("FAIL: No usage info returned.")
    except Exception as e:
        print(f"ERROR during usage fetch: {e}")

if __name__ == "__main__":
    asyncio.run(test_integration())
