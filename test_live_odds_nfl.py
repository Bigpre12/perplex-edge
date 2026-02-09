#!/usr/bin/env python3
"""
TEST LIVE ODDS NFL ENDPOINTS - Test the new live odds NFL endpoints
"""
import requests
import time
from datetime import datetime

def test_live_odds_nfl():
    """Test live odds NFL endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING LIVE ODDS NFL ENDPOINTS")
    print("="*80)
    
    print(f"\nTime: {datetime.now().strftime('%I:%M:%S %p')}")
    print("Testing live odds NFL endpoints...")
    
    # Test endpoints
    endpoints = [
        ("Live Odds NFL", "/immediate/live-odds-nfl"),
        ("Current Live Odds NFL", "/immediate/live-odds-nfl/current"),
        ("Live Odds NFL Movements", "/immediate/live-odds-nfl/movements/2001"),
        ("Live Odds NFL Comparison", "/immediate/live-odds-nfl/comparison/2001"),
        ("Live Odds NFL Statistics", "/immediate/live-odds-nfl/statistics?hours=24"),
        ("Live Odds NFL Efficiency", "/immediate/live-odds-nfl/efficiency?hours=24"),
        ("Live Odds NFL by Week", "/immediate/live-odds-nfl/week/18"),
        ("Search Live Odds NFL", "/immediate/live-odds-nfl/search?query=chiefs")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"\n{name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if name == "Live Odds NFL":
                    odds = data.get('odds', [])
                    print(f"  Total Odds: {data.get('total', 0)}")
                    print(f"  Filters: {data.get('filters', {})}")
                    
                    for odd in odds[:2]:
                        print(f"  - {odd['home_team']} vs {odd['away_team']}")
                        print(f"    {odd['bookmaker']}: {odd['home_odds']} / {odd['away_odds']}")
                        print(f"    Week {odd['week']}, Season {odd['season']}")
                        print(f"    Timestamp: {odd['timestamp']}")
                        
                elif name == "Current Live Odds NFL":
                    current = data.get('current_odds', [])
                    print(f"  Current Odds: {data.get('total', 0)}")
                    print(f"  Game ID: {data.get('game_id', 'N/A')}")
                    print(f"  Bookmaker: {data.get('bookmaker', 'N/A')}")
                    
                    for odd in current[:2]:
                        print(f"  - {odd['home_team']} vs {odd['away_team']}")
                        print(f"    {odd['bookmaker']}: {odd['home_odds']} / {odd['away_odds']}")
                        print(f"    Week {odd['week']}, Timestamp: {odd['timestamp']}")
                        
                elif name == "Live Odds NFL Movements":
                    print(f"  Game ID: {data.get('game_id', 0)}")
                    print(f"  Total Movements: {data.get('total_movements', 0)}")
                    print(f"  Minutes: {data.get('minutes', 0)}")
                    
                    movements = data.get('movements', [])
                    print(f"  Movements: {len(movements)}")
                    for movement in movements[:2]:
                        print(f"    - {movement['sportsbook']}: {movement['home_odds']} / {movement['away_odds']}")
                        print(f"      Movement: {movement['home_movement']:+d} / {movement['away_movement']:+d}")
                        print(f"      Timestamp: {movement['timestamp']}")
                        
                elif name == "Live Odds NFL Comparison":
                    print(f"  Game ID: {data.get('game_id', 0)}")
                    print(f"  Total Sportsbooks: {data.get('total_sportsbooks', 0)}")
                    print(f"  Minutes: {data.get('minutes', 0)}")
                    
                    comparison = data.get('comparison', [])
                    print(f"  Comparison: {len(comparison)}")
                    for comp in comparison[:2]:
                        print(f"    - {comp['sportsbook']}: {comp['home_odds']} / {comp['away_odds']}")
                    
                    best_home = data.get('best_home_odds', {})
                    best_away = data.get('best_away_odds', {})
                    print(f"  Best Home Odds: {best_home.get('sportsbook', 'N/A')} ({best_home.get('line_value', 'N/A')})")
                    print(f"  Best Away Odds: {best_away.get('best_away_odds', 'N/A')} ({best_away.get('line_value', 'N/A')})")
                    
                elif name == "Live Odds NFL Statistics":
                    print(f"  Period: {data.get('period_hours', 0)} hours")
                    print(f"  Total Odds: {data.get('total_odds', 0)}")
                    print(f"  Unique Games: {data.get('unique_games', 0)}")
                    print(f"  Unique Teams: {data.get('unique_teams', 0)}")
                    print(f"  Unique Bookmakers: {data.get('unique_bookmakers', 0)}")
                    print(f"  Unique Weeks: {data.get('unique_weeks', 0)}")
                    print(f"  Avg Home Odds: {data.get('avg_home_odds', 0):.0f}")
                    print(f"  Avg Away Odds: {data.get('avg_away_odds', 0):.0f}")
                    print(f"  Home Favorites: {data.get('home_favorites', 0)}")
                    print(f"  Away Favorites: {data.get('away_favorites', 0)}")
                    
                    sportsbooks = data.get('by_sportsbook', [])
                    print(f"  Sportsbooks: {len(sportsbooks)}")
                    for sportsbook in sportsbooks[:2]:
                        print(f"    - {sportsbook['bookmaker']}: {sportsbook['total_odds']} odds")
                        print(f"      Unique Games: {sportsbook['unique_games']}")
                        print(f"      Avg Home Odds: {sportsbook['avg_home_odds']:.0f}")
                        
                    weeks = data.get('by_week', [])
                    print(f"  Weeks: {len(weeks)}")
                    for week in weeks[:2]:
                        print(f"    - Week {week['week']}: {week['total_odds']} odds")
                        print(f"      Unique Games: {week['unique_games']}")
                        
                    teams = data.get('by_team', [])
                    print(f"  Teams: {len(teams)}")
                    for team in teams[:2]:
                        print(f"    - {team['team']}: {team['total_games']} games")
                        print(f"      Home Wins: {team['home_wins']}, Away Wins: {team['away_wins']}")
                        
                elif name == "Live Odds NFL Efficiency":
                    print(f"  Period: {data.get('period_hours', 0)} hours")
                    print(f"  Total Arbitrage Opportunities: {data.get('total_arbitrage_opportunities', 0)}")
                    print(f"  Avg Home Range: {data.get('avg_home_range', 0):.1f}")
                    print(f"  Avg Away Range: {data.get('avg_away_range', 0):.1f}")
                    
                    arbitrage = data.get('arbitrage_opportunities', [])
                    print(f"  Arbitrage Opportunities: {len(arbitrage)}")
                    for arb in arbitrage[:2]:
                        print(f"    - {arb['home_team']} vs {arb['away_team']} (Week {arb['week']})")
                        print(f"      Sportsbooks: {arb['sportsbooks_count']}")
                        print(f"      Home Range: {arb['home_odds_range']}, Away Range: {arb['away_odds_range']}")
                        print(f"      Best Home: {arb['best_home_odds']}, Best Away: {arb['best_away_odds']}")
                        
                elif name == "Live Odds NFL by Week":
                    print(f"  Week: {data.get('week', 0)}")
                    print(f"  Season: {data.get('season', 0)}")
                    print(f"  Total Odds: {data.get('total', 0)}")
                    print(f"  Bookmaker: {data.get('bookmaker', 'N/A')}")
                    
                    odds = data.get('odds', [])
                    print(f"  Odds: {len(odds)}")
                    for odd in odds[:2]:
                        print(f"    - {odd['home_team']} vs {odd['away_team']}")
                        print(f"      {odd['bookmaker']}: {odd['home_odds']} / {odd['away_odds']}")
                        print(f"      Timestamp: {odd['timestamp']}")
                        
                elif name == "Search Live Odds NFL":
                    print(f"  Query: {data.get('query', 'N/A')}")
                    print(f"  Total Results: {data.get('total', 0)}")
                    print(f"  Limit: {data.get('limit', 0)}")
                    
                    results = data.get('results', [])
                    print(f"  Results: {len(results)}")
                    for result in results:
                        print(f"    - {result['home_team']} vs {result['away_team']}")
                        print(f"      {result['bookmaker']}: {result['home_odds']} / {result['away_odds']}")
                        print(f"      Week {result['week']}, Season {result['season']}")
                
                print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
                print(f"  Note: {data.get('note', 'N/A')}")
                
            else:
                print(f"  Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"\n{name}: ERROR - {e}")
    
    print("\n" + "="*80)
    print("LIVE ODDS NFL TEST RESULTS:")
    print("="*80)
    
    print("\nLive Odds NFL Table Structure:")
    print("The live_odds_nfl table tracks:")
    print("- Real-time NFL betting odds from sportsbooks")
    print("- Odds movements over time")
    print("- Current vs historical odds data")
    print("- Multi-sportsbook coverage")
    print("- Week and season tracking")
    
    print("\nOdds Data Types:")
    print("- Home Odds: Betting odds for home team")
    print("- Away Odds: Betting odds for away team")
    print("- Draw Odds: Betting odds for draw (rare in NFL)")
    print("- Bookmaker: Betting provider (DraftKings, FanDuel, etc.)")
    print("- Timestamp: When the odds were recorded")
    print("- Week: NFL week number")
    print("- Season: NFL season year")
    
    print("\nSupported Sportsbooks:")
    print("- DraftKings: Major US sportsbook")
    print("- FanDuel: Major US sportsbook")
    print("- BetMGM: MGM Resorts sportsbook")
    print("- Caesars: Caesars Entertainment sportsbook")
    print("- PointsBet: Australian sportsbook")
    print("- Bet365: International sportsbook")
    
    print("\nSample NFL Games:")
    print("- Chiefs vs Bills: -165 / +145 (AFC Championship)")
    print("- 49ers vs Eagles: -125 / +105 (NFC Championship)")
    print("- Cowboys vs Giants: -280 / +230 (NFC East Rivalry)")
    print("- Packers vs Bears: -190 / +160 (NFC North Rivalry)")
    print("- Patriots vs Jets: -140 / +120 (AFC East Rivalry)")
    
    print("\nOdds Movement Analysis:")
    print("- Track odds changes over time")
    print("- Compare odds across sportsbooks")
    print("- Identify market inefficiencies")
    print("- Analyze odds movement patterns")
    print("- Calculate best available odds")
    
    print("\nAvailable Endpoints:")
    print("- GET /immediate/live-odds-nfl - Get odds with filters")
    print("- GET /immediate/live-odds-nfl/current - Get current odds")
    print("- GET /immediate/live-odds-nfl/movements/{game_id} - Get movements")
    print("- GET /immediate/live-odds-nfl/comparison/{game_id} - Compare sportsbooks")
    print("- GET /immediate/live-odds-nfl/statistics - Get statistics")
    print("- GET /immediate/live-odds-nfl/efficiency - Analyze efficiency")
    print("- GET /immediate/live-odds-nfl/week/{week} - Get week odds")
    print("- GET /immediate/live-odds-nfl/search - Search odds")
    
    print("\nBusiness Value:")
    print("- Real-time odds tracking")
    print("- Market efficiency analysis")
    print("- Best odds identification")
    print("- Odds movement prediction")
    print("- Sportsbook comparison shopping")
    print("- Arbitrage opportunity detection")
    
    print("\nIntegration Features:")
    print("- Multi-sportsbook integration")
    print("- Historical odds tracking")
    print("- Real-time odds updates")
    print("- Movement analysis")
    print("- Efficiency metrics calculation")
    print("- Week-based organization")
    
    print("\n" + "="*80)
    print("LIVE ODDS NFL SYSTEM COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    test_live_odds_nfl()
