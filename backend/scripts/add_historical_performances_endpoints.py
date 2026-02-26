#!/usr/bin/env python3
"""
ADD HISTORICAL PERFORMANCES ENDPOINTS - Add historical performance tracking endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_historical_performances_endpoints():
    """Add historical performance tracking endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the historical performance endpoints
    historical_performance_code = '''

# Historical Performance Tracking Endpoints
@router.get("/historical-performances")
async def get_historical_performances(player: str = Query(None, description="Player name to filter"), 
                                      stat_type: str = Query(None, description="Stat type to filter"),
                                      limit: int = Query(50, description="Number of performances to return")):
    """Get historical performances with optional filters"""
    try:
        # Return mock historical performance data for now
        mock_performances = [
            {
                "id": 1,
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_yards",
                "total_picks": 156,
                "hits": 98,
                "misses": 58,
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0842,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "total_picks": 89,
                "hits": 62,
                "misses": 27,
                "hit_rate_percentage": 69.66,
                "avg_ev": 0.0921,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 3,
                "player_name": "Josh Allen",
                "stat_type": "passing_yards",
                "total_picks": 142,
                "hits": 87,
                "misses": 55,
                "hit_rate_percentage": 61.27,
                "avg_ev": 0.0789,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 4,
                "player_name": "LeBron James",
                "stat_type": "points",
                "total_picks": 178,
                "hits": 112,
                "misses": 66,
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0768,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 5,
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "total_picks": 189,
                "hits": 121,
                "misses": 68,
                "hit_rate_percentage": 64.02,
                "avg_ev": 0.0934,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 6,
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "total_picks": 89,
                "hits": 56,
                "misses": 33,
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0912,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 7,
                "player_name": "Brain System",
                "stat_type": "overall_predictions",
                "total_picks": 1245,
                "hits": 789,
                "misses": 456,
                "hit_rate_percentage": 63.38,
                "avg_ev": 0.0823,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 8,
                "player_name": "Sam Darnold",
                "stat_type": "passing_yards",
                "total_picks": 45,
                "hits": 22,
                "misses": 23,
                "hit_rate_percentage": 48.89,
                "avg_ev": -0.0234,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_performances = mock_performances
        if player:
            filtered_performances = [p for p in filtered_performances if player.lower() in p['player_name'].lower()]
        if stat_type:
            filtered_performances = [p for p in filtered_performances if stat_type.lower() in p['stat_type'].lower()]
        
        return {
            "performances": filtered_performances[:limit],
            "total": len(filtered_performances),
            "filters": {
                "player": player,
                "stat_type": stat_type,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock historical performance data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/top")
async def get_top_performers(limit: int = Query(10, description="Number of top performers to return"), 
                               stat_type: str = Query(None, description="Stat type to filter")):
    """Get top performers by hit rate"""
    try:
        # Return mock top performers data
        mock_top_performers = [
            {
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "hit_rate_percentage": 64.02,
                "avg_ev": 0.0934,
                "total_picks": 189,
                "hits": 121,
                "misses": 68
            },
            {
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "hit_rate_percentage": 69.66,
                "avg_ev": 0.0921,
                "total_picks": 89,
                "hits": 62,
                "misses": 27
            },
            {
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0912,
                "total_picks": 89,
                "hits": 56,
                "misses": 33
            },
            {
                "player_name": "LeBron James",
                "stat_type": "points",
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0768,
                "total_picks": 178,
                "hits": 112,
                "misses": 66
            },
            {
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_yards",
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0842,
                "total_picks": 156,
                "hits": 98,
                "misses": 58
            },
            {
                "player_name": "Brain System",
                "stat_type": "overall_predictions",
                "hit_rate_percentage": 63.38,
                "avg_ev": 0.0823,
                "total_picks": 1245,
                "hits": 789,
                "misses": 456
            },
            {
                "player_name": "Josh Allen",
                "stat_type": "passing_yards",
                "hit_rate_percentage": 61.27,
                "avg_ev": 0.0789,
                "total_picks": 142,
                "hits": 87,
                "misses": 55
            },
            {
                "player_name": "Lamar Jackson",
                "stat_type": "rushing_yards",
                "hit_rate_percentage": 62.24,
                "avg_ev": 0.0897,
                "total_picks": 98,
                "hits": 61,
                "misses": 37
            },
            {
                "player_name": "Kevin Durant",
                "stat_type": "points",
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0811,
                "total_picks": 156,
                "hits": 98,
                "misses": 58
            },
            {
                "player_name": "Stephen Curry",
                "stat_type": "three_pointers",
                "hit_rate_percentage": 61.68,
                "avg_ev": 0.0889,
                "total_picks": 167,
                "hits": 103,
                "misses": 64
            }
        ]
        
        # Apply stat type filter
        if stat_type:
            mock_top_performers = [p for p in mock_top_performers if p['stat_type'] == stat_type]
        
        return {
            "top_performers": mock_top_performers[:limit],
            "total": len(mock_top_performers),
            "limit": limit,
            "stat_type": stat_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock top performers data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/best-ev")
async def get_best_ev_performers(limit: int = Query(10, description="Number of best EV performers to return"), 
                                   stat_type: str = Query(None, description="Stat type to filter")):
    """Get best performers by expected value"""
    try:
        # Return mock best EV performers data
        mock_best_ev = [
            {
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "hit_rate_percentage": 64.02,
                "avg_ev": 0.0934,
                "total_picks": 189,
                "hits": 121,
                "misses": 68
            },
            {
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "hit_rate_percentage": 69.66,
                "avg_ev": 0.0921,
                "total_picks": 89,
                "hits": 62,
                "misses": 27
            },
            {
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0912,
                "total_picks": 89,
                "hits": 56,
                "misses": 33
            },
            {
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_yards",
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0842,
                "total_picks": 156,
                "hits": 98,
                "misses": 58
            },
            {
                "player_name": "Brain System",
                "stat_type": "overall_predictions",
                "hit_rate_percentage": 63.38,
                "avg_ev": 0.0823,
                "total_picks": 1245,
                "hits": 789,
                "misses": 456
            },
            {
                "player_name": "Lamar Jackson",
                "stat_type": "rushing_yards",
                "hit_rate_percentage": 62.24,
                "avg_ev": 0.0897,
                "total_picks": 98,
                "hits": 61,
                "misses": 37
            },
            {
                "player_name": "Stephen Curry",
                "stat_type": "three_pointers",
                "hit_rate_percentage": 61.68,
                "avg_ev": 0.0889,
                "total_picks": 167,
                "hits": 103,
                "misses": 64
            },
            {
                "player_name": "Josh Allen",
                "stat_type": "passing_yards",
                "hit_rate_percentage": 61.27,
                "avg_ev": 0.0789,
                "total_picks": 142,
                "hits": 87,
                "misses": 55
            },
            {
                "player_name": "Kevin Durant",
                "stat_type": "points",
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0811,
                "total_picks": 156,
                "hits": 98,
                "misses": 58
            },
            {
                "player_name": "LeBron James",
                "stat_type": "points",
                "hit_rate_percentage": 62.92,
                "avg_ev": 0.0768,
                "total_picks": 178,
                "hits": 112,
                "misses": 66
            }
        ]
        
        # Apply stat type filter
        if stat_type:
            mock_best_ev = [p for p in mock_best_ev if p['stat_type'] == stat_type]
        
        return {
            "best_ev_performers": mock_best_ev[:limit],
            "total": len(mock_best_ev),
            "limit": limit,
            "stat_type": stat_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock best EV performers data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/worst")
async def get_worst_performers(limit: int = Query(10, description="Number of worst performers to return"), 
                                  stat_type: str = Query(None, description="Stat type to filter")):
    """Get worst performers by hit rate"""
    try:
        # Return mock worst performers data
        mock_worst = [
            {
                "player_name": "Russell Westbrook",
                "stat_type": "field_goal_percentage",
                "hit_rate_percentage": 46.27,
                "avg_ev": -0.0345,
                "total_picks": 67,
                "hits": 31,
                "misses": 36
            },
            {
                "player_name": "Mookie Betts",
                "stat_type": "batting_average",
                "hit_rate_percentage": 46.15,
                "avg_ev": -0.0289,
                "total_picks": 78,
                "hits": 36,
                "misses": 42
            },
            {
                "player_name": "Sam Darnold",
                "stat_type": "passing_yards",
                "hit_rate_percentage": 48.89,
                "avg_ev": -0.0234,
                "total_picks": 45,
                "hits": 22,
                "misses": 23
            },
            {
                "player_name": "Shohei Ohtani",
                "stat_type": "home_runs",
                "hit_rate_percentage": 61.54,
                "avg_ev": 0.0834,
                "total_picks": 78,
                "hits": 48,
                "misses": 30
            },
            {
                "player_name": "Shohei Ohtani",
                "stat_type": "strikeouts",
                "hit_rate_percentage": 61.96,
                "avg_ev": 0.0798,
                "total_picks": 92,
                "hits": 57,
                "misses": 35
            }
        ]
        
        # Apply stat type filter
        if stat_type:
            mock_worst = [p for p in mock_worst if p['stat_type'] == stat_type]
        
        return {
            "worst_performers": mock_worst[:limit],
            "total": len(mock_worst),
            "limit": limit,
            "stat_type": stat_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock worst performers data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/statistics")
async def get_performance_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get performance statistics"""
    try:
        # Return mock statistics data
        mock_stats = {
            "period_days": days,
            "total_performances": 21,
            "unique_players": 11,
            "unique_stat_types": 12,
            "avg_hit_rate": 59.87,
            "avg_ev": 0.0634,
            "total_picks_all": 2478,
            "total_hits_all": 1483,
            "total_misses_all": 995,
            "by_stat_type": [
                {
                    "stat_type": "passing_touchdowns",
                    "total_performances": 1,
                    "avg_hit_rate": 69.66,
                    "avg_ev": 0.0921,
                    "total_picks": 89,
                    "total_hits": 62,
                    "unique_players": 1
                },
                {
                    "stat_type": "points",
                    "total_performances": 3,
                    "avg_hit_rate": 63.25,
                    "avg_ev": 0.0838,
                    "total_picks": 523,
                    "total_hits": 331,
                    "unique_players": 3
                },
                {
                    "stat_type": "home_runs",
                    "total_performances": 2,
                    "avg_hit_rate": 62.23,
                    "avg_ev": 0.0873,
                    "total_picks": 167,
                    "total_hits": 104,
                    "unique_players": 2
                },
                {
                    "stat_type": "passing_yards",
                    "total_performances": 3,
                    "avg_hit_rate": 57.66,
                    "avg_ev": 0.0466,
                    "total_picks": 343,
                    "total_hits": 207,
                    "unique_players": 3
                },
                {
                    "stat_type": "overall_predictions",
                    "total_performances": 4,
                    "avg_hit_rate": 62.90,
                    "avg_ev": 0.0807,
                    "total_picks": 2180,
                    "total_hits": 1370,
                    "unique_players": 1
                }
            ],
            "by_player": [
                {
                    "player_name": "Patrick Mahomes",
                    "total_performances": 2,
                    "avg_hit_rate": 66.24,
                    "avg_ev": 0.0882,
                    "total_picks": 245,
                    "total_hits": 160,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "Stephen Curry",
                    "total_performances": 2,
                    "avg_hit_rate": 62.85,
                    "avg_ev": 0.0912,
                    "total_picks": 356,
                    "total_hits": 224,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "Brain System",
                    "total_performances": 4,
                    "avg_hit_rate": 62.90,
                    "avg_ev": 0.0807,
                    "total_picks": 2180,
                    "total_hits": 1370,
                    "unique_stat_types": 4
                },
                {
                    "player_name": "Josh Allen",
                    "total_performances": 2,
                    "avg_hit_rate": 61.23,
                    "avg_ev": 0.0802,
                    "total_picks": 209,
                    "total_hits": 128,
                    "unique_stat_types": 2
                },
                {
                    "player_name": "LeBron James",
                    "total_performances": 2,
                    "avg_hit_rate": 62.15,
                    "avg_ev": 0.0755,
                    "total_picks": 323,
                    "total_hits": 201,
                    "unique_stat_types": 2
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock performance statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/player/{player_name}")
async def get_player_performance(player_name: str, stat_type: str = Query(None, description="Stat type to filter")):
    """Get performance for a specific player"""
    try:
        # Return mock player performance data
        mock_player_data = {
            "player_name": player_name,
            "performances": [
                {
                    "id": 1,
                    "stat_type": "passing_yards",
                    "total_picks": 156,
                    "hits": 98,
                    "misses": 58,
                    "hit_rate_percentage": 62.82,
                    "avg_ev": 0.0842,
                    "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
                },
                {
                    "id": 2,
                    "stat_type": "passing_touchdowns",
                    "total_picks": 89,
                    "hits": 62,
                    "misses": 27,
                    "hit_rate_percentage": 69.66,
                    "avg_ev": 0.0921,
                    "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
                }
            ],
            "summary": {
                "total_performances": 2,
                "avg_hit_rate": 66.24,
                "avg_ev": 0.0882,
                "total_picks": 245,
                "total_hits": 160,
                "total_misses": 85,
                "unique_stat_types": 2
            }
        }
        
        # Apply stat type filter
        if stat_type:
            mock_player_data["performances"] = [p for p in mock_player_data["performances"] if p["stat_type"] == stat_type]
        
        return {
            "player_name": player_name,
            "performances": mock_player_data["performances"],
            "summary": mock_player_data["summary"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock performance data for {player_name}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/historical-performances/search")
async def search_performances(query: str = Query(..., description="Search query"), 
                               limit: int = Query(20, description="Number of results to return")):
    """Search performances by player name or stat type"""
    try:
        # Return mock search results
        mock_results = [
            {
                "id": 1,
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_yards",
                "total_picks": 156,
                "hits": 98,
                "misses": 58,
                "hit_rate_percentage": 62.82,
                "avg_ev": 0.0842,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                p for p in mock_results 
                if query_lower in p['player_name'].lower() or 
                   query_lower in p['stat_type'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
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
        content = content.replace("# Brain Anomaly Detection Endpoints", historical_performance_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += historical_performance_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Historical performances endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_historical_performances_endpoints())
