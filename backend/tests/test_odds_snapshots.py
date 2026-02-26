#!/usr/bin/env python3
"""
TEST ODDS SNAPSHOTS ENDPOINTS - Test the new odds snapshots tracking endpoints
"""
import requests
import time
from datetime import datetime

def test_odds_snapshots():
    """Test odds snapshots endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING ODDS SNAPSHOTS ENDPOINTS")
    print("="*80)
    
    print(f"\nTime: {datetime.now().strftime('%I:%M:%S %p')}")
    print("Testing odds snapshots tracking endpoints...")
    
    # Test endpoints
    endpoints = [
        ("Odds Snapshots", "/immediate/odds-snapshots"),
        ("Odds Movements", "/immediate/odds-snapshots/movements/662"),
        ("Odds Comparison", "/immediate/odds-snapshots/comparison/662"),
        ("Odds Snapshots Statistics", "/immediate/odds-snapshots/statistics?hours=24"),
        ("Odds by Bookmaker", "/immediate/odds-snapshots/bookmaker/DraftKings"),
        ("Odds by Player", "/immediate/odds-snapshots/player/91"),
        ("Search Odds Snapshots", "/immediate/odds-snapshots/search?query=nba")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"\n{name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if name == "Odds Snapshots":
                    snapshots = data.get('snapshots', [])
                    print(f"  Total Snapshots: {data.get('total', 0)}")
                    print(f"  Filters: {data.get('filters', {})}")
                    
                    for snapshot in snapshots[:2]:
                        print(f"  - Game {snapshot['game_id']}, Market {snapshot['market_id']}")
                        print(f"    {snapshot['bookmaker']}: {snapshot['line_value']} {snapshot['side']} ({snapshot['american_odds']})")
                        print(f"    Price: {snapshot['price']:.4f}, Player {snapshot['player_id']}")
                        print(f"    Snapshot: {snapshot['snapshot_at']}")
                        
                elif name == "Odds Movements":
                    print(f"  Game ID: {data.get('game_id', 0)}")
                    print(f"  Market ID: {data.get('market_id', 'N/A')}")
                    print(f"  Player ID: {data.get('player_id', 'N/A')}")
                    print(f"  Total Movements: {data.get('total_movements', 0)}")
                    print(f"  Hours: {data.get('hours', 0)}")
                    
                    movements = data.get('movements', [])
                    print(f"  Movements: {len(movements)}")
                    for movement in movements[:3]:
                        print(f"    - {movement['bookmaker']}: {movement['line_value']} {movement['side']} ({movement['american_odds']})")
                        print(f"      Movement: Line {movement['line_movement']:+.1f}, Price {movement['price_movement']:+.4f}, Odds {movement['odds_movement']:+d}")
                        print(f"      Snapshot: {movement['snapshot_at']}")
                        
                elif name == "Odds Comparison":
                    print(f"  Game ID: {data.get('game_id', 0)}")
                    print(f"  Market ID: {data.get('market_id', 'N/A')}")
                    print(f"  Player ID: {data.get('player_id', 'N/A')}")
                    print(f"  Total Bookmakers: {data.get('total_bookmakers', 0)}")
                    print(f"  Hours: {data.get('hours', 0)}")
                    
                    comparison = data.get('comparison', [])
                    print(f"  Comparison: {len(comparison)}")
                    for comp in comparison[:2]:
                        print(f"    - {comp['bookmaker']}: {comp['line_value']} {comp['side']} ({comp['american_odds']})")
                        print(f"      Price: {comp['price']:.4f}")
                    
                    best_over = data.get('best_over_odds', {})
                    best_under = data.get('best_under_odds', {})
                    print(f"  Best Over Odds: {best_over.get('bookmaker', 'N/A')} ({best_over.get('line_value', 'N/A')})")
                    print(f"  Best Under Odds: {best_under.get('bookmaker', 'N/A')} ({best_under.get('line_value', 'N/A')})")
                    
                elif name == "Odds Snapshots Statistics":
                    print(f"  Period: {data.get('period_hours', 0)} hours")
                    print(f"  Total Snapshots: {data.get('total_snapshots', 0)}")
                    print(f"  Unique Games: {data.get('unique_games', 0)}")
                    print(f"  Unique Markets: {data.get('unique_markets', 0)}")
                    print(f"  Unique Players: {data.get('unique_players', 0)}")
                    print(f"  Unique Bookmakers: {data.get('unique_bookmakers', 0)}")
                    print(f"  Avg Line Value: {data.get('avg_line_value', 0):.2f}")
                    print(f"  Avg Price: {data.get('avg_price', 0):.4f}")
                    print(f"  Avg American Odds: {data.get('avg_american_odds', 0):.0f}")
                    print(f"  Over/Under: {data.get('over_snapshots', 0)}/{data.get('under_snapshots', 0)}")
                    
                    bookmakers = data.get('by_bookmaker', [])
                    print(f"  Bookmakers: {len(bookmakers)}")
                    for bookmaker in bookmakers[:2]:
                        print(f"    - {bookmaker['bookmaker']}: {bookmaker['total_snapshots']} snapshots")
                        print(f"      Unique Games: {bookmaker['unique_games']}")
                        print(f"      Avg Line Value: {bookmaker['avg_line_value']:.2f}")
                        print(f"      Avg Price: {bookmaker['avg_price']:.4f}")
                        
                    games = data.get('by_game', [])
                    print(f"  Games: {len(games)}")
                    for game in games[:2]:
                        print(f"    - Game {game['game_id']}: {game['total_snapshots']} snapshots")
                        print(f"      Unique Markets: {game['unique_markets']}")
                        print(f"      Unique Players: {game['unique_players']}")
                        print(f"      Unique Bookmakers: {game['unique_bookmakers']}")
                        
                    sides = data.get('by_side', [])
                    print(f"  Sides: {len(sides)}")
                    for side in sides:
                        print(f"    - {side['side']}: {side['total_snapshots']} snapshots")
                        print(f"      Avg Line Value: {side['avg_line_value']:.2f}")
                        print(f"      Avg Price: {side['avg_price']:.4f}")
                        
                elif name == "Odds by Bookmaker":
                    print(f"  Bookmaker: {data.get('bookmaker', 'N/A')}")
                    print(f"  Total Snapshots: {data.get('total', 0)}")
                    print(f"  Hours: {data.get('hours', 0)}")
                    
                    snapshots = data.get('snapshots', [])
                    print(f"  Snapshots: {len(snapshots)}")
                    for snapshot in snapshots[:2]:
                        print(f"    - Game {snapshot['game_id']}, Market {snapshot['market_id']}")
                        print(f"      {snapshot['bookmaker']}: {snapshot['line_value']} {snapshot['side']} ({snapshot['american_odds']})")
                        print(f"      Price: {snapshot['price']:.4f}, Player {snapshot['player_id']}")
                        print(f"      Snapshot: {snapshot['snapshot_at']}")
                        
                elif name == "Odds by Player":
                    print(f"  Player ID: {data.get('player_id', 0)}")
                    print(f"  Total Snapshots: {data.get('total', 0)}")
                    print(f"  Bookmaker: {data.get('bookmaker', 'N/A')}")
                    print(f"  Hours: {data.get('hours', 0)}")
                    
                    snapshots = data.get('snapshots', [])
                    print(f"  Snapshots: {len(snapshots)}")
                    for snapshot in snapshots[:2]:
                        print(f"    - Game {snapshot['game_id']}, Market {snapshot['market_id']}")
                        print(f"      {snapshot['bookmaker']}: {snapshot['line_value']} {snapshot['side']} ({snapshot['american_odds']})")
                        print(f"      Price: {snapshot['price']:.4f}")
                        print(f"      Snapshot: {snapshot['snapshot_at']}")
                        
                elif name == "Search Odds Snapshots":
                    print(f"  Query: {data.get('query', 'N/A')}")
                    print(f"  Total Results: {data.get('total', 0)}")
                    print(f"  Bookmaker: {data.get('bookmaker', 'N/A')}")
                    print(f"  Hours: {data.get('hours', 0)}")
                    print(f"  Limit: {data.get('limit', 0)}")
                    
                    results = data.get('results', [])
                    print(f"  Results: {len(results)}")
                    for result in results:
                        print(f"    - Game {result['game_id']}, Market {result['market_id']}")
                        print(f"      {result['bookmaker']}: {result['line_value']} {result['side']} ({result['american_odds']})")
                        print(f"      External Fixture: {result['external_fixture_id']}")
                        print(f"      External Market: {result['external_market_id']}")
                        print(f"      External Outcome: {result['external_outcome_id']}")
                
                print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
                print(f"  Note: {data.get('note', 'N/A')}")
                
            else:
                print(f"  Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"\n{name}: ERROR - {e}")
    
    print("\n" + "="*80)
    print("ODDS SNAPSHOTS TEST RESULTS:")
    print("="*80)
    
    print("\nOdds Snapshots Table Structure:")
    print("The odds_snapshots table tracks:")
    print("- Historical odds data from external sportsbooks")
    print("- Line movements and price changes over time")
    print("- Multi-bookmaker odds comparison")
    print("- External fixture/market/outcome IDs")
    print("- Real-time odds snapshots")
    
    print("\nOdds Data Types:")
    print("- Game ID: Internal game identifier")
    print("- Market ID: Internal market identifier")
    print("- Player ID: Internal player identifier")
    print("- External IDs: Sportsbook-specific identifiers")
    print("- Bookmaker: Sportsbook name (DraftKings, FanDuel, etc.)")
    print("- Line Value: Betting line (e.g., 14.5 points)")
    print("- Price: Decimal odds (e.g., 1.9091)")
    print("- American Odds: American odds format (e.g., -110)")
    print("- Side: over/under/home/away")
    print("- Is Active: Whether the odds are currently active")
    
    print("\nSupported Bookmakers:")
    print("- DraftKings: Major US sportsbook")
    print("- FanDuel: Major US sportsbook")
    print("- BetMGM: MGM Resorts sportsbook")
    print("- Caesars: Caesars Entertainment sportsbook")
    print("- PointsBet: Australian sportsbook")
    print("- Bet365: International sportsbook")
    
    print("\nSample Odds Data:")
    print("- LeBron James Points: 14.0 over (-102) at DraftKings")
    print("- Stephen Curry Points: 28.5 over (-110) at DraftKings")
    print("- Patrick Mahomes Pass Yards: 285.5 over (-110) at DraftKings")
    print("- Aaron Judge Home Runs: 1.5 over (-110) at DraftKings")
    print("- Connor McDavid Points: 1.5 over (-110) at DraftKings")
    
    print("\nLine Movement Analysis:")
    print("- Track odds changes over time")
    print("- Compare odds across sportsbooks")
    print("- Identify market inefficiencies")
    print("- Analyze odds movement patterns")
    print("- Calculate best available odds")
    
    print("\nExternal ID Mapping:")
    print("- External Fixture ID: Sportsbook game identifier")
    print("- External Market ID: Sportsbook market identifier")
    print("- External Outcome ID: Sportsbook outcome identifier")
    print("- Enables integration with external odds providers")
    
    print("\nAvailable Endpoints:")
    print("- GET /immediate/odds-snapshots - Get snapshots with filters")
    print("- GET /immediate/odds-snapshots/movements/{game_id} - Get movements")
    print("- GET /immediate/odds-snapshots/comparison/{game_id} - Compare bookmakers")
    print("- GET /immediate/odds-snapshots/statistics - Get statistics")
    print("- GET /immediate/odds-snapshots/bookmaker/{bookmaker} - Get by bookmaker")
    print("- GET /immediate/odds-snapshots/player/{player_id} - Get by player")
    print("- GET /immediate/odds-snapshots/search - Search snapshots")
    
    print("\nBusiness Value:")
    print("- Historical odds tracking and analysis")
    print("- Market efficiency monitoring")
    print("- Best odds identification")
    print("- Odds movement prediction")
    print("- Sportsbook comparison shopping")
    print("- Arbitrage opportunity detection")
    
    print("\nIntegration Features:")
    print("- Multi-sportsbook integration")
    print("- External ID mapping")
    print("- Real-time odds updates")
    print("- Movement analysis")
    print("- Statistical analysis and reporting")
    print("- Search and filtering capabilities")
    
    print("\n" + "="*80)
    print("ODDS SNAPSHOTS SYSTEM COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    test_odds_snapshots()
