#!/usr/bin/env python3
"""
ADD GAMES ENDPOINTS - Add games management endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_games_endpoints():
    """Add games management endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the games endpoints
    games_code = '''

# Games Management Endpoints
@router.get("/games")
async def get_games(sport_id: int = Query(None, description="Sport ID to filter"), 
                  status: str = Query(None, description="Game status to filter"),
                  start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
                  end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
                  limit: int = Query(50, description="Number of games to return")):
    """Get games with optional filters"""
    try:
        # Return mock games data for now
        mock_games = [
            {
                "id": 1,
                "sport_id": 32,
                "external_game_id": "nfl_kc_buf_20260208",
                "home_team_id": 48,
                "away_team_id": 83,
                "home_team_name": "Kansas City Chiefs",
                "away_team_name": "Buffalo Bills",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 2,
                "sport_id": 32,
                "external_game_id": "nfl_phi_nyg_20260208",
                "home_team_id": 84,
                "away_team_id": 50,
                "home_team_name": "Philadelphia Eagles",
                "away_team_name": "New York Giants",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 3,
                "sport_id": 30,
                "external_game_id": "nba_lal_bos_20260208",
                "home_team_id": 17,
                "away_team_id": 27,
                "home_team_name": "Los Angeles Lakers",
                "away_team_name": "Boston Celtics",
                "sport_name": "NBA",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 4,
                "sport_id": 32,
                "external_game_id": "nfl_ari_sea_20260209",
                "home_team_id": 390,
                "away_team_id": 391,
                "home_team_name": "Arizona Cardinals",
                "away_team_name": "Seattle Seahawks",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                "status": "scheduled",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 5,
                "sport_id": 30,
                "external_game_id": "nba_chi_cle_20260209",
                "home_team_id": 17,
                "away_team_id": 27,
                "home_team_name": "Chicago Bulls",
                "away_team_name": "Cleveland Cavaliers",
                "sport_name": "NBA",
                "start_time": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
                "status": "scheduled",
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "season_id": 2026
            }
        ]
        
        # Apply filters
        filtered_games = mock_games
        if sport_id:
            filtered_games = [g for g in filtered_games if g['sport_id'] == sport_id]
        if status:
            filtered_games = [g for g in filtered_games if g['status'] == status]
        if start_date:
            filtered_games = [g for g in filtered_games if g['start_time'][:10] >= start_date]
        if end_date:
            filtered_games = [g for g in filtered_games if g['start_time'][:10] <= end_date]
        
        return {
            "games": filtered_games[:limit],
            "total": len(filtered_games),
            "filters": {
                "sport_id": sport_id,
                "status": status,
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock games data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/upcoming")
async def get_upcoming_games(hours: int = Query(24, description="Hours ahead to look"), 
                          sport_id: int = Query(None, description="Sport ID to filter")):
    """Get upcoming games"""
    try:
        # Return mock upcoming games data for now
        mock_upcoming = [
            {
                "id": 4,
                "sport_id": 32,
                "external_game_id": "nfl_ari_sea_20260209",
                "home_team_id": 390,
                "away_team_id": 391,
                "home_team_name": "Arizona Cardinals",
                "away_team_name": "Seattle Seahawks",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                "status": "scheduled",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 5,
                "sport_id": 30,
                "external_game_id": "nba_chi_cle_20260209",
                "home_team_id": 17,
                "away_team_id": 27,
                "home_team_name": "Chicago Bulls",
                "away_team_name": "Cleveland Cavaliers",
                "sport_name": "NBA",
                "start_time": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
                "status": "scheduled",
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 6,
                "sport_id": 32,
                "external_game_id": "nfl_gb_phi_20260209",
                "home_team_id": 295,
                "away_team_id": 84,
                "home_team_name": "Green Bay Packers",
                "away_team_name": "Philadelphia Eagles",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat(),
                "status": "scheduled",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "season_id": 2026
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_upcoming = [g for g in mock_upcoming if g['sport_id'] == sport_id]
        
        return {
            "upcoming_games": mock_upcoming,
            "total": len(mock_upcoming),
            "hours": hours,
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock upcoming games data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/recent")
async def get_recent_games(hours: int = Query(24, description="Hours back to look"), 
                        sport_id: int = Query(None, description="Sport ID to filter")):
    """Get recent games"""
    try:
        # Return mock recent games data for now
        mock_recent = [
            {
                "id": 1,
                "sport_id": 32,
                "external_game_id": "nfl_kc_buf_20260208",
                "home_team_id": 48,
                "away_team_id": 83,
                "home_team_name": "Kansas City Chiefs",
                "away_team_name": "Buffalo Bills",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 2,
                "sport_id": 32,
                "external_game_id": "nfl_phi_nyg_20260208",
                "home_team_id": 84,
                "away_team_id": 50,
                "home_team_name": "Philadelphia Eagles",
                "away_team_name": "New York Giants",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 3,
                "sport_id": 30,
                "external_game_id": "nba_lal_bos_20260208",
                "home_team_id": 17,
                "away_team_id": 27,
                "home_team_name": "Los Angeles Lakers",
                "away_team_name": "Boston Celtics",
                "sport_name": "NBA",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "season_id": 2026
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_recent = [g for g in mock_recent if g['sport_id'] == sport_id]
        
        return {
            "recent_games": mock_recent,
            "total": len(mock_recent),
            "hours": hours,
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock recent games data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/statistics")
async def get_games_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get games statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_games": 15,
            "final_games": 8,
            "scheduled_games": 7,
            "in_progress_games": 0,
            "cancelled_games": 0,
            "postponed_games": 0,
            "suspended_games": 0,
            "by_sport": [
                {
                    "sport_id": 32,
                    "total_games": 10,
                    "final_games": 6,
                    "scheduled_games": 4,
                    "in_progress_games": 0
                },
                {
                    "sport_id": 30,
                    "total_games": 5,
                    "final_games": 2,
                    "scheduled_games": 3,
                    "in_progress_games": 0
                }
            ],
            "by_date": [
                {
                    "date": "2026-02-08",
                    "total_games": 8,
                    "final_games": 5,
                    "scheduled_games": 3
                },
                {
                    "date": "2026-02-09",
                    "total_games": 7,
                    "final_games": 3,
                    "scheduled_games": 4
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock games statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/schedule")
async def get_game_schedule(start_date: str = Query(..., description="Start date (YYYY-MM-DD)"), 
                             end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
                             sport_id: int = Query(None, description="Sport ID to filter")):
    """Get game schedule for date range"""
    try:
        # Return mock schedule data for now
        mock_schedule = [
            {
                "id": 1,
                "sport_id": 32,
                "external_game_id": "nfl_kc_buf_20260208",
                "home_team_id": 48,
                "away_team_id": 83,
                "home_team_name": "Kansas City Chiefs",
                "away_team_name": "Buffalo Bills",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 2,
                "sport_id": 32,
                "external_game_id": "nfl_phi_nyg_20260208",
                "home_team_id": 84,
                "away_team_id": 50,
                "home_team_name": "Philadelphia Eagles",
                "away_team_name": "New York Giants",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "season_id": 2026
            },
            {
                "id": 3,
                "sport_id": 30,
                "external_game_id": "nba_lal_bos_20260208",
                "home_team_id": 17,
                "away_team_id": 27,
                "home_team_name": "Los Angeles Lakers",
                "away_team_name": "Boston Celtics",
                "sport_name": "NBA",
                "start_time": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "season_id": 2026
            }
        ]
        
        # Apply date and sport filters
        if sport_id:
            mock_schedule = [g for g in mock_schedule if g['sport_id'] == sport_id]
        
        if start_date and end_date:
            mock_schedule = [g for g in mock_schedule if start_date <= g['start_time'][:10] <= end_date]
        
        return {
            "schedule": mock_schedule,
            "start_date": start_date,
            "end_date": end_date,
            "sport_id": sport_id,
            "total": len(mock_schedule),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock game schedule data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/{game_id}")
async def get_game_detail(game_id: int):
    """Get detailed game information"""
    try:
        # Return mock detailed game data for now
        mock_detail = {
            "id": game_id,
            "sport_id": 32,
            "external_game_id": "nfl_kc_buf_20260208",
            "home_team_id": 48,
            "away_team_id": 83,
            "home_team_name": "Kansas City Chiefs",
            "away_team_name": "Buffalo Bills",
            "sport_name": "NFL",
            "start_time": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "status": "final",
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "season_id": 2026,
            "game_details": {
                "venue": "Arrowhead Stadium",
                "location": "Kansas City, MO",
                "attendance": 76416,
                "weather": "Clear, 72°F",
                "duration": "3:15:00",
                "broadcast": "CBS",
                "referees": ["John Smith", "Mike Johnson", "Bob Wilson"]
            },
            "betting_summary": {
                "total_bets": 15420,
                "total_wagered": 3084000,
                "total_profit": 185040,
                "roi_percent": 6.0,
                "popular_bets": {
                    "moneyline": "KC -145",
                    "spread": "KC -2.5",
                    "total": "Over 59.5"
                }
            }
        }
        
        return mock_detail
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/games/create")
async def create_game(game_data: dict):
    """Create a new game"""
    try:
        # Simulate creating a game
        game_id = game_data.get("game_id")
        external_game_id = game_data.get("external_game_id")
        home_team_id = game_data.get("home_team_id")
        away_team_id = game_data.get("away_team_id")
        start_time = game_data.get("start_time")
        
        if not all([game_id, external_game_id, home_team_id, away_team_id, start_time]):
            return {
                "status": "error",
                "error": "Missing required fields: game_id, external_game_id, home_team_id, away_team_id, start_time",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "status": "created",
            "game_id": game_id,
            "external_game_id": external_game_id,
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "start_time": start_time,
            "status": "scheduled",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock game created for {external_game_id}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.put("/games/{game_id}/status")
async def update_game_status(game_id: int, status: str = Query(..., description="New game status")):
    """Update game status"""
    try:
        # Simulate updating game status
        valid_statuses = ["scheduled", "in_progress", "final", "cancelled", "postponed", "suspended"]
        
        if status not in valid_statuses:
            return {
                "status": "error",
                "error": f"Invalid status: {status}. Valid statuses: {', '.join(valid_statuses)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "status": "updated",
            "game_id": game_id,
            "new_status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock game {game_id} status updated to {status}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/games/search")
async def search_games(query: str = Query(..., description="Search query"), 
                        sport_id: int = Query(None, description="Sport ID to filter"),
                        limit: int = Query(20, description="Number of results to return")):
    """Search games by external ID or team names"""
    try:
        # Return mock search results
        mock_results = [
            {
                "id": 1,
                "sport_id": 32,
                "external_game_id": "nfl_kc_buf_20260208",
                "home_team_id": 48,
                "away_team_id": 83,
                "home_team_name": "Kansas City Chiefs",
                "away_team_name": "Buffalo Bills",
                "sport_name": "NFL",
                "start_time": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "status": "final",
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "season_id": 2026
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                g for g in mock_results 
                if query_lower in g['external_game_id'].lower() or 
                   query_lower in g['home_team_name'].lower() or 
                   query_lower in g['away_team_name'].lower()
            ]
        
        # Apply sport filter
        if sport_id:
            mock_results = [g for g in mock_results if g['sport_id'] == sport_id]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "sport_id": sport_id,
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
        content = content.replace("# Brain Anomaly Detection Endpoints", games_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += games_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Games endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_games_endpoints())
