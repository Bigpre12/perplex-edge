#!/usr/bin/env python3
"""
TEST HISTORICAL ODDS NCAAB ENDPOINTS - Test the new NCAA basketball historical odds endpoints
"""
import requests
import time
from datetime import datetime

def test_historical_odds_ncaab():
    """Test NCAA basketball historical odds endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING HISTORICAL ODDS NCAAB ENDPOINTS")
    print("="*80)
    
    print(f"\nTime: {datetime.now().strftime('%I:%M:%S %p')}")
    print("Testing NCAA basketball historical odds endpoints...")
    
    # Test endpoints
    endpoints = [
        ("Historical Odds NCAAB", "/immediate/historical-odds-ncaab"),
        ("Odds by Game", "/immediate/historical-odds-ncaab/game/1001"),
        ("Odds Movements", "/immediate/historical-odds-ncaab/movements/1001"),
        ("Bookmaker Comparison", "/immediate/historical-odds-ncaab/comparison/1001"),
        ("Odds Statistics", "/immediate/historical-odds-ncaab/statistics?days=30"),
        ("Odds Efficiency", "/immediate/historical-odds-ncaab/efficiency?days=30"),
        ("Search Odds", "/immediate/historical-odds-ncaab/search?query=duke")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"\n{name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if name == "Historical Odds NCAAB":
                    odds = data.get('odds', [])
                    print(f"  Total Odds: {data.get('total', 0)}")
                    print(f"  Filters: {data.get('filters', {})}")
                    
                    for odd in odds[:2]:
                        print(f"  - {odd['home_team']} vs {odd['away_team']}")
                        print(f"    Home: {odd['home_odds']}, Away: {odd['away_odds']}")
                        print(f"    Bookmaker: {odd['bookmaker']}, Result: {odd['result']}")
                        print(f"    Snapshot: {odd['snapshot_date']}")
                        
                elif name == "Odds by Game":
                    print(f"  Game ID: {data.get('game_id', 0)}")
                    print(f"  Teams: {data.get('home_team', 'N/A')} vs {data.get('away_team', 'N/A')}")
                    print(f"  Total Snapshots: {data.get('total_snapshots', 0)}")
                    print(f"  Bookmakers: {data.get('bookmakers', [])}")
                    
                    history = data.get('odds_history', [])
                    print(f"  Odds History: {len(history)} snapshots")
                    for snapshot in history[:2]:
                        print(f"    - {snapshot['bookmaker']}: {snapshot['home_odds']}/{snapshot['away_odds']}")
                        
                elif name == "Odds Movements":
                    print(f"  Game ID: {data.get('game_id', 0)}")
                    print(f"  Total Movements: {data.get('total_movements', 0)}")
                    print(f"  Bookmakers: {data.get('bookmakers', [])}")
                    
                    movements = data.get('movements', [])
                    print(f"  Movements: {len(movements)} records")
                    for movement in movements[:2]:
                        print(f"    - {movement['bookmaker']}: {movement['home_odds']} ({movement['home_movement']:+d})")
                        
                elif name == "Bookmaker Comparison":
                    print(f"  Game ID: {data.get('game_id', 0)}")
                    print(f"  Teams: {data.get('home_team', 'N/A')} vs {data.get('away_team', 'N/A')}")
                    print(f"  Total Bookmakers: {data.get('total_bookmakers', 0)}")
                    
                    comparison = data.get('comparison', [])
                    print(f"  Comparison: {len(comparison)} bookmakers")
                    for comp in comparison[:2]:
                        print(f"    - {comp['bookmaker']}: {comp['home_odds']}/{comp['away_odds']}")
                    
                    best_home = data.get('best_home_odds', {})
                    best_away = data.get('best_away_odds', {})
                    print(f"  Best Home Odds: {best_home.get('bookmaker', 'N/A')} ({best_home.get('odds', 'N/A')})")
                    print(f"  Best Away Odds: {best_away.get('bookmaker', 'N/A')} ({best_away.get('odds', 'N/A')})")
                    
                elif name == "Odds Statistics":
                    print(f"  Period: {data.get('period_days', 0)} days")
                    print(f"  Total Odds: {data.get('total_odds', 0)}")
                    print(f"  Unique Games: {data.get('unique_games', 0)}")
                    print(f"  Unique Bookmakers: {data.get('unique_bookmakers', 0)}")
                    print(f"  Home Wins: {data.get('home_wins', 0)}")
                    print(f"  Away Wins: {data.get('away_wins', 0)}")
                    print(f"  Home Win Rate: {data.get('home_win_rate', 0):.1f}%")
                    print(f"  Avg Home Odds: {data.get('avg_home_odds', 0):.1f}")
                    print(f"  Avg Away Odds: {data.get('avg_away_odds', 0):.1f}")
                    
                    bookmakers = data.get('by_bookmaker', [])
                    print(f"  Bookmakers: {len(bookmakers)}")
                    for bookmaker in bookmakers[:2]:
                        print(f"    - {bookmaker['bookmaker']}: {bookmaker['total_odds']} odds")
                        
                elif name == "Odds Efficiency":
                    print(f"  Period: {data.get('period_days', 0)} days")
                    
                    efficiency = data.get('bookmaker_efficiency', [])
                    print(f"  Bookmaker Efficiency: {len(efficiency)} bookmakers")
                    for eff in efficiency[:2]:
                        print(f"    - {eff['bookmaker']}: {eff['overall_accuracy']:.1f}% accuracy")
                        print(f"      Home Edge: {eff['home_edge']:+.1f}%, Away Edge: {eff['away_edge']:+.1f}%")
                        
                elif name == "Search Odds":
                    print(f"  Query: {data.get('query', 'N/A')}")
                    print(f"  Total Results: {data.get('total', 0)}")
                    print(f"  Limit: {data.get('limit', 0)}")
                    
                    results = data.get('results', [])
                    print(f"  Results: {len(results)}")
                    for result in results:
                        print(f"    - {result['home_team']} vs {result['away_team']}")
                        print(f"      Bookmaker: {result['bookmaker']}, Result: {result['result']}")
                
                print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
                print(f"  Note: {data.get('note', 'N/A')}")
                
            else:
                print(f"  Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"\n{name}: ERROR - {e}")
    
    print("\n" + "="*80)
    print("HISTORICAL ODDS NCAAB TEST RESULTS:")
    print("="*80)
    
    print("\nHistorical Odds NCAAB Table Structure:")
    print("The historical_odds_ncaab table tracks:")
    print("- NCAA basketball betting odds history")
    print("- Bookmaker odds snapshots")
    print("- Odds movements over time")
    print("- Game results and outcomes")
    print("- Season and date tracking")
    print("- Team matchup information")
    
    print("\nOdds Data Types:")
    print("- Home Odds: Odds for home team (negative = favorite, positive = underdog)")
    print("- Away Odds: Odds for away team")
    print("- Draw Odds: Odds for draw (rare in basketball)")
    print("- Bookmaker: Betting provider (DraftKings, FanDuel, etc.)")
    print("- Snapshot Date: When odds were recorded")
    print("- Result: Game outcome (home_win, away_win, draw)")
    
    print("\nSupported Bookmakers:")
    print("- DraftKings: Major US sportsbook")
    print("- FanDuel: Major US sportsbook")
    print("- BetMGM: MGM Resorts sportsbook")
    print("- Caesars: Caesars Entertainment sportsbook")
    print("- PointsBet: Australian sportsbook")
    print("- Bet365: International sportsbook")
    
    print("\nSample NCAA Basketball Games:")
    print("- Duke vs North Carolina: Rivalry game")
    print("- Kansas vs Kentucky: Blue blood matchup")
    print("- UCLA vs Gonzaga: West coast powerhouse")
    print("- Michigan vs Ohio State: Big Ten rivalry")
    print("- Arizona vs Oregon: Pac-12 matchup")
    print("- Purdue vs Indiana: Big Ten rivalry")
    print("- Texas vs Baylor: Big 12 matchup")
    print("- Villanova vs UConn: Big East vs Big East")
    
    print("\nOdds Movement Analysis:")
    print("- Track odds changes over time")
    print("- Compare odds across bookmakers")
    print("- Identify betting value opportunities")
    print("- Analyze market efficiency")
    print("- Track line movements")
    
    print("\nAvailable Endpoints:")
    print("- GET /immediate/historical-odds-ncaab - Get odds with filters")
    print("- GET /immediate/historical-odds-ncaab/game/{id} - Get odds by game")
    print("- GET /immediate/historical-odds-ncaab/movements/{id} - Get odds movements")
    print("- GET /immediate/historical-odds-ncaab/comparison/{id} - Compare bookmakers")
    print("- GET /immediate/historical-odds-ncaab/statistics - Get statistics")
    print("- GET /immediate/historical-odds-ncaab/efficiency - Analyze efficiency")
    print("- GET /immediate/historical-odds-ncaab/search - Search odds")
    
    print("\nBusiness Value:")
    print("- Historical betting pattern analysis")
    print("- Market efficiency tracking")
    print("- Bookmaker comparison shopping")
    print("- Odds movement prediction")
    print("- Value betting opportunities")
    print("- Risk management insights")
    
    print("\nIntegration Features:")
    print("- Real-time odds tracking")
    print("- Multiple bookmaker integration")
    print("- Automated odds collection")
    print("- Historical trend analysis")
    print("- Performance metrics calculation")
    
    print("\n" + "="*80)
    print("HISTORICAL ODDS NCAAB SYSTEM COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    test_historical_odds_ncaab()
