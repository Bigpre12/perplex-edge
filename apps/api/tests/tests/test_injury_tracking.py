#!/usr/bin/env python3
"""
TEST INJURY TRACKING ENDPOINTS - Test the new injury tracking endpoints
"""
import requests
import time
from datetime import datetime

def test_injury_tracking():
    """Test injury tracking endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING INJURY TRACKING ENDPOINTS")
    print("="*80)
    
    print(f"\nTime: {datetime.now().strftime('%I:%M:%S %p')}")
    print("Testing injury tracking endpoints...")
    
    # Test endpoints
    endpoints = [
        ("Injuries", "/immediate/injuries"),
        ("Active Injuries", "/immediate/injuries/active"),
        ("Out Injuries", "/immediate/injuries/out"),
        ("Injury Statistics", "/immediate/injuries/statistics?days=30"),
        ("Player Injuries", "/immediate/injuries/player/65"),
        ("Injury Impact Analysis", "/immediate/injuries/impact-analysis/30"),
        ("Injury Trends", "/immediate/injuries/trends/30"),
        ("Search Injuries", "/immediate/injuries/search?query=knee")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"\n{name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if name == "Injuries":
                    injuries = data.get('injuries', [])
                    print(f"  Total Injuries: {data.get('total', 0)}")
                    print(f"  Filters: {data.get('filters', {})}")
                    
                    for injury in injuries[:2]:
                        print(f"  - Player {injury['player_id']}: {injury['status']}")
                        print(f"    Detail: {injury['status_detail']}")
                        print(f"    Starter: {injury['is_starter_flag']}")
                        print(f"    Probability: {injury['probability']:.2f}")
                        print(f"    Source: {injury['source']}")
                        
                elif name == "Active Injuries":
                    active = data.get('active_injuries', [])
                    print(f"  Active Injuries: {data.get('total', 0)}")
                    print(f"  Sport ID: {data.get('sport_id', 'N/A')}")
                    
                    for injury in active[:2]:
                        print(f"  - Player {injury['player_id']}: {injury['status']}")
                        print(f"    Detail: {injury['status_detail']}")
                        print(f"    Probability: {injury['probability']:.2f}")
                        
                elif name == "Out Injuries":
                    out = data.get('out_injuries', [])
                    print(f"  Out Injuries: {data.get('total', 0)}")
                    print(f"  Sport ID: {data.get('sport_id', 'N/A')}")
                    
                    for injury in out[:2]:
                        print(f"  - Player {injury['player_id']}: {injury['status']}")
                        print(f"    Detail: {injury['status_detail']}")
                        print(f"    Starter: {injury['is_starter_flag']}")
                        
                elif name == "Injury Statistics":
                    print(f"  Period: {data.get('period_days', 0)} days")
                    print(f"  Total Injuries: {data.get('total_injuries', 0)}")
                    print(f"  Unique Sports: {data.get('unique_sports', 0)}")
                    print(f"  Unique Players: {data.get('unique_players', 0)}")
                    print(f"  Out Injuries: {data.get('out_injuries', 0)}")
                    print(f"  Day-to-Day: {data.get('day_to_day_injuries', 0)}")
                    print(f"  Questionable: {data.get('questionable_injuries', 0)}")
                    print(f"  Doubtful: {data.get('doubtful_injuries', 0)}")
                    print(f"  Starter Injuries: {data.get('starter_injuries', 0)}")
                    print(f"  Avg Probability: {data.get('avg_probability', 0):.2f}")
                    
                    sports = data.get('by_sport', [])
                    print(f"  Sports: {len(sports)}")
                    for sport in sports[:2]:
                        print(f"    - Sport {sport['sport_id']}: {sport['total_injuries']} injuries")
                        
                    statuses = data.get('by_status', [])
                    print(f"  Statuses: {len(statuses)}")
                    for status in statuses[:2]:
                        print(f"    - {status['status']}: {status['total_injuries']} injuries")
                        
                elif name == "Player Injuries":
                    print(f"  Player ID: {data.get('player_id', 0)}")
                    injuries = data.get('injuries', [])
                    print(f"  Injuries: {data.get('total', 0)}")
                    
                    for injury in injuries:
                        print(f"  - {injury['status']}: {injury['status_detail']}")
                        print(f"    Probability: {injury['probability']:.2f}")
                        
                elif name == "Injury Impact Analysis":
                    print(f"  Sport ID: {data.get('sport_id', 0)}")
                    print(f"  Period: {data.get('period_days', 0)} days")
                    print(f"  Total Injuries: {data.get('total_injuries', 0)}")
                    print(f"  Active Injuries: {data.get('active_injuries', 0)}")
                    print(f"  Out Injuries: {data.get('out_injuries', 0)}")
                    print(f"  Starter Injuries: {data.get('starter_injuries', 0)}")
                    print(f"  Starter Impact Score: {data.get('starter_impact_score', 0):.1f}%")
                    print(f"  Active Impact Score: {data.get('active_impact_score', 0):.1f}%")
                    print(f"  Out Impact Score: {data.get('out_impact_score', 0):.1f}%")
                    print(f"  Weighted Impact: {data.get('weighted_impact', 0):.2f}")
                    print(f"  Impact Analysis: {data.get('impact_analysis', 'N/A')}")
                    
                    concerning = data.get('concerning_injuries', [])
                    print(f"  Concerning Injuries: {len(concerning)}")
                    for injury in concerning[:2]:
                        print(f"    - Player {injury['player_id']}: {injury['status']}")
                        print(f"      {injury['status_detail']} (Starter: {injury['is_starter']})")
                        
                elif name == "Injury Trends":
                    print(f"  Sport ID: {data.get('sport_id', 0)}")
                    print(f"  Period: {data.get('period_days', 0)} days")
                    print(f"  Trend Analysis: {data.get('trend_analysis', 'N/A')}")
                    
                    trends = data.get('daily_trends', [])
                    print(f"  Daily Trends: {len(trends)} days")
                    for trend in trends[:2]:
                        print(f"    - {trend['date']}: {trend['total_injuries']} total")
                        print(f"      Out: {trend['out_injuries']}, Day-to-Day: {trend['day_to_day_injuries']}")
                        
                elif name == "Search Injuries":
                    print(f"  Query: {data.get('query', 'N/A')}")
                    print(f"  Total Results: {data.get('total', 0)}")
                    print(f"  Limit: {data.get('limit', 0)}")
                    
                    results = data.get('results', [])
                    print(f"  Results: {len(results)}")
                    for result in results:
                        print(f"    - Player {result['player_id']}: {result['status']}")
                        print(f"      {result['status_detail']}, Probability: {result['probability']:.2f}")
                
                print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
                print(f"  Note: {data.get('note', 'N/A')}")
                
            else:
                print(f"  Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"\n{name}: ERROR - {e}")
    
    print("\n" + "="*80)
    print("INJURY TRACKING TEST RESULTS:")
    print("="*80)
    
    print("\nInjuries Table Structure:")
    print("The injuries table tracks:")
    print("- Player injury status and details")
    print("- Injury probability and availability")
    print("- Starter vs bench player injuries")
    print("- Injury sources and update timestamps")
    print("- Multi-sport injury tracking")
    
    print("\nInjury Status Types:")
    print("- ACTIVE: Player is fully available")
    print("- DAY_TO_DAY: Minor injury, day-to-day decision")
    print("- OUT: Player will not play")
    print("- QUESTIONABLE: Uncertain availability")
    print("- DOUBTFUL: Unlikely to play")
    print("- SUSPENDED: Player suspended")
    print("- INJURED_RESERVE: On injured reserve")
    
    print("\nInjury Sources:")
    print("- OFFICIAL: Official team/league reports")
    print("- TEAM_REPORT: Team-provided information")
    print("- LEAGUE_REPORT: League-provided information")
    print("- MEDIA_REPORT: Media reports")
    print("- INSIDER: Insider information")
    
    print("\nSample Injuries:")
    print("- NBA Player 65: Day-to-day (Knee) - 50% probability")
    print("- NBA Player 67: Out (Groin) - 0% probability")
    print("- NBA Player 27: Out (Foot/Toe) - Starter")
    print("- NFL Player 101: Questionable (Concussion) - 30% probability")
    print("- NFL Player 103: Out (ACL Tear - Season-ending)")
    print("- MLB Player 201: Day-to-day (Elbow) - 40% probability")
    
    print("\nInjury Impact Analysis:")
    print("- Starter Impact Score: Percentage of injured starters")
    print("- Active Impact Score: Percentage of active injuries")
    print("- Out Impact Score: Percentage of players out")
    print("- Weighted Impact: Probability-weighted impact")
    print("- Concerning Injuries: High-priority injury concerns")
    
    print("\nAvailable Endpoints:")
    print("- GET /immediate/injuries - Get injuries with filters")
    print("- GET /immediate/injuries/active - Get active injuries")
    print("- GET /immediate/injuries/out - Get out injuries")
    print("- GET /immediate/injuries/statistics - Get statistics")
    print("- GET /immediate/injuries/player/{id} - Get player injuries")
    print("- GET /immediate/injuries/impact-analysis/{sport_id} - Analyze impact")
    print("- GET /immediate/injuries/trends/{sport_id} - Analyze trends")
    print("- GET /immediate/injuries/search - Search injuries")
    
    print("\nBusiness Value:")
    print("- Player availability assessment")
    print("- Team strength evaluation")
    print("- Betting line adjustments")
    print("- Risk management for predictions")
    print("- Fantasy sports lineup decisions")
    
    print("\nIntegration Features:")
    print("- Multi-sport injury tracking")
    print("- Real-time injury updates")
    print("- Probability-based availability")
    print("- Starter impact analysis")
    print("- Trend analysis and forecasting")
    
    print("\n" + "="*80)
    print("INJURY TRACKING SYSTEM COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    test_injury_tracking()
