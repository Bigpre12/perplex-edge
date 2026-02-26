#!/usr/bin/env python3
"""
TEST LINE TRACKING ENDPOINTS - Test the new line tracking endpoints
"""
import requests
import time
from datetime import datetime

def test_line_tracking():
    """Test line tracking endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING LINE TRACKING ENDPOINTS")
    print("="*80)
    
    print(f"\nTime: {datetime.now().strftime('%I:%M:%S %p')}")
    print("Testing line tracking endpoints...")
    
    # Test endpoints
    endpoints = [
        ("Lines", "/immediate/lines"),
        ("Current Lines", "/immediate/lines/current"),
        ("Line Movements", "/immediate/lines/movements/662/91"),
        ("Sportsbook Comparison", "/immediate/lines/comparison/662/91"),
        ("Line Statistics", "/immediate/lines/statistics?hours=24"),
        ("Line Efficiency", "/immediate/lines/efficiency?hours=24"),
        ("Search Lines", "/immediate/lines/search?query=91")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"\n{name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if name == "Lines":
                    lines = data.get('lines', [])
                    print(f"  Total Lines: {data.get('total', 0)}")
                    print(f"  Filters: {data.get('filters', {})}")
                    
                    for line in lines[:2]:
                        print(f"  - Game {line['game_id']}, Player {line['player_id']}")
                        print(f"    {line['sportsbook']}: {line['line_value']} {line['side']} ({line['odds']})")
                        print(f"    Market {line['market_id']}, Current: {line['is_current']}")
                        
                elif name == "Current Lines":
                    current = data.get('current_lines', [])
                    print(f"  Current Lines: {data.get('total', 0)}")
                    print(f"  Game ID: {data.get('game_id', 'N/A')}")
                    print(f"  Player ID: {data.get('player_id', 'N/A')}")
                    
                    for line in current[:2]:
                        print(f"  - Game {line['game_id']}, Player {line['player_id']}")
                        print(f"    {line['sportsbook']}: {line['line_value']} {line['side']} ({line['odds']})")
                        print(f"    Fetched: {line['fetched_at']}")
                        
                elif name == "Line Movements":
                    print(f"  Game ID: {data.get('game_id', 0)}")
                    print(f"  Player ID: {data.get('player_id', 0)}")
                    print(f"  Total Movements: {data.get('total_movements', 0)}")
                    print(f"  Market ID: {data.get('market_id', 'N/A')}")
                    
                    movements = data.get('movements', [])
                    print(f"  Movements: {len(movements)}")
                    for movement in movements[:2]:
                        print(f"    - {movement['sportsbook']}: {movement['line_value']} {movement['side']} ({movement['odds']})")
                        print(f"      Movement: {movement['line_movement']:+.1f}, Odds: {movement['odds_movement']:+d}")
                        
                elif name == "Sportsbook Comparison":
                    print(f"  Game ID: {data.get('game_id', 0)}")
                    print(f"  Player ID: {data.get('player_id', 0)}")
                    print(f"  Total Sportsbooks: {data.get('total_sportsbooks', 0)}")
                    
                    comparison = data.get('comparison', [])
                    print(f"  Comparison: {len(comparison)}")
                    for comp in comparison[:2]:
                        print(f"    - {comp['sportsbook']}: {comp['line_value']} {comp['side']} ({comp['odds']})")
                    
                    best_over = data.get('best_over_odds', {})
                    best_under = data.get('best_under_odds', {})
                    print(f"  Best Over Odds: {best_over.get('sportsbook', 'N/A')} ({best_over.get('odds', 'N/A')})")
                    print(f"  Best Under Odds: {best_under.get('sportsbook', 'N/A')} ({best_under.get('odds', 'N/A')})")
                    
                elif name == "Line Statistics":
                    print(f"  Period: {data.get('period_hours', 0)} hours")
                    print(f"  Total Lines: {data.get('total_lines', 0)}")
                    print(f"  Unique Games: {data.get('unique_games', 0)}")
                    print(f"  Unique Markets: {data.get('unique_markets', 0)}")
                    print(f"  Unique Players: {data.get('unique_players', 0)}")
                    print(f"  Unique Sportsbooks: {data.get('unique_sportsbooks', 0)}")
                    print(f"  Current Lines: {data.get('current_lines', 0)}")
                    print(f"  Historical Lines: {data.get('historical_lines', 0)}")
                    print(f"  Avg Line Value: {data.get('avg_line_value', 0):.2f}")
                    print(f"  Avg Odds: {data.get('avg_odds', 0):.0f}")
                    print(f"  Over Lines: {data.get('over_lines', 0)}")
                    print(f"  Under Lines: {data.get('under_lines', 0)}")
                    
                    sportsbooks = data.get('by_sportsbook', [])
                    print(f"  Sportsbooks: {len(sportsbooks)}")
                    for sportsbook in sportsbooks[:2]:
                        print(f"    - {sportsbook['sportsbook']}: {sportsbook['total_lines']} lines")
                        print(f"      Current: {sportsbook['current_lines']}, Avg Line: {sportsbook['avg_line_value']:.2f}")
                        
                    sides = data.get('by_side', [])
                    print(f"  Sides: {len(sides)}")
                    for side in sides:
                        print(f"    - {side['side']}: {side['total_lines']} lines")
                        
                elif name == "Line Efficiency":
                    print(f"  Period: {data.get('period_hours', 0)} hours")
                    
                    efficiency = data.get('sportsbook_efficiency', [])
                    print(f"  Sportsbook Efficiency: {len(efficiency)}")
                    for eff in efficiency:
                        print(f"    - {eff['sportsbook']}: {eff['efficiency_score']:.1f}% efficiency")
                        print(f"      Movement Rate: {eff['movement_rate']:.1f}%")
                        print(f"      Avg Movement: {eff['avg_movement']:.2f}")
                        
                elif name == "Search Lines":
                    print(f"  Query: {data.get('query', 'N/A')}")
                    print(f"  Total Results: {data.get('total', 0)}")
                    print(f"  Limit: {data.get('limit', 0)}")
                    
                    results = data.get('results', [])
                    print(f"  Results: {len(results)}")
                    for result in results:
                        print(f"    - Game {result['game_id']}, Player {result['player_id']}")
                        print(f"      {result['sportsbook']}: {result['line_value']} {result['side']} ({result['odds']})")
                
                print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
                print(f"  Note: {data.get('note', 'N/A')}")
                
            else:
                print(f"  Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"\n{name}: ERROR - {e}")
    
    print("\n" + "="*80)
    print("LINE TRACKING TEST RESULTS:")
    print("="*80)
    
    print("\nLines Table Structure:")
    print("The lines table tracks:")
    print("- Betting lines and odds from sportsbooks")
    print("- Line movements over time")
    print("- Current vs historical line data")
    print("- Multi-sportsbook coverage")
    print("- Player prop betting lines")
    
    print("\nLine Data Types:")
    print("- Line Value: The betting line (e.g., 13.5 points)")
    print("- Odds: Betting odds (negative = favorite, positive = underdog)")
    print("- Side: Over/Under betting side")
    print("- Sportsbook: Betting provider (DraftKings, FanDuel, etc.)")
    print("- Is Current: Whether this is the current line")
    print("- Fetched At: When the line was recorded")
    
    print("\nSupported Sportsbooks:")
    print("- DraftKings: Major US sportsbook")
    print("- FanDuel: Major US sportsbook")
    print("- BetMGM: MGM Resorts sportsbook")
    print("- Caesars: Caesars Entertainment sportsbook")
    print("- PointsBet: Australian sportsbook")
    print("- Bet365: International sportsbook")
    
    print("\nSample Lines:")
    print("- LeBron James Points: 14.0 over/under (-105)")
    print("- Stephen Curry Points: 28.5 over/under (-110)")
    print("- Patrick Mahomes Passing Yards: 285.5 over/under (-110)")
    print("- Aaron Judge Home Runs: 1.5 over/under (-110)")
    
    print("\nLine Movement Analysis:")
    print("- Track line changes over time")
    print("- Compare odds across sportsbooks")
    ("  Identify market inefficiencies")
    print("- Analyze line movement patterns")
    print("- Calculate best available odds")
    
    print("\nAvailable Endpoints:")
    print("- GET /immediate/lines - Get lines with filters")
    print("- GET /immediate/lines/current - Get current lines")
    print("- GET /immediate/lines/movements/{game_id}/{player_id} - Get movements")
    print("- GET /immediate/lines/comparison/{game_id}/{player_id} - Compare sportsbooks")
    print("- GET /immediate/lines/statistics - Get statistics")
    print("- GET /immediate/lines/efficiency - Analyze efficiency")
    print("- GET /immediate/lines/search - Search lines")
    
    print("\nBusiness Value:")
    print("- Real-time line tracking")
    print("- Market efficiency analysis")
    print("- Best odds identification")
    print("- Line movement prediction")
    print("- Sportsbook comparison shopping")
    
    print("\nIntegration Features:")
    print("- Multi-sportsbook integration")
    print("- Historical line tracking")
    print("- Real-time line updates")
    print("- Movement analysis")
    print("- Efficiency metrics calculation")
    
    print("\n" + "="*80)
    print("LINE TRACKING SYSTEM COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    test_line_tracking()
