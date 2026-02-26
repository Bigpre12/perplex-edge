#!/usr/bin/env python3
"""
ADD PICKS ENDPOINTS - Add picks management endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_picks_endpoints():
    """Add picks management endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the picks endpoints
    picks_code = '''

# Picks Management Endpoints
@router.get("/picks")
async def get_picks(game_id: int = Query(None, description="Game ID to filter"), 
                  player: str = Query(None, description="Player name to filter"),
                  stat_type: str = Query(None, description="Stat type to filter"),
                  min_ev: float = Query(0.0, description="Minimum EV percentage"),
                  min_confidence: float = Query(0.0, description="Minimum confidence"),
                  hours: int = Query(24, description="Hours of data to analyze"),
                  limit: int = Query(50, description="Number of picks to return")):
    """Get picks with optional filters"""
    try:
        # Return mock picks data for now
        mock_picks = [
            {
                "id": 1,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 2,
                "game_id": 664,
                "pick_type": "player_prop",
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "line": 2.5,
                "odds": -108,
                "model_probability": 0.6300,
                "implied_probability": 0.5195,
                "ev_percentage": 21.28,
                "confidence": 91.0,
                "hit_rate": 66.8,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat()
            },
            {
                "id": 3,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "line": 1.5,
                "odds": -105,
                "model_probability": 0.6100,
                "implied_probability": 0.5122,
                "ev_percentage": 19.09,
                "confidence": 87.0,
                "hit_rate": 63.5,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=10).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=10).isoformat()
            },
            {
                "id": 4,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "LeBron James",
                "stat_type": "points",
                "line": 25.0,
                "odds": -108,
                "model_probability": 0.6100,
                "implied_probability": 0.5195,
                "ev_percentage": 17.40,
                "confidence": 89.0,
                "hit_rate": 64.1,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 5,
                "game_id": 668,
                "pick_type": "player_prop",
                "player_name": "Connor McDavid",
                "stat_type": "points",
                "line": 1.5,
                "odds": -108,
                "model_probability": 0.6000,
                "implied_probability": 0.5195,
                "ev_percentage": 15.40,
                "confidence": 85.0,
                "hit_rate": 62.8,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 6,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 28.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.0,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 7,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Kevin Durant",
                "stat_type": "points",
                "line": 26.5,
                "odds": -108,
                "model_probability": 0.5900,
                "implied_probability": 0.5195,
                "ev_percentage": 13.58,
                "confidence": 86.0,
                "hit_rate": 63.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 8,
                "game_id": 664,
                "pick_type": "player_prop",
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_yards",
                "line": 285.5,
                "odds": -110,
                "model_probability": 0.5800,
                "implied_probability": 0.5238,
                "ev_percentage": 10.75,
                "confidence": 84.0,
                "hit_rate": 63.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=3).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=3).isoformat()
            },
            {
                "id": 9,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "line": 1.5,
                "odds": -110,
                "model_probability": 0.5900,
                "implied_probability": 0.5238,
                "ev_percentage": 12.61,
                "confidence": 85.0,
                "hit_rate": 62.9,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat()
            },
            {
                "id": 10,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Mike Trout",
                "stat_type": "hits",
                "line": 1.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat()
            }
        ]
        
        # Apply filters
        filtered_picks = mock_picks
        if game_id:
            filtered_picks = [p for p in filtered_picks if p['game_id'] == game_id]
        if player:
            filtered_picks = [p for p in filtered_picks if player.lower() in p['player_name'].lower()]
        if stat_type:
            filtered_picks = [p for p in filtered_picks if p['stat_type'].lower() == stat_type.lower()]
        if min_ev > 0:
            filtered_picks = [p for p in filtered_picks if p['ev_percentage'] >= min_ev]
        if min_confidence > 0:
            filtered_picks = [p for p in filtered_picks if p['confidence'] >= min_confidence]
        
        return {
            "picks": filtered_picks[:limit],
            "total": len(filtered_picks),
            "filters": {
                "game_id": game_id,
                "player": player,
                "stat_type": stat_type,
                "min_ev": min_ev,
                "min_confidence": min_confidence,
                "hours": hours,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock picks data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/high-ev")
async def get_high_ev_picks(min_ev: float = Query(5.0, description="Minimum EV percentage"),
                           hours: int = Query(24, description="Hours of data to analyze"),
                           limit: int = Query(20, description="Number of picks to return")):
    """Get picks with high expected value"""
    try:
        # Return mock high EV picks data for now
        mock_high_ev = [
            {
                "id": 2,
                "game_id": 664,
                "pick_type": "player_prop",
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "line": 2.5,
                "odds": -108,
                "model_probability": 0.6300,
                "implied_probability": 0.5195,
                "ev_percentage": 21.28,
                "confidence": 91.0,
                "hit_rate": 66.8,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat()
            },
            {
                "id": 1,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 3,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Aaron Judge",
                "stat_type": "home_runs",
                "line": 1.5,
                "odds": -105,
                "model_probability": 0.6100,
                "implied_probability": 0.5122,
                "ev_percentage": 19.09,
                "confidence": 87.0,
                "hit_rate": 63.5,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=10).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=10).isoformat()
            },
            {
                "id": 6,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 28.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.0,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 10,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Mike Trout",
                "stat_type": "hits",
                "line": 1.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat()
            }
        ]
        
        # Apply EV filter
        filtered_picks = [p for p in mock_high_ev if p['ev_percentage'] >= min_ev]
        
        return {
            "high_ev_picks": filtered_picks[:limit],
            "total": len(filtered_picks),
            "min_ev": min_ev,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock high EV picks (>= {min_ev}% EV)"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "min_ev": min_ev,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/high-confidence")
async def get_high_confidence_picks(min_confidence: float = Query(80.0, description="Minimum confidence"),
                                   hours: int = Query(24, description="Hours of data to analyze"),
                                   limit: int = Query(20, description="Number of picks to return")):
    """Get picks with high confidence"""
    try:
        # Return mock high confidence picks data for now
        mock_high_confidence = [
            {
                "id": 2,
                "game_id": 664,
                "pick_type": "player_prop",
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "line": 2.5,
                "odds": -108,
                "model_probability": 0.6300,
                "implied_probability": 0.5195,
                "ev_percentage": 21.28,
                "confidence": 91.0,
                "hit_rate": 66.8,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat()
            },
            {
                "id": 1,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 4,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "LeBron James",
                "stat_type": "points",
                "line": 25.0,
                "odds": -108,
                "model_probability": 0.6100,
                "implied_probability": 0.5195,
                "ev_percentage": 17.40,
                "confidence": 89.0,
                "hit_rate": 64.1,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 6,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 28.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.0,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 10,
                "game_id": 666,
                "pick_type": "player_prop",
                "player_name": "Mike Trout",
                "stat_type": "hits",
                "line": 1.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=4).isoformat()
            }
        ]
        
        # Apply confidence filter
        filtered_picks = [p for p in mock_high_confidence if p['confidence'] >= min_confidence]
        
        return {
            "high_confidence_picks": filtered_picks[:limit],
            "total": len(filtered_picks),
            "min_confidence": min_confidence,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock high confidence picks (>= {min_confidence}% confidence)"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "min_confidence": min_confidence,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/statistics")
async def get_picks_statistics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get picks statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_hours": hours,
            "total_picks": 22,
            "unique_games": 4,
            "unique_players": 8,
            "unique_stat_types": 6,
            "unique_pick_types": 1,
            "avg_line": 45.8,
            "avg_odds": -110,
            "avg_model_prob": 0.5950,
            "avg_implied_prob": 0.5238,
            "avg_ev": 11.23,
            "avg_confidence": 84.5,
            "avg_hit_rate": 63.4,
            "high_ev_picks": 18,
            "high_confidence_picks": 16,
            "high_hit_rate_picks": 20,
            "by_player": [
                {
                    "player_name": "Patrick Mahomes",
                    "total_picks": 2,
                    "avg_ev": 15.52,
                    "avg_confidence": 87.5,
                    "avg_hit_rate": 65.0,
                    "avg_model_prob": 0.6050,
                    "avg_implied_prob": 0.5217,
                    "high_ev_picks": 2,
                    "high_confidence_picks": 2
                },
                {
                    "player_name": "Stephen Curry",
                    "total_picks": 3,
                    "avg_ev": 16.91,
                    "avg_confidence": 88.7,
                    "avg_hit_rate": 64.4,
                    "avg_model_prob": 0.6233,
                    "avg_implied_prob": 0.5295,
                    "high_ev_picks": 3,
                    "high_confidence_picks": 3
                },
                {
                    "player_name": "Aaron Judge",
                    "total_picks": 2,
                    "avg_ev": 15.85,
                    "avg_confidence": 86.0,
                    "avg_hit_rate": 63.2,
                    "avg_model_prob": 0.6000,
                    "avg_implied_prob": 0.5180,
                    "high_ev_picks": 2,
                    "high_confidence_picks": 2
                },
                {
                    "player_name": "LeBron James",
                    "total_picks": 2,
                    "avg_ev": 13.49,
                    "avg_confidence": 87.0,
                    "avg_hit_rate": 63.3,
                    "avg_model_prob": 0.5950,
                    "avg_implied_prob": 0.5217,
                    "high_ev_picks": 2,
                    "high_confidence_picks": 2
                }
            ],
            "by_stat_type": [
                {
                    "stat_type": "points",
                    "total_picks": 8,
                    "avg_ev": 16.47,
                    "avg_confidence": 87.9,
                    "avg_hit_rate": 64.1,
                    "avg_model_prob": 0.6163,
                    "avg_implied_prob": 0.5257,
                    "high_ev_picks": 8
                },
                {
                    "stat_type": "passing_touchdowns",
                    "total_picks": 1,
                    "avg_ev": 21.28,
                    "avg_confidence": 91.0,
                    "avg_hit_rate": 66.8,
                    "avg_model_prob": 0.6300,
                    "avg_implied_prob": 0.5195,
                    "high_ev_picks": 1
                },
                {
                    "stat_type": "home_runs",
                    "total_picks": 2,
                    "avg_ev": 15.85,
                    "avg_confidence": 86.0,
                    "avg_hit_rate": 63.2,
                    "avg_model_prob": 0.6000,
                    "avg_implied_prob": 0.5180,
                    "high_ev_picks": 2
                },
                {
                    "stat_type": "hits",
                    "total_picks": 1,
                    "avg_ev": 15.92,
                    "avg_confidence": 88.0,
                    "avg_hit_rate": 64.2,
                    "avg_model_prob": 0.6200,
                    "avg_implied_prob": 0.5349,
                    "high_ev_picks": 1
                },
                {
                    "stat_type": "passing_yards",
                    "total_picks": 1,
                    "avg_ev": 10.75,
                    "avg_confidence": 84.0,
                    "avg_hit_rate": 63.2,
                    "avg_model_prob": 0.5800,
                    "avg_implied_prob": 0.5238,
                    "high_ev_picks": 1
                },
                {
                    "stat_type": "rebounds",
                    "total_picks": 1,
                    "avg_ev": 9.34,
                    "avg_confidence": 82.0,
                    "avg_hit_rate": 61.1,
                    "avg_model_prob": 0.5600,
                    "avg_implied_prob": 0.5122,
                    "high_ev_picks": 1
                }
            ],
            "ev_distribution": [
                {
                    "ev_category": "Very High EV (15%+)",
                    "total_picks": 8,
                    "avg_ev": 17.89,
                    "avg_confidence": 88.8,
                    "avg_hit_rate": 64.6
                },
                {
                    "ev_category": "High EV (10-15%)",
                    "total_picks": 10,
                    "avg_ev": 12.17,
                    "avg_confidence": 83.2,
                    "avg_hit_rate": 62.8
                },
                {
                    "ev_category": "Medium EV (5-10%)",
                    "total_picks": 4,
                    "avg_ev": 7.52,
                    "avg_confidence": 80.5,
                    "avg_hit_rate": 61.9
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock picks statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/player/{player_name}")
async def get_picks_by_player(player_name: str, hours: int = Query(24, description="Hours of data to analyze")):
    """Get picks for a specific player"""
    try:
        # Return mock player picks data for now
        mock_player_picks = [
            {
                "id": 1,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": player_name,
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 6,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": player_name,
                "stat_type": "points",
                "line": 28.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.0,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 11,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": player_name,
                "stat_type": "three_pointers",
                "line": 4.5,
                "odds": -110,
                "model_probability": 0.5700,
                "implied_probability": 0.5238,
                "ev_percentage": 8.84,
                "confidence": 80.0,
                "hit_rate": 61.7,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            }
        ]
        
        return {
            "player_name": player_name,
            "picks": mock_player_picks,
            "total": len(mock_player_picks),
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock picks for {player_name}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_name": player_name,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/game/{game_id}")
async def get_picks_by_game(game_id: int):
    """Get picks for a specific game"""
    try:
        # Return mock game picks data for now
        mock_game_picks = [
            {
                "id": 1,
                "game_id": game_id,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 4,
                "game_id": game_id,
                "pick_type": "player_prop",
                "player_name": "LeBron James",
                "stat_type": "points",
                "line": 25.0,
                "odds": -108,
                "model_probability": 0.6100,
                "implied_probability": 0.5195,
                "ev_percentage": 17.40,
                "confidence": 89.0,
                "hit_rate": 64.1,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 6,
                "game_id": game_id,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 28.5,
                "odds": -115,
                "model_probability": 0.6200,
                "implied_probability": 0.5349,
                "ev_percentage": 15.92,
                "confidence": 88.0,
                "hit_rate": 64.0,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 7,
                "game_id": game_id,
                "pick_type": "player_prop",
                "player_name": "Kevin Durant",
                "stat_type": "points",
                "line": 26.5,
                "odds": -108,
                "model_probability": 0.5900,
                "implied_probability": 0.5195,
                "ev_percentage": 13.58,
                "confidence": 86.0,
                "hit_rate": 63.2,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            }
        ]
        
        return {
            "game_id": game_id,
            "picks": mock_game_picks,
            "total": len(mock_game_picks),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock picks for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/picks/search")
async def search_picks(query: str = Query(..., description="Search query"),
                      hours: int = Query(24, description="Hours of data to analyze"),
                      limit: int = Query(20, description="Number of results to return")):
    """Search picks by player name or stat type"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "game_id": 662,
                "pick_type": "player_prop",
                "player_name": "Stephen Curry",
                "stat_type": "points",
                "line": 29.0,
                "odds": -112,
                "model_probability": 0.6300,
                "implied_probability": 0.5283,
                "ev_percentage": 19.28,
                "confidence": 90.0,
                "hit_rate": 65.2,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 2,
                "game_id": 664,
                "pick_type": "player_prop",
                "player_name": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "line": 2.5,
                "odds": -108,
                "model_probability": 0.6300,
                "implied_probability": 0.5195,
                "ev_percentage": 21.28,
                "confidence": 91.0,
                "hit_rate": 66.8,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=15).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['player_name'].lower() or 
                   query_lower in r['stat_type'].lower() or
                   query_lower in r['pick_type'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
'''
    
    # Add the endpoints before the anomaly endpoints
    if "# Brain Anomaly Detection Endpoints" in content:
        content = content.replace("# Brain Anomaly Detection Endpoints", picks_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += picks_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Picks endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_picks_endpoints())
