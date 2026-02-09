#!/usr/bin/env python3
"""
ADD LINE TRACKING ENDPOINTS - Add line tracking endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_line_endpoints():
    """Add line tracking endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the line tracking endpoints
    line_code = '''

# Line Tracking Endpoints
@router.get("/lines")
async def get_lines(game_id: int = Query(None, description="Game ID to filter"), 
                   player_id: int = Query(None, description="Player ID to filter"),
                   sportsbook: str = Query(None, description="Sportsbook to filter"),
                   is_current: bool = Query(None, description="Filter current lines only"),
                   limit: int = Query(50, description="Number of lines to return")):
    """Get betting lines with optional filters"""
    try:
        # Return mock line data for now
        mock_lines = [
            {
                "id": 759109,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759110,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "under",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759111,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 15.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759112,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 15.5,
                "odds": -110,
                "side": "under",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759113,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 16.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759114,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 16.5,
                "odds": -110,
                "side": "under",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759115,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 14.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759116,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 14.5,
                "odds": -110,
                "side": "under",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759117,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 12.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759118,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 12.5,
                "odds": -110,
                "side": "under",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_lines = mock_lines
        if game_id:
            filtered_lines = [l for l in filtered_lines if l['game_id'] == game_id]
        if player_id:
            filtered_lines = [l for l in filtered_lines if l['player_id'] == player_id]
        if sportsbook:
            filtered_lines = [l for l in filtered_lines if l['sportsbook'].lower() == sportsbook.lower()]
        if is_current is not None:
            filtered_lines = [l for l in filtered_lines if l['is_current'] == is_current]
        
        return {
            "lines": filtered_lines[:limit],
            "total": len(filtered_lines),
            "filters": {
                "game_id": game_id,
                "player_id": player_id,
                "sportsbook": sportsbook,
                "is_current": is_current,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock line data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/current")
async def get_current_lines(game_id: int = Query(None, description="Game ID to filter"), 
                            player_id: int = Query(None, description="Player ID to filter")):
    """Get current betting lines"""
    try:
        # Return mock current lines data for now
        mock_current = [
            {
                "id": 759119,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759120,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "under",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759121,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759122,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "under",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759123,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759124,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "under",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759125,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "draftkings",
                "line_value": 28.5,
                "odds": -110,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759126,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "draftkings",
                "line_value": 28.5,
                "odds": -110,
                "side": "under",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759127,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "fanduel",
                "line_value": 29.0,
                "odds": -108,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759128,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "fanduel",
                "line_value": 29.0,
                "odds": -108,
                "side": "under",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            }
        ]
        
        # Apply filters
        if game_id:
            mock_current = [l for l in mock_current if l['game_id'] == game_id]
        if player_id:
            mock_current = [l for l in mock_current if l['player_id'] == player_id]
        
        return {
            "current_lines": mock_current,
            "total": len(mock_current),
            "game_id": game_id,
            "player_id": player_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock current lines data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "player_id": player_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/movements/{game_id}/{player_id}")
async def get_line_movements(game_id: int, player_id: int, market_id: int = Query(None, description="Market ID to filter")):
    """Get line movements for a specific game/player"""
    try:
        # Return mock line movements data for now
        mock_movements = [
            {
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            },
            {
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            },
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -110,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "line_movement": 0.5,
                "odds_movement": 0,
                "prev_line_value": 13.5,
                "prev_odds": -110
            },
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -110,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "line_movement": 0.5,
                "odds_movement": 0,
                "prev_line_value": 13.5,
                "prev_odds": -110
            },
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 5,
                "prev_line_value": 14.0,
                "prev_odds": -110
            },
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 5,
                "prev_line_value": 14.0,
                "prev_odds": -110
            },
            {
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            },
            {
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            },
            {
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            },
            {
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "line_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_odds": None
            }
        ]
        
        # Apply market filter
        if market_id:
            mock_movements = [m for m in mock_movements if m['sportsbook'] == 'draftkings'] or m['sportsbook'] == 'fanduel']
        
        return {
            "game_id": game_id,
            "player_id": player_id,
            "movements": mock_movements,
            "total_movements": len(mock_movements),
            "market_id": market_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock line movements for game {game_id}, player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "player_id": player_id,
            "market_id": market_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/comparison/{game_id}/{player_id}")
async def get_sportsbook_comparison(game_id: int, player_id: int, market_id: int = Query(None, description="Market ID to filter")):
    """Compare lines across sportsbooks"""
    try:
        # Return mock comparison data for now
        mock_comparison = [
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "sportsbook": "draftkings",
                "line_value": 14.0,
                "odds": -105,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "sportsbook": "fanduel",
                "line_value": 13.5,
                "odds": -108,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "over",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "sportsbook": "betmgm",
                "line_value": 14.5,
                "odds": -110,
                "side": "under",
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            }
        ]
        
        # Calculate best odds
        best_over = max(mock_comparison, key=lambda x: x['odds'] if x['side'] == 'over' else float('inf'))
        best_under = max(mock_comparison, key=lambda x: x['odds'] if x['side'] == 'under' else float('inf'))
        
        return {
            "game_id": game_id,
            "player_id": player_id,
            "comparison": mock_comparison,
            "best_over_odds": {
                "sportsbook": best_over['sportsbook'],
                "line_value": best_over['line_value'],
                "odds": best_over['odds'],
                "side": best_over['side']
            },
            "best_under_odds": {
                "sportsbook": best_under['sportsbook'],
                "line_value": best_under['line_value'],
                "odds": best_under['odds'],
                "side": best_under['side']
            },
            "total_sportsbooks": len(set(c['sportsbook'] for c in mock_comparison)),
            "market_id": market_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock sportsbook comparison for game {game_id}, player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "player_id": player_id,
            "market_id": market_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/statistics")
async def get_line_statistics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get line statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_hours": hours,
            "total_lines": 24,
            "unique_games": 4,
            "unique_markets": 6,
            "unique_players": 4,
            "unique_sportsbooks": 3,
            "current_lines": 10,
            "historical_lines": 14,
            "avg_line_value": 20.25,
            "avg_odds": -108,
            "over_lines": 12,
            "under_lines": 12,
            "by_sportsbook": [
                {
                    "sportsbook": "draftkings",
                    "total_lines": 10,
                    "current_lines": 4,
                    "unique_games": 4,
                    "unique_players": 4,
                    "avg_line_value": 18.5,
                    "avg_odds": -108,
                    "over_lines": 5,
                    "under_lines": 5
                },
                {
                    "sportsbook": "fanduel",
                    "total_lines": 8,
                    "current_lines": 4,
                    "unique_games": 3,
                    "unique_players": 3,
                    "avg_line_value": 21.25,
                    "avg_odds": -108,
                    "over_lines": 4,
                    "under_lines": 4
                },
                {
                    "sportsbook": "betmgm",
                    "total_lines": 6,
                    "current_lines": 2,
                    "unique_games": 2,
                    "unique_players": 2,
                    "avg_line_value": 22.0,
                    "avg_odds": -110,
                    "over_lines": 3,
                    "under_lines": 3
                }
            ],
            "by_side": [
                {
                    "side": "over",
                    "total_lines": 12,
                    "avg_line_value": 20.25,
                    "avg_odds": -108,
                    "unique_sportsbooks": 3,
                    "unique_players": 4
                },
                {
                    "side": "under",
                    "total_lines": 12,
                    "avg_line_value": 20.25,
                    "avg_odds": -108,
                    "unique_sportsbooks": 3,
                    "unique_players": 4
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock line statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/efficiency")
async def get_line_efficiency(hours: int = Query(24, description="Hours of data to analyze")):
    """Analyze line efficiency and market efficiency"""
    try:
        # Return mock efficiency analysis data for now
        mock_efficiency = {
            "period_hours": hours,
            "sportsbook_efficiency": [
                {
                    "sportsbook": "draftkings",
                    "total_lines": 10,
                    "significant_movements": 3,
                    "movement_rate": 30.0,
                    "avg_movement": 0.75,
                    "unique_games": 4,
                    "unique_players": 4,
                    "efficiency_score": 70.0
                },
                {
                    "sportsbook": "fanduel",
                    "total_lines": 8,
                    "significant_movements": 2,
                    "movement_rate": 25.0,
                    "avg_movement": 0.5,
                    "unique_games": 3,
                    "unique_players": 3,
                    "efficiency_score": 75.0
                },
                {
                    "sportsbook": "betmgm",
                    "total_lines": 6,
                    "significant_movements": 1,
                    "movement_rate": 16.7,
                    "avg_movement": 0.3,
                    "unique_games": 2,
                    "unique_players": 2,
                    "efficiency_score": 83.3
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock line efficiency analysis data"
        }
        
        return mock_efficiency
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/search")
async def search_lines(query: str = Query(..., description="Search query"), 
                       sportsbook: str = Query(None, description="Sportsbook to filter"),
                       limit: int = Query(20, description="Number of results to return")):
    """Search lines by player ID or sportsbook"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 759109,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759125,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "draftkings",
                "line_value": 28.5,
                "odds": -110,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759129,
                "game_id": 664,
                "market_id": 101,
                "player_id": 101,
                "sportsbook": "draftkings",
                "line_value": 285.5,
                "odds": -110,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            }
        ]
        
        # Apply filters
        if sportsbook:
            mock_results = [r for r in mock_results if r['sportsbook'].lower() == sportsbook.lower()]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in str(r['player_id']) or 
                   query_lower in r['sportsbook'].lower()
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
            "query": query,
            "sportsbook": sportsbook,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
'''
    
    # Add the endpoints before the anomaly endpoints
    if "# Brain Anomaly Detection Endpoints" in content:
        content = content.replace("# Brain Anomaly Detection Endpoints", line_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += line_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Line tracking endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_line_endpoints())
