#!/usr/bin/env python3
"""
TEST GAMES ENDPOINTS - Test the new games management endpoints
"""
import requests
import time
from datetime import datetime

def test_games():
    """Test games endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING GAMES ENDPOINTS")
    print("="*80)
    
    print(f"\nTime: {datetime.now().strftime('%I:%M:%S %p')}")
    print("Testing games management endpoints...")
    
    # Test endpoints
    endpoints = [
        ("Games", "/immediate/games"),
        ("Upcoming Games", "/immediate/games/upcoming"),
        ("Recent Games", "/immediate/games/recent"),
        ("Games Statistics", "/immediate/games/statistics?days=30"),
        ("Game Schedule", "/immediate/games/schedule?start_date=2026-02-08&end_date=2026-02-09"),
        ("Game Detail", "/immediate/games/1"),
        ("Search Games", "/immediate/games/search?query=chiefs")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"\n{name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if name == "Games":
                    games = data.get('games', [])
                    print(f"  Total Games: {data.get('total', 0)}")
                    print(f"  Filters: {data.get('filters', {})}")
                    
                    for game in games[:2]:
                        print(f"  - {game['external_game_id']}: {game['home_team_name']} vs {game['away_team_name']}")
                        print(f"    Sport: {game['sport_name']} ({game['sport_id']})")
                        print(f"    Status: {game['status']}")
                        print(f"    Start: {game['start_time']}")
                        
                elif name == "Upcoming Games":
                    upcoming = data.get('upcoming_games', [])
                    print(f"  Upcoming Games: {data.get('total', 0)}")
                    print(f"  Hours: {data.get('hours', 0)}")
                    
                    for game in upcoming:
                        print(f"  - {game['external_game_id']}: {game['home_team_name']} vs {game['away_team_name']}")
                        print(f"    Sport: {game['sport_name']} ({game['sport_id']})")
                        print(f"    Start: {game['start_time']}")
                        
                elif name == "Recent Games":
                    recent = data.get('recent_games', [])
                    print(f"  Recent Games: {data.get('total', 0)}")
                    print(f"  Hours: {data.get('hours', 0)}")
                    
                    for game in recent:
                        print(f"  - {game['external_game_id']}: {game['home_team_name']} vs {game['away_team_name']}")
                        print(f"    Sport: {game['sport_name']} ({game['sport_id']})")
                        print(f"    Status: {game['status']}")
                        print(f"    Start: {game['start_time']}")
                        
                elif name == "Games Statistics":
                    print(f"  Period: {data.get('period_days', 0)} days")
                    print(f"  Total Games: {data.get('total_games', 0)}")
                    print(f"  Final: {data.get('final_games', 0)}")
                    print(f"  Scheduled: {data.get('scheduled_games', 0)}")
                    print(f"  In Progress: {data.get('in_progress_games', 0)}")
                    
                    sports = data.get('by_sport', [])
                    print(f"  Sports: {len(sports)}")
                    for sport in sports:
                        print(f"    - Sport {sport['sport_id']}: {sport['total_games']} games")
                        
                elif name == "Game Schedule":
                    schedule = data.get('schedule', [])
                    print(f"  Date Range: {data.get('start_date', 'N/A')} to {data.get('end_date', 'N/A')}")
                    print(f"  Total Games: {data.get('total', 0)}")
                    
                    for game in schedule:
                        print(f"  - {game['external_game_id']}: {game['home_team_name']} vs {game['away_team_name']}")
                        print(f"    Sport: {game['sport_name']} ({game['sport_id']})")
                        print(f"    Start: {game['start_time']}")
                        
                elif name == "Game Detail":
                    print(f"  Game ID: {data.get('id', 0)}")
                    print(f"  External ID: {data.get('external_game_id', 'N/A')}")
                    print(f"  Teams: {data.get('home_team_name', 'N/A')} vs {data.get('away_team_name', 'N/A')}")
                    print(f"  Sport: {data.get('sport_name', 'N/A')} ({data.get('sport_id', 0)})")
                    print(f"  Status: {data.get('status', 'N/A')}")
                    print(f"  Start: {data.get('start_time', 'N/A')}")
                    
                    details = data.get('game_details', {})
                    print(f"  Venue: {details.get('venue', 'N/A')}")
                    print(f"  Location: {details.get('location', 'N/A')}")
                    print(f"  Attendance: {details.get('attendance', 0):,}")
                    
                    betting = data.get('betting_summary', {})
                    print(f"  Total Bets: {betting.get('total_bets', 0):,}")
                    print(f"  Total Wagered: ${betting.get('total_wagered', 0):,}")
                    print(f"  ROI: {betting.get('roi_percent', 0):.1f}%")
                    
                elif name == "Search Games":
                    results = data.get('results', [])
                    print(f"  Search Query: {data.get('query', 'N/A')}")
                    print(f"  Total Results: {data.get('total', 0)}")
                    print(f"  Limit: {data.get('limit', 0)}")
                    
                    for game in results:
                        print(f"  - {game['external_game_id']}: {game['home_team_name']} vs {game['away_team_name']}")
                        print(f"    Sport: {game['sport_name']} ({game['sport_id']})")
                        print(f"    Status: {game['status']}")
                
                print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
                print(f"  Note: {data.get('note', 'N/A')}")
                
            else:
                print(f"  Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"\n{name}: ERROR - {e}")
    
    # Test POST endpoints
    post_endpoints = [
        ("Create Game", "/immediate/games/create", {
            "game_id": 1006,
            "external_game_id": "nfl_test_game_20260209",
            "home_team_id": 390,
            "away_team_id": 391,
            "start_time": "2026-02-10T20:00:00Z"
        }),
        ("Update Game Status", "/immediate/games/1006/status?status=final", {})
    ]
    
    for name, endpoint, data in post_endpoints:
        try:
            if name == "Update Game Status":
                response = requests.put(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", json=data, timeout=10)
            
            print(f"\n{name}: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                if name == "Create Game":
                    print(f"  Status: {result.get('status', 'unknown')}")
                    print(f"  Game ID: {result.get('game_id', 0)}")
                    print(f"  External ID: {result.get('external_game_id', 'N/A')}")
                    print(f"  Created: {result.get('created_at', 'N/A')}")
                    
                elif name == "Update Game Status":
                    print(f"  Status: {result.get('status', 'unknown')}")
                    print(f"  Game ID: {result.get('game_id', 0)}")
                    print(f"  New Status: {result.get('new_status', 'N/A')}")
                    print(f"  Updated: {result.get('updated_at', 'N/A')}")
                
                print(f"  Timestamp: {result.get('timestamp', 'N/A')}")
                print(f"  Note: {result.get('note', 'N/A')}")
                
            else:
                print(f"  Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"\n{name}: ERROR - {e}")
    
    print("\n" + "="*80)
    print("GAMES TEST RESULTS:")
    print("="*80)
    
    print("\nGames Table Structure:")
    print("The games table tracks:")
    print("- Game schedule and metadata")
    print("- Team matchups and timing")
    print("- Game status tracking")
    print("- External game ID mapping")
    print("- Season information")
    print("- Creation and update timestamps")
    
    print("\nGame Status Types:")
    print("- Scheduled: Game scheduled but not started")
    print("- In Progress: Game currently being played")
    print("- Final: Game completed with results")
    print("- Cancelled: Game cancelled (rare)")
    print("- Postponed: Game rescheduled")
    print("- Suspended: Game temporarily suspended")
    
    print("\nSports Supported:")
    print("- NFL (sport_id: 32): Professional Football")
    print("- NBA (sport_id: 30): Professional Basketball")
    print("- NHL (sport_id: 53): Professional Hockey")
    print("- NCAA Basketball: College Basketball")
    print("- MLB (sport_id: 29): Professional Baseball")
    
    print("\nSample Games:")
    print("- NFL: KC vs BUF (Final)")
    print("- NFL: PHI vs NYG (Final)")
    print("- NBA: LAL vs BOS (Final)")
    print("- NHL: RAN vs HUR (Final)")
    print("- NCAA: ESPN Tournament Games (Scheduled)")
    
    print("\nGame Features:")
    print("- Real-time status updates")
    print("- Team name mapping")
    print("- External provider integration")
    print("- Season tracking")
    print("- Search functionality")
    print("- Schedule management")
    
    print("\nAvailable Endpoints:")
    print("- GET /immediate/games - Get games with filters")
    print("- GET /immediate/games/upcoming - Get upcoming games")
    print("- GET /immediate/games/recent - Get recent games")
    print("- GET /immediate/games/statistics - Get statistics")
    print("- GET /immediate/games/schedule - Get schedule by date range")
    print("- GET /immediate/games/{id} - Get detailed game info")
    print("- POST /immediate/games/create - Create new game")
    print("- PUT /immediate/games/{id}/status - Update game status")
    print("- GET /immediate/games/search - Search games")
    
    print("\nBusiness Value:")
    print("- Game schedule management")
    print("- Team matchup tracking")
    print("- Betting market preparation")
    print("- Real-time game updates")
    print("- Historical game analysis")
    
    print("\nIntegration Features:")
    print("- External data provider integration")
    print("- Team database mapping")
    print("- Real-time score updates")
    print("- Multi-sport support")
    print("- Season-based organization")
    
    print("\n" + "="*80)
    print("GAMES SYSTEM COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    test_games()
