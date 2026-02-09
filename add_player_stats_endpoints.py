#!/usr/bin/env python3
"""
ADD PLAYER STATS ENDPOINTS - Add player statistics tracking endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_player_stats_endpoints():
    """Add player statistics tracking endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the player stats endpoints
    player_stats_code = '''

# Player Statistics Tracking Endpoints
@router.get("/player-stats")
async def get_player_stats(player: str = Query(None, description="Player name to filter"),
                             team: str = Query(None, description="Team name to filter"),
                             stat_type: str = Query(None, description="Stat type to filter"),
                             days: int = Query(30, description="Days of data to analyze"),
                             limit: int = Query(50, description="Number of stats to return")):
    """Get player statistics with optional filters"""
    try:
        # Return mock player stats data for now
        mock_stats = [
            {
                "id": 1,
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 27.5,
                "line": 24.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": "rebounds",
                "actual_value": 8.2,
                "line": 7.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 3,
                "player_name": "Stephen Curry",
                "team": "Golden State Warriors",
                "opponent": "Los Angeles Lakers",
                "date": (datetime.now(timezone.utc) - timedelta(days=2)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 31.2,
                "line": 28.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            },
            {
                "id": 4,
                "player_name": "Stephen Curry",
                "team": "Golden State Warriors",
                "opponent": "Los Angeles Lakers",
                "date": (datetime.now(timezone.utc) - timedelta(days=2)).date().isoformat(),
                "stat_type": "three_pointers",
                "actual_value": 4.5,
                "line": 4.0,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            },
            {
                "id": 5,
                "player_name": "Patrick Mahomes",
                "team": "Kansas City Chiefs",
                "opponent": "Buffalo Bills",
                "date": (datetime.now(timezone.utc) - timedelta(days=4)).date().isoformat(),
                "stat_type": "passing_yards",
                "actual_value": 298.5,
                "line": 285.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
            },
            {
                "id": 6,
                "player_name": "Patrick Mahomes",
                "team": "Kansas City Chiefs",
                "opponent": "Buffalo Bills",
                "date": (datetime.now(timezone.utc) - timedelta(days=4)).date().isoformat(),
                "stat_type": "passing_touchdowns",
                "actual_value": 3.0,
                "line": 2.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
            },
            {
                "id": 7,
                "player_name": "Aaron Judge",
                "team": "New York Yankees",
                "opponent": "Boston Red Sox",
                "date": (datetime.now(timezone.utc) - timedelta(days=6)).date().isoformat(),
                "stat_type": "home_runs",
                "actual_value": 2.0,
                "line": 1.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat()
            },
            {
                "id": 8,
                "player_name": "Mike Trout",
                "team": "Los Angeles Angels",
                "opponent": "Seattle Mariners",
                "date": (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat(),
                "stat_type": "hits",
                "actual_value": 2.0,
                "line": 1.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            },
            {
                "id": 9,
                "player_name": "Connor McDavid",
                "team": "Edmonton Oilers",
                "opponent": "Calgary Flames",
                "date": (datetime.now(timezone.utc) - timedelta(days=8)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 2.0,
                "line": 1.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
            },
            {
                "id": 10,
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "opponent": "Miami Heat",
                "date": datetime.now(timezone.utc).date().isoformat(),
                "stat_type": "points",
                "actual_value": 22.5,
                "line": 25.0,
                "result": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Apply filters
        filtered_stats = mock_stats
        if player:
            filtered_stats = [s for s in filtered_stats if player.lower() in s['player_name'].lower()]
        if team:
            filtered_stats = [s for s in filtered_stats if team.lower() in s['team'].lower()]
        if stat_type:
            filtered_stats = [s for s in filtered_stats if s['stat_type'].lower() == stat_type.lower()]
        
        return {
            "stats": filtered_stats[:limit],
            "total": len(filtered_stats),
            "filters": {
                "player": player,
                "team": team,
                "stat_type": stat_type,
                "days": days,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock player stats data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/player-statistics")
async def get_player_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get overall player statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_stats": 25,
            "unique_players": 8,
            "unique_teams": 8,
            "unique_opponents": 8,
            "unique_stat_types": 10,
            "unique_dates": 10,
            "avg_actual_value": 45.8,
            "avg_line": 42.3,
            "hits": 18,
            "misses": 7,
            "hit_rate_percentage": 72.0,
            "top_performers": [
                {
                    "player_name": "LeBron James",
                    "total_stats": 3,
                    "hits": 2,
                    "misses": 1,
                    "hit_rate_percentage": 66.67,
                    "avg_actual_value": 20.83,
                    "avg_line": 18.83,
                    "unique_stat_types": 3
                },
                {
                    "player_name": "Stephen Curry",
                    "total_stats": 2,
                    "hits": 2,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 17.85,
                    "avg_line": 16.25,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "Patrick Mahomes",
                    "total_stats": 2,
                    "hits": 2,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 300.75,
                    "avg_line": 289.0,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "Aaron Judge",
                    "total_stats": 2,
                    "hits": 2,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 2.5,
                    "avg_line": 2.0,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "Mike Trout",
                    "total_stats": 2,
                    "hits": 2,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 1.75,
                    "avg_line": 1.5,
                    "unique_stat_types": 2
                }
            ],
            "stat_type_performance": [
                {
                    "stat_type": "points",
                    "total_stats": 8,
                    "hits": 6,
                    "misses": 2,
                    "hit_rate_percentage": 75.0,
                    "avg_actual_value": 27.56,
                    "avg_line": 25.69,
                    "unique_players": 5
                },
                {
                    "stat_type": "passing_yards",
                    "total_stats": 2,
                    "hits": 2,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 287.2,
                    "avg_line": 280.5,
                    "unique_players": 2
                },
                {
                    "stat_type": "home_runs",
                    "total_stats": 1,
                    "hits": 1,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 2.0,
                    "avg_line": 1.5,
                    "unique_players": 1
                },
                {
                    "stat_type": "rebounds",
                    "total_stats": 2,
                    "hits": 1,
                    "misses": 1,
                    "hit_rate_percentage": 50.0,
                    "avg_actual_value": 7.35,
                    "avg_line": 7.25,
                    "unique_players": 1
                },
                {
                    "stat_type": "assists",
                    "total_stats": 1,
                    "hits": 1,
                    "misses": 0,
                    "hit_rate_percentage": 100.0,
                    "avg_actual_value": 7.8,
                    "avg_line": 6.5,
                    "unique_players": 1
                }
            ],
            "over_under_performance": [
                {
                    "over_under_result": "OVER",
                    "total_stats": 20,
                    "hits": 15,
                    "misses": 5,
                    "hit_rate_percentage": 75.0
                },
                {
                    "over_under_result": "UNDER",
                    "total_stats": 5,
                    "hits": 3,
                    "misses": 2,
                    "hit_rate_percentage": 60.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock player statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/player-stats/{player_name}")
async def get_player_stats_by_name(player_name: str, days: int = Query(30, description="Days of data to analyze")):
    """Get player statistics for a specific player"""
    try:
        # Return mock player stats data for now
        mock_player_stats = [
            {
                "id": 1,
                "player_name": player_name,
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 27.5,
                "line": 24.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "player_name": player_name,
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "stat_type": "rebounds",
                "actual_value": 8.2,
                "line": 7.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 10,
                "player_name": player_name,
                "team": "Los Angeles Lakers",
                "opponent": "Miami Heat",
                "date": datetime.now(timezone.utc).date().isoformat(),
                "stat_type": "points",
                "actual_value": 22.5,
                "line": 25.0,
                "result": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        return {
            "player_name": player_name,
            "stats": mock_player_stats,
            "total": len(mock_player_stats),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock player stats for {player_name}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_name": player_name,
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/player-stats/team/{team}")
async def get_player_stats_by_team(team: str, days: int = Query(30, description="Days of data to analyze")):
    """Get player statistics for a specific team"""
    try:
        # Return mock team stats data for now
        mock_team_stats = [
            {
                "id": 1,
                "player_name": "LeBron James",
                "team": team,
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 27.5,
                "line": 24.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "player_name": "LeBron James",
                "team": team,
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "stat_type": "rebounds",
                "actual_value": 8.2,
                "line": 7.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 3,
                "player_name": "Anthony Davis",
                "team": team,
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "stat_type": "points",
                "actual_value": 18.5,
                "line": 20.5,
                "result": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            }
        ]
        
        return {
            "team": team,
            "stats": mock_team_stats,
            "total": len(mock_team_stats),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock player stats for {team}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "team": team,
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/player-stats/stat/{stat_type}")
async def get_player_stats_by_stat_type(stat_type: str, days: int = Query(30, description="Days of data to analyze")):
    """Get player statistics for a specific stat type"""
    try:
        # Return mock stat type stats data for now
        mock_stat_stats = [
            {
                "id": 1,
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": stat_type,
                "actual_value": 27.5,
                "line": 24.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 3,
                "player_name": "Stephen Curry",
                "team": "Golden State Warriors",
                "opponent": "Los Angeles Lakers",
                "date": (datetime.now(timezone.utc) - timedelta(days=2)).date().isoformat(),
                "stat_type": stat_type,
                "actual_value": 31.2,
                "line": 28.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            },
            {
                "id": 5,
                "player_name": "Kevin Durant",
                "team": "Phoenix Suns",
                "opponent": "Denver Nuggets",
                "date": (datetime.now(timezone.utc) - timedelta(days=3)).date().isoformat(),
                "stat_type": stat_type,
                "actual_value": 25.8,
                "line": 26.5,
                "result": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            }
        ]
        
        return {
            "stat_type": stat_type,
            "stats": mock_stat_stats,
            "total": len(mock_stat_stats),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock player stats for {stat_type}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "stat_type": stat_type,
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/player-stats/search")
async def search_player_stats(query: str = Query(..., description="Search query"),
                              days: int = Query(30, description="Days of data to analyze"),
                              limit: int = Query(20, description="Number of results to return")):
    """Search player stats by player name, team, or stat type"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "player_name": "LeBron James",
                "team": "Los Angeles Lakers",
                "opponent": "Boston Celtics",
                "date": (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat(),
                "stat_type": "points",
                "actual_value": 27.5,
                "line": 24.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 5,
                "player_name": "Patrick Mahomes",
                "team": "Kansas City Chiefs",
                "opponent": "Buffalo Bills",
                "date": (datetime.now(timezone.utc) - timedelta(days=4)).date().isoformat(),
                "stat_type": "passing_yards",
                "actual_value": 298.5,
                "line": 285.5,
                "result": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['player_name'].lower() or 
                   query_lower in r['team'].lower() or
                   query_lower in r['opponent'].lower() or
                   query_lower in r['stat_type'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "days": days,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "days": days,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
'''
    
    # Add the endpoints before the anomaly endpoints
    if "# Brain Anomaly Detection Endpoints" in content:
        content = content.replace("# Brain Anomaly Detection Endpoints", player_stats_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += player_stats_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Player stats endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_player_stats_endpoints())
