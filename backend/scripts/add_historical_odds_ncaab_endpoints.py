#!/usr/bin/env python3
"""
ADD HISTORICAL ODDS NCAAB ENDPOINTS - Add NCAA basketball historical odds endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_historical_odds_ncaab_endpoints():
    """Add NCAA basketball historical odds endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the historical odds endpoints
    historical_odds_code = '''

# Historical Odds NCAAB Endpoints
@router.get("/historical-odds-ncaab")
async def get_historical_odds_ncaab(game_id: int = Query(None, description="Game ID to filter"), 
                                  bookmaker: str = Query(None, description="Bookmaker to filter"),
                                  team: str = Query(None, description="Team name to filter"),
                                  days: int = Query(30, description="Days of data to return"),
                                  limit: int = Query(50, description="Number of odds to return")):
    """Get NCAA basketball historical odds with optional filters"""
    try:
        # Return mock historical odds data for now
        mock_odds = [
            {
                "id": 1,
                "sport": 32,
                "game_id": 1001,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -150,
                "away_odds": 130,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            },
            {
                "id": 2,
                "sport": 32,
                "game_id": 1001,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -145,
                "away_odds": 125,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            },
            {
                "id": 3,
                "sport": 32,
                "game_id": 1002,
                "home_team": "Kansas Jayhawks",
                "away_team": "Kentucky Wildcats",
                "home_odds": -110,
                "away_odds": -110,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=6, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=12)).isoformat()
            },
            {
                "id": 4,
                "sport": 32,
                "game_id": 1003,
                "home_team": "UCLA Bruins",
                "away_team": "Gonzaga Bulldogs",
                "home_odds": 180,
                "away_odds": -220,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=5, hours=12)).isoformat(),
                "result": "away_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5, hours=12)).isoformat()
            },
            {
                "id": 5,
                "sport": 32,
                "game_id": 1004,
                "home_team": "Michigan Wolverines",
                "away_team": "Ohio State Buckeyes",
                "home_odds": -125,
                "away_odds": 105,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=4, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=4, hours=12)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_odds = mock_odds
        if game_id:
            filtered_odds = [o for o in filtered_odds if o['game_id'] == game_id]
        if bookmaker:
            filtered_odds = [o for o in filtered_odds if o['bookmaker'].lower() == bookmaker.lower()]
        if team:
            filtered_odds = [o for o in filtered_odds if team.lower() in o['home_team'].lower() or team.lower() in o['away_team'].lower()]
        
        return {
            "odds": filtered_odds[:limit],
            "total": len(filtered_odds),
            "filters": {
                "game_id": game_id,
                "bookmaker": bookmaker,
                "team": team,
                "days": days,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock NCAA basketball historical odds data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/game/{game_id}")
async def get_odds_by_game(game_id: int):
    """Get odds history for a specific game"""
    try:
        # Return mock odds history for a specific game
        mock_odds_history = [
            {
                "id": 1,
                "sport": 32,
                "game_id": game_id,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -150,
                "away_odds": 130,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            },
            {
                "id": 2,
                "sport": 32,
                "game_id": game_id,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -145,
                "away_odds": 125,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            },
            {
                "id": 3,
                "sport": 32,
                "game_id": game_id,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -155,
                "away_odds": 135,
                "draw_odds": None,
                "bookmaker": "BetMGM",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            },
            {
                "id": 4,
                "sport": 32,
                "game_id": game_id,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -140,
                "away_odds": 120,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat()
            },
            {
                "id": 5,
                "sport": 32,
                "game_id": game_id,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat()
            }
        ]
        
        return {
            "game_id": game_id,
            "home_team": "Duke Blue Devils",
            "away_team": "North Carolina Tar Heels",
            "odds_history": mock_odds_history,
            "total_snapshots": len(mock_odds_history),
            "bookmakers": list(set(o['bookmaker'] for o in mock_odds_history)),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds history for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/movements/{game_id}")
async def get_odds_movements(game_id: int):
    """Get odds movements for a specific game"""
    try:
        # Return mock odds movements data
        mock_movements = [
            {
                "bookmaker": "DraftKings",
                "home_odds": -150,
                "away_odds": 130,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "home_movement": 0,
                "away_movement": 0,
                "draw_movement": 0,
                "prev_home_odds": None,
                "prev_away_odds": None,
                "prev_draw_odds": None
            },
            {
                "bookmaker": "DraftKings",
                "home_odds": -140,
                "away_odds": 120,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "home_movement": 10,
                "away_movement": -10,
                "draw_movement": 0,
                "prev_home_odds": -150,
                "prev_away_odds": 130,
                "prev_draw_odds": None
            },
            {
                "bookmaker": "FanDuel",
                "home_odds": -145,
                "away_odds": 125,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "home_movement": 0,
                "away_movement": 0,
                "draw_movement": 0,
                "prev_home_odds": None,
                "prev_away_odds": None,
                "prev_draw_odds": None
            },
            {
                "bookmaker": "FanDuel",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "home_movement": -15,
                "away_movement": 15,
                "draw_movement": 0,
                "prev_home_odds": -145,
                "prev_away_odds": 125,
                "prev_draw_odds": None
            },
            {
                "bookmaker": "BetMGM",
                "home_odds": -155,
                "away_odds": 135,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "home_movement": 0,
                "away_movement": 0,
                "draw_movement": 0,
                "prev_home_odds": None,
                "prev_away_odds": None,
                "prev_draw_odds": None
            }
        ]
        
        return {
            "game_id": game_id,
            "movements": mock_movements,
            "total_movements": len(mock_movements),
            "bookmakers": list(set(m['bookmaker'] for m in mock_movements)),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds movements for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/comparison/{game_id}")
async def get_bookmaker_comparison(game_id: int):
    """Compare odds across bookmakers for a specific game"""
    try:
        # Return mock bookmaker comparison data
        mock_comparison = [
            {
                "bookmaker": "DraftKings",
                "home_odds": -140,
                "away_odds": 120,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "result": "home_win"
            },
            {
                "bookmaker": "FanDuel",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "result": "home_win"
            },
            {
                "bookmaker": "BetMGM",
                "home_odds": -155,
                "away_odds": 135,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win"
            },
            {
                "bookmaker": "Caesars",
                "home_odds": -145,
                "away_odds": 125,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=6)).isoformat(),
                "result": "home_win"
            },
            {
                "bookmaker": "PointsBet",
                "home_odds": -150,
                "away_odds": 130,
                "draw_odds": None,
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win"
            }
        ]
        
        # Calculate best odds
        best_home_odds = max(mock_comparison, key=lambda x: x['home_odds'])
        best_away_odds = min(mock_comparison, key=lambda x: x['away_odds'])
        
        return {
            "game_id": game_id,
            "home_team": "Duke Blue Devils",
            "away_team": "North Carolina Tar Heels",
            "comparison": mock_comparison,
            "best_home_odds": {
                "bookmaker": best_home_odds['bookmaker'],
                "odds": best_home_odds['home_odds']
            },
            "best_away_odds": {
                "bookmaker": best_away_odds['bookmaker'],
                "odds": best_away_odds['away_odds']
            },
            "total_bookmakers": len(mock_comparison),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock bookmaker comparison for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/statistics")
async def get_historical_odds_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get NCAA basketball historical odds statistics"""
    try:
        # Return mock statistics data
        mock_stats = {
            "period_days": days,
            "total_odds": 28,
            "unique_games": 8,
            "unique_bookmakers": 6,
            "unique_teams": 16,
            "home_wins": 18,
            "away_wins": 10,
            "pending_games": 0,
            "home_win_rate": 64.3,
            "avg_home_odds": -45.7,
            "avg_away_odds": -45.7,
            "avg_draw_odds": None,
            "by_bookmaker": [
                {
                    "bookmaker": "DraftKings",
                    "total_odds": 8,
                    "unique_games": 8,
                    "home_wins": 5,
                    "away_wins": 3,
                    "pending_games": 0,
                    "avg_home_odds": -48.8,
                    "avg_away_odds": -48.8,
                    "avg_draw_odds": None
                },
                {
                    "bookmaker": "FanDuel",
                    "total_odds": 6,
                    "unique_games": 6,
                    "home_wins": 4,
                    "away_wins": 2,
                    "pending_games": 0,
                    "avg_home_odds": -42.5,
                    "avg_away_odds": -42.5,
                    "avg_draw_odds": None
                },
                {
                    "bookmaker": "BetMGM",
                    "total_odds": 5,
                    "unique_games": 5,
                    "home_wins": 3,
                    "away_wins": 2,
                    "pending_games": 0,
                    "avg_home_odds": -50.0,
                    "avg_away_odds": -50.0,
                    "avg_draw_odds": None
                },
                {
                    "bookmaker": "Caesars",
                    "total_odds": 4,
                    "unique_games": 4,
                    "home_wins": 3,
                    "away_wins": 1,
                    "pending_games": 0,
                    "avg_home_odds": -37.5,
                    "avg_away_odds": -37.5,
                    "avg_draw_odds": None
                },
                {
                    "bookmaker": "PointsBet",
                    "total_odds": 3,
                    "unique_games": 3,
                    "home_wins": 2,
                    "away_wins": 1,
                    "pending_games": 0,
                    "avg_home_odds": -50.0,
                    "avg_away_odds": -50.0,
                    "avg_draw_odds": None
                },
                {
                    "bookmaker": "Bet365",
                    "total_odds": 2,
                    "unique_games": 2,
                    "home_wins": 1,
                    "away_wins": 1,
                    "pending_games": 0,
                    "avg_home_odds": -50.0,
                    "avg_away_odds": -50.0,
                    "avg_draw_odds": None
                }
            ],
            "by_team": [
                {
                    "team": "Duke Blue Devils",
                    "total_games": 5,
                    "home_wins": 5,
                    "home_losses": 0,
                    "avg_home_odds": -150.0,
                    "avg_away_odds": 130.0
                },
                {
                    "team": "Kansas Jayhawks",
                    "total_games": 4,
                    "home_wins": 4,
                    "home_losses": 0,
                    "avg_home_odds": -110.0,
                    "avg_away_odds": -110.0
                },
                {
                    "team": "UCLA Bruins",
                    "total_games": 4,
                    "home_wins": 0,
                    "home_losses": 4,
                    "avg_home_odds": 180.0,
                    "avg_away_odds": -220.0
                },
                {
                    "team": "Michigan Wolverines",
                    "total_games": 3,
                    "home_wins": 3,
                    "home_losses": 0,
                    "avg_home_odds": -125.0,
                    "avg_away_odds": 105.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock NCAA basketball historical odds statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/efficiency")
async def get_odds_efficiency(days: int = Query(30, description="Days of data to analyze")):
    """Analyze odds efficiency and accuracy"""
    try:
        # Return mock efficiency analysis data
        mock_efficiency = {
            "period_days": days,
            "bookmaker_efficiency": [
                {
                    "bookmaker": "DraftKings",
                    "total_games": 8,
                    "home_wins": 5,
                    "away_wins": 3,
                    "avg_implied_home_prob": 60.0,
                    "avg_implied_away_prob": 40.0,
                    "actual_home_win_rate": 62.5,
                    "home_accuracy": 97.5,
                    "away_accuracy": 97.5,
                    "overall_accuracy": 97.5,
                    "home_edge": 2.5,
                    "away_edge": -2.5
                },
                {
                    "bookmaker": "FanDuel",
                    "total_games": 6,
                    "home_wins": 4,
                    "away_wins": 2,
                    "avg_implied_home_prob": 58.3,
                    "avg_implied_away_prob": 41.7,
                    "actual_home_win_rate": 66.7,
                    "home_accuracy": 91.6,
                    "away_accuracy": 91.6,
                    "overall_accuracy": 91.6,
                    "home_edge": 8.4,
                    "away_edge": -8.4
                },
                {
                    "bookmaker": "BetMGM",
                    "total_games": 5,
                    "home_wins": 3,
                    "away_wins": 2,
                    "avg_implied_home_prob": 60.0,
                    "avg_implied_away_prob": 40.0,
                    "actual_home_win_rate": 60.0,
                    "home_accuracy": 100.0,
                    "away_accuracy": 100.0,
                    "overall_accuracy": 100.0,
                    "home_edge": 0.0,
                    "away_edge": 0.0
                },
                {
                    "bookmaker": "Caesars",
                    "total_games": 4,
                    "home_wins": 3,
                    "away_wins": 1,
                    "avg_implied_home_prob": 56.3,
                    "avg_implied_away_prob": 43.8,
                    "actual_home_win_rate": 75.0,
                    "home_accuracy": 81.3,
                    "away_accuracy": 81.3,
                    "overall_accuracy": 81.3,
                    "home_edge": 18.7,
                    "away_edge": -18.7
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock odds efficiency analysis data"
        }
        
        return mock_efficiency
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-odds-ncaab/search")
async def search_historical_odds(query: str = Query(..., description="Search query"), 
                                 days: int = Query(30, description="Days of data to search"),
                                 limit: int = Query(20, description="Number of results to return")):
    """Search NCAA basketball historical odds"""
    try:
        # Return mock search results
        mock_results = [
            {
                "id": 1,
                "sport": 32,
                "game_id": 1001,
                "home_team": "Duke Blue Devils",
                "away_team": "North Carolina Tar Heels",
                "home_odds": -150,
                "away_odds": 130,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "snapshot_date": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "result": "home_win",
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=12)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                o for o in mock_results 
                if query_lower in o['home_team'].lower() or 
                   query_lower in o['away_team'].lower() or 
                   query_lower in o['bookmaker'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "days": days,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
'''
    
    # Add the endpoints before the anomaly endpoints
    if "# Brain Anomaly Detection Endpoints" in content:
        content = content.replace("# Brain Anomaly Detection Endpoints", historical_odds_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += historical_odds_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Historical odds NCAAB endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_historical_odds_ncaab_endpoints())
