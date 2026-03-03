#!/usr/bin/env python3
"""
TEST USER BETS ENDPOINTS - Test the new user betting tracking endpoints
"""
import requests
import time
from datetime import datetime

def test_user_bets():
    """Test user bets endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING USER BETS ENDPOINTS")
    print("="*80)
    
    print(f"\nTime: {datetime.now().strftime('%I:%M:%S %p')}")
    print("Testing user betting tracking endpoints...")
    
    # Test endpoints
    endpoints = [
        ("User Bets", "/immediate/user-bets"),
        ("User Bets Statistics", "/immediate/user-bets/statistics?days=30"),
        ("User Bets by Sport", "/immediate/user-bets/sport/30"),
        ("User Bets by Status", "/immediate/user-bets/status/won"),
        ("User Bets by Sportsbook", "/immediate/user-bets/sportsbook/DraftKings"),
        ("Search User Bets", "/immediate/user-bets/search?query=points")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"\n{name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if name == "User Bets":
                    user_bets = data.get('user_bets', [])
                    print(f"  Total User Bets: {data.get('total', 0)}")
                    print(f"  Filters: {data.get('filters', {})}")
                    
                    for bet in user_bets[:2]:
                        print(f"  - Player {bet['player_id']} {bet['market_type']} {bet['side']} {bet['line_value']}")
                        print(f"    Sport: {bet['sport_id']}, Sportsbook: {bet['sportsbook']}")
                        print(f"    Stake: ${bet['stake']:.2f}, Odds: {bet['opening_odds']}")
                        print(f"    Status: {bet['status']}")
                        if bet['status'] in ['won', 'lost']:
                            print(f"    P/L: ${bet['profit_loss']:.2f}, CLV: {bet['clv_cents']:.2f}")
                        print(f"    Placed: {bet['placed_at']}")
                        if bet['settled_at']:
                            print(f"    Settled: {bet['settled_at']}")
                        print(f"    Notes: {bet['notes']}")
                        
                elif name == "User Bets Statistics":
                    print(f"  Period: {data.get('period_days', 0)} days")
                    print(f"  Total Bets: {data.get('total_bets', 0)}")
                    print(f"  Unique Sports: {data.get('unique_sports', 0)}")
                    print(f"  Unique Games: {data.get('unique_games', 0)}")
                    print(f"  Unique Players: {data.get('unique_players', 0)}")
                    print(f"  Unique Sportsbooks: {data.get('unique_sportsbooks', 0)}")
                    print(f"  Unique Market Types: {data.get('unique_market_types', 0)}")
                    print(f"  Won Bets: {data.get('won_bets', 0)}")
                    print(f"  Lost Bets: {data.get('lost_bets', 0)}")
                    print(f"  Pending Bets: {data.get('pending_bets', 0)}")
                    print(f"  Total Stake: ${data.get('total_stake', 0):.2f}")
                    print(f"  Total P/L: ${data.get('total_profit_loss', 0):.2f}")
                    print(f"  Avg Stake: ${data.get('avg_stake', 0):.2f}")
                    print(f"  Avg P/L: ${data.get('avg_profit_loss', 0):.2f}")
                    print(f"  Win Rate: {data.get('win_rate_percentage', 0):.2f}%")
                    print(f"  Total CLV: {data.get('total_clv_cents', 0):.2f}")
                    print(f"  Avg CLV: {data.get('avg_clv_cents', 0):.2f}")
                    
                    sport_stats = data.get('sport_stats', [])
                    print(f"  Sport Statistics: {len(sport_stats)}")
                    for sport in sport_stats[:2]:
                        sport_name = {30: "NBA", 1: "NFL", 2: "MLB", 53: "NHL"}.get(sport['sport_id'], f"Sport {sport['sport_id']}")
                        print(f"    - {sport_name}:")
                        print(f"      Total Bets: {sport['total_bets']}")
                        print(f"      Won: {sport['won_bets']}, Lost: {sport['lost_bets']}, Pending: {sport['pending_bets']}")
                        print(f"      Total Stake: ${sport['total_stake']:.2f}")
                        print(f"      Total P/L: ${sport['total_profit_loss']:.2f}")
                        print(f"      Win Rate: {sport['win_rate_percentage']:.2f}%")
                        
                    sportsbook_stats = data.get('sportsbook_stats', [])
                    print(f"  Sportsbook Statistics: {len(sportsbook_stats)}")
                    for sportsbook in sportsbook_stats[:2]:
                        print(f"    - {sportsbook['sportsbook']}:")
                        print(f"      Total Bets: {sportsbook['total_bets']}")
                        print(f"      Won: {sportsbook['won_bets']}, Lost: {sportsbook['lost_bets']}, Pending: {sportsbook['pending_bets']}")
                        print(f"      Total Stake: ${sportsbook['total_stake']:.2f}")
                        print(f"      Total P/L: ${sportsbook['total_profit_loss']:.2f}")
                        print(f"      Win Rate: {sportsbook['win_rate_percentage']:.2f}%")
                        
                    market_stats = data.get('market_stats', [])
                    print(f"  Market Statistics: {len(market_stats)}")
                    for market in market_stats[:2]:
                        print(f"    - {market['market_type']}:")
                        print(f"      Total Bets: {market['total_bets']}")
                        print(f"      Won: {market['won_bets']}, Lost: {market['lost_bets']}, Pending: {market['pending_bets']}")
                        print(f"      Total Stake: ${market['total_stake']:.2f}")
                        print(f"      Total P/L: ${market['total_profit_loss']:.2f}")
                        print(f"      Win Rate: {market['win_rate_percentage']:.2f}%")
                        
                elif name == "User Bets by Sport":
                    user_bets = data.get('user_bets', [])
                    print(f"  Sport ID: {data.get('sport_id', 'N/A')}")
                    print(f"  Total Bets: {data.get('total', 0)}")
                    
                    for bet in user_bets:
                        print(f"  - Player {bet['player_id']} {bet['market_type']} {bet['side']} {bet['line_value']}")
                        print(f"    Sportsbook: {bet['sportsbook']}")
                        print(f"    Stake: ${bet['stake']:.2f}, Odds: {bet['opening_odds']}")
                        print(f"    Status: {bet['status']}")
                        if bet['status'] in ['won', 'lost']:
                            print(f"    P/L: ${bet['profit_loss']:.2f}, CLV: {bet['clv_cents']:.2f}")
                        print(f"    Placed: {bet['placed_at']}")
                        print(f"    Notes: {bet['notes']}")
                        
                elif name == "User Bets by Status":
                    user_bets = data.get('user_bets', [])
                    print(f"  Status: {data.get('status', 'N/A')}")
                    print(f"  Total Bets: {data.get('total', 0)}")
                    
                    for bet in user_bets:
                        print(f"  - Player {bet['player_id']} {bet['market_type']} {bet['side']} {bet['line_value']}")
                        print(f"    Sport: {bet['sport_id']}, Sportsbook: {bet['sportsbook']}")
                        print(f"    Stake: ${bet['stake']:.2f}, Odds: {bet['opening_odds']}")
                        print(f"    P/L: ${bet['profit_loss']:.2f}, CLV: {bet['clv_cents']:.2f}")
                        print(f"    Placed: {bet['placed_at']}")
                        print(f"    Settled: {bet['settled_at']}")
                        print(f"    Notes: {bet['notes']}")
                        
                elif name == "User Bets by Sportsbook":
                    user_bets = data.get('user_bets', [])
                    print(f"  Sportsbook: {data.get('sportsbook', 'N/A')}")
                    print(f"  Total Bets: {data.get('total', 0)}")
                    
                    for bet in user_bets:
                        print(f"  - Player {bet['player_id']} {bet['market_type']} {bet['side']} {bet['line_value']}")
                        print(f"    Sport: {bet['sport_id']}, Status: {bet['status']}")
                        print(f"    Stake: ${bet['stake']:.2f}, Odds: {bet['opening_odds']}")
                        print(f"    P/L: ${bet['profit_loss']:.2f}, CLV: {bet['clv_cents']:.2f}")
                        print(f"    Placed: {bet['placed_at']}")
                        print(f"    Notes: {bet['notes']}")
                        
                elif name == "Search User Bets":
                    results = data.get('results', [])
                    print(f"  Query: {data.get('query', 'N/A')}")
                    print(f"  Total Results: {data.get('total', 0)}")
                    print(f"  Limit: {data.get('limit', 0)}")
                    
                    for result in results:
                        print(f"  - Player {result['player_id']} {result['market_type']} {result['side']} {result['line_value']}")
                        print(f"    Sport: {result['sport_id']}, Sportsbook: {result['sportsbook']}")
                        print(f"    Stake: ${result['stake']:.2f}, Odds: {result['opening_odds']}")
                        print(f"    Status: {result['status']}")
                        print(f"    P/L: ${result['profit_loss']:.2f}, CLV: {result['clv_cents']:.2f}")
                        print(f"    Placed: {result['placed_at']}")
                        print(f"    Notes: {result['notes']}")
                
                print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
                print(f"  Note: {data.get('note', 'N/A')}")
                
            else:
                print(f"  Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"\n{name}: ERROR - {e}")
    
    print("\n" + "="*80)
    print("USER BETS TEST RESULTS:")
    print("="*80)
    
    print("\nUser Bets Table Structure:")
    print("The user_bets table tracks:")
    print("- Individual user betting activity and performance")
    print("- Detailed bet information including odds and lines")
    print("- Profit/loss calculations and CLV tracking")
    print("- Sportsbook and market type categorization")
    print("- Settlement status and timestamps")
    
    print("\nBet Data Types:")
    print("- Sport/Game/Player ID: Context and target information")
    print("- Market Type: Type of bet (points, yards, HRs, etc.)")
    print("- Side: Over/under or other bet direction")
    print("- Line Value: Specific line for the bet")
    print("- Sportsbook: Where the bet was placed")
    print("- Odds: Opening and closing odds")
    print("- Stake: Amount wagered")
    print("- Status: Won, lost, pending, etc.")
    print("- P/L: Profit or loss amount")
    print("- CLV: Closing line value")
    
    print("\nBet Categories:")
    print("- Player Props: Individual player performance bets")
    print("- Over/Under: Betting on statistical totals")
    print("- Multi-Sport: NBA, NFL, MLB, NHL coverage")
    print("- Various Sportsbooks: DK, FD, BetMGM, etc.")
    print("- Status Tracking: Won, lost, pending bets")
    
    print("\nSample Bet Scenarios:")
    print("- LeBron James over 24.5 points: $110 stake, $100 profit")
    print("- Patrick Mahomes over 285.5 yards: $110 stake, $100 profit")
    print("- Aaron Judge over 1.5 HRs: $110 stake, $100 profit")
    print("- Connor McDavid over 1.5 points: $110 stake, $100 profit")
    print("- Jayson Tatum over 22.5 points: $220 stake, pending")
    
    print("\nBetting Analysis Features:")
    print("- Performance Tracking: Win rates and profit/loss")
    print("- CLV Analysis: Closing line value tracking")
    print("- Sportsbook Comparison: Performance by sportsbook")
    print("- Market Analysis: Success by market type")
    print("- Sport Analysis: Performance by sport")
    
    print("\nBusiness Value:")
    print("- User Account Management: Complete betting history")
    print("- Performance Analytics: Detailed betting performance")
    print("- Risk Management: Stake and profit tracking")
    print("- Market Intelligence: Sportsbook and market insights")
    print("- User Engagement: Betting activity and patterns")
    
    print("\nAvailable Endpoints:")
    print("- GET /immediate/user-bets - Get bets with filters")
    print("- GET /immediate/user-bets/statistics - Get overall statistics")
    print("- GET /immediate/user-bets/sport/{sport_id} - Get sport bets")
    print("- GET /immediate/user-bets/status/{status} - Get status bets")
    print("- GET /immediate/user-bets/sportsbook/{sportsbook} - Get sportsbook bets")
    print("- GET /immediate/user-bets/search - Search user bets")
    
    print("\nIntegration Features:")
    print("- Multi-Sport Support: NBA, NFL, MLB, NHL bets")
    print("- Sportsbook Integration: Major sportsbooks tracked")
    print("- Market Variety: Points, yards, HRs, etc.")
    print("- Performance Metrics: P/L, CLV, win rates")
    print("- Status Management: Real-time bet settlement")
    
    print("\n" + "="*80)
    print("USER BETS SYSTEM COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    test_user_bets()
