#!/usr/bin/env python3
"""
ADD INJURY TRACKING ENDPOINTS - Add injury tracking endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_injury_endpoints():
    """Add injury tracking endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the injury tracking endpoints
    injury_code = '''

# Injury Tracking Endpoints
@router.get("/injuries")
async def get_injuries(sport_id: int = Query(None, description="Sport ID to filter"), 
                        status: str = Query(None, description="Injury status to filter"),
                        player_id: int = Query(None, description="Player ID to filter"),
                        limit: int = Query(50, description="Number of injuries to return")):
    """Get injuries with optional filters"""
    try:
        # Return mock injury data for now
        mock_injuries = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": 65,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 22,
                "sport_id": 30,
                "player_id": 66,
                "status": "DAY_TO_DAY",
                "status_detail": "Back",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 23,
                "sport_id": 30,
                "player_id": 67,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 24,
                "sport_id": 30,
                "player_id": 68,
                "status": "DAY_TO_DAY",
                "status_detail": "Hip",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 25,
                "sport_id": 30,
                "player_id": 69,
                "status": "OUT",
                "status_detail": "Toe",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 26,
                "sport_id": 30,
                "player_id": 70,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 27,
                "sport_id": 30,
                "player_id": 71,
                "status": "OUT",
                "status_detail": "Shoulder (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 28,
                "sport_id": 30,
                "player_id": 72,
                "status": "OUT",
                "status_detail": "Oblique",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 29,
                "sport_id": 30,
                "player_id": 27,
                "status": "OUT",
                "status_detail": "Foot/Toe",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 30,
                "sport_id": 30,
                "player_id": 30,
                "status": "OUT",
                "status_detail": "Calf",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 31,
                "sport_id": 32,
                "player_id": 101,
                "status": "QUESTIONABLE",
                "status_detail": "Concussion",
                "is_starter_flag": False,
                "probability": 0.3,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 32,
                "sport_id": 32,
                "player_id": 102,
                "status": "DOUBTFUL",
                "status_detail": "Ankle",
                "is_starter_flag": False,
                "probability": 0.4,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 33,
                "sport_id": 32,
                "player_id": 103,
                "status": "OUT",
                "status_detail": "ACL Tear (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 34,
                "sport_id": 32,
                "player_id": 104,
                "status": "DAY_TO_DAY",
                "status_detail": "Shoulder",
                "is_starter_flag": False,
                "probability": 0.6,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 35,
                "sport_id": 32,
                "player_id": 105,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 36,
                "sport_id": 32,
                'player_id': 106,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Knee',
                'is_starter_flag': False,
                'probability': 0.7,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_injuries = mock_injuries
        if sport_id:
            filtered_injuries = [i for i in filtered_injuries if i['sport_id'] == sport_id]
        if status:
            filtered_injuries = [i for i in filtered_injuries if i['status'] == status.upper()]
        if player_id:
            filtered_injuries = [i for i in filtered_injuries if i['player_id'] == player_id]
        
        return {
            "injuries": filtered_injuries[:limit],
            "total": len(filtered_injuries),
            "filters": {
                "sport_id": sport_id,
                "status": status,
                "player_id": player_id,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock injury data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "status": status,
            "player_id": player_id,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/active")
async def get_active_injuries(sport_id: int = Query(None, description="Sport ID to filter")):
    """Get currently active injuries"""
    try:
        # Return mock active injuries data for now
        mock_active = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": 65,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 22,
                "sport_id": 30,
                "player_id": 66,
                "status": "DAY_TO_DAY",
                "status_detail": "Back",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 24,
                "sport_id": 30,
                "player_id": 68,
                "status": "DAY_TO_DAY",
                "status_detail": "Hip",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 31,
                "sport_id": 32,
                "player_id": 101,
                "status": "QUESTIONABLE",
                "status_detail": "Concussion",
                "is_starter_flag": False,
                "probability": 0.3,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 32,
                "sport_id": 32,
                "player_id": 102,
                "status": "DOUBTFUL",
                "status_detail": "Ankle",
                "is_starter_flag": False,
                "probability": 0.4,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 36,
                "sport_id": 32,
                'player_id': 106,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Knee',
                'is_starter_flag': False,
                'probability': 0.7,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 403,
                "sport_id": 32,
                'player_id': 403,
                'status': 'QUESTIONABLE',
                'status_detail': 'Concussion Protocol',
                'is_starter_flag': False,
                'probability': 0.25,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=3, hours=10)).isoformat()
            },
            {
                "id": 404,
                "sport_id': 32,
                'player_id': 404,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Back Strain',
                'is_starter_flag': False,
                'probability': 0.4,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=3, hours=10)).isoformat()
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_active = [i for i in mock_active if i['sport_id'] == sport_id]
        
        return {
            "active_injuries": mock_active,
            "total": len(mock_active),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock active injuries data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/out")
async def get_out_injuries(sport_id: int = Query(None, description="Sport ID to filter")):
    """Get players who are out"""
    try:
        # Return mock out injuries data for now
        mock_out = [
            {
                "id": 23,
                "sport_id": 30,
                "player_id": 67,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 25,
                "sport_id": 30,
                "player_id": 69,
                "status": "OUT",
                "status_detail": "Toe",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 26,
                "sport_id": 30,
                "player_id": 70,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 27,
                "sport_id": 30,
                "player_id": 71,
                "status": "OUT",
                "status_detail": "Shoulder (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 28,
                "sport_id": 30,
                "player_id": 72,
                "status": "OUT",
                "status_detail": "Oblique",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 29,
                "sport_id": 30,
                "player_id": 27,
                "status": "OUT",
                "status_detail": "Foot/Toe",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 30,
                "sport_id": 30,
                "player_id": 30,
                "status": "OUT",
                "status_detail": "Calf",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 33,
                "sport_id": 32,
                "player_id": 103,
                "status": "OUT",
                "status_detail": "ACL Tear (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 35,
                "sport_id": 32,
                "player_id": 105,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_out = [i for i in mock_out if i['sport_id'] == sport_id]
        
        return {
            "out_injuries": mock_out,
            "total": len(mock_out),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock out injuries data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/statistics")
async def get_injury_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get injury statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_injuries": 21,
            "unique_sports": 4,
            "unique_players": 16,
            "out_injuries": 10,
            "day_to_day_injuries": 7,
            "questionable_injuries": 2,
            "doubtful_injuries": 1,
            "starter_injuries": 2,
            "avg_probability": 0.31,
            "official_injuries": 21,
            "by_sport": [
                {
                    "sport_id": 30,
                    "total_injuries": 10,
                    "out_injuries": 5,
                    "day_to_day_injuries": 5,
                    "questionable_injuries": 2,
                    "doubtful_injuries": 1,
                    "starter_injuries": 2,
                    "avg_probability": 0.40,
                    "unique_players": 10
                },
                {
                    "sport_id": 32,
                    "total_injuries": 7,
                    "out_injuries": 3,
                    "day_to_day_injuries": 2,
                    "questionable_injuries": 1,
                    "doubtful_injuries": 1,
                    "starter_injuries": 0,
                    "avg_probability": 0.33,
                    "unique_players": 7
                },
                {
                    "sport_id": 29,
                    "total_injuries": 4,
                    "out_injuries": 2,
                    "day_to_day_injuries": 2,
                    "questionable_injuries": 0,
                    "doubtful_injuries": 0,
                    "starter_injuries": 0,
                    "avg_probability": 0.20,
                    "unique_players": 4
                },
                {
                    "sport_id": 53,
                    "total_injuries": 4,
                    "out_injuries": 2,
                    "day_to_day_injuries": 2,
                    "questionable_injuries": 1,
                    "doubtful_injuries": 0,
                    "starter_injuries": 0,
                    "avg_probability": 0.25,
                    "unique_players": 4
                }
            ],
            "by_status": [
                {
                    "status": "OUT",
                    "total_injuries": 10,
                    "avg_probability": 0.0,
                    "starter_injuries": 2,
                    "unique_players": 10
                },
                {
                    "status": "DAY_TO_DAY",
                    "total_injuries": 7,
                    "avg_probability": 0.47,
                    "starter_injuries": 2,
                    "unique_players": 7
                },
                {
                    "status": "QUESTIONABLE",
                    "total_injuries": 3,
                    "avg_probability": 0.28,
                    "starter_injuries": 0,
                    "unique_players": 3
                },
                {
                    "status": "DOUBTFUL",
                    "total_injuries": 2,
                    "avg_probability": 0.35,
                    "starter_injuries": 0,
                    "unique_players": 2
                }
            ],
            "by_source": [
                {
                    "source": "official",
                    "total_injuries": 21,
                    "avg_probability": 0.31,
                    "unique_players": 16
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock injury statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/player/{player_id}")
async def get_player_injuries(player_id: int, sport_id: int = Query(None, description="Sport ID to filter")):
    """Get injuries for a specific player"""
    try:
        # Return mock player injury data for now
        mock_player_injuries = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": player_id,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 22,
                "sport_id": 30,
                "player_id": player_id,
                "status": "DAY_TO_DAY",
                "status_detail": "Back",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 23,
                "sport_id": 30,
                "player_id": player_id,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_player_injuries = [i for i in mock_player_injuries if i['sport_id'] == sport_id]
        
        return {
            "player_id": player_id,
            "injuries": mock_player_injuries,
            "total": len(mock_player_injuries),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock injury data for player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_id": player_id,
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/impact-analysis/{sport_id}")
async def get_injury_impact_analysis(sport_id: int, days: int = Query(30, description="Days of data to analyze")):
    """Analyze injury impact on team performance"""
    try:
        # Return mock impact analysis data for now
        mock_impact = {
            "sport_id": sport_id,
            "period_days": days,
            "total_injuries": 10,
            "active_injuries": 5,
            "out_injuries": 3,
            "starter_injuries": 0,
            "starter_impact_score": 0.0,
            "active_impact_score": 50.0,
            "out_impact_score": 30.0,
            "weighted_impact": 0.3,
            "concerning_injuries": [
                {
                    "player_id": 103,
                    "status": "OUT",
                    "status_detail": "ACL Tear (Season-ending)",
                    "is_starter": False,
                    "probability": 0.0
                },
                {
                    "player_id": 101,
                    "status": "QUESTIONABLE",
                    "status_detail": "Concussion",
                    "is_starter": False,
                    "probability": 0.3
                }
            ],
            "impact_analysis": "Moderate impact - some active injuries",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock impact analysis for sport {sport_id}"
        }
        
        return mock_impact
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/trends/{sport_id}")
async def get_injury_trends(sport_id: int, days: int = Query(30, description="Days of data to analyze")):
    """Analyze injury trends over time"""
    try:
        # Return mock trend analysis data for now
        mock_trends = {
            "sport_id": sport_id,
            "period_days": days,
            "daily_trends": [
                {
                    "date": "2026-02-01",
                    "total_injuries": 5,
                    "out_injuries": 2,
                    "day_to_day_injuries": 3,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-02",
                    "total_injuries": 3,
                    "out_injuries": 1,
                    "day_to_day_injuries": 2,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-03",
                    "total_injuries": 2,
                    "out_injuries": 0,
                    "day_to_day_injuries": 2,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-04",
                    "total_injuries": 1,
                    "out_injuries": 0,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-05",
                    "total_injuries": 2,
                    "out_injuries": 1,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-06",
                    "total_injuries": 1,
                    "out_injuries": 0,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-07",
                    "total_injuries": 1,
                    "out_injuries": 0,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                }
            ],
            "trend_analysis": "Decreasing injuries - positive trend",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock injury trends for sport {sport_id}"
        }
        
        return mock_trends
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/search")
async def search_injuries(query: str = Query(..., description="Search query"), 
                             sport_id: int = Query(None, description="Sport ID to filter"),
                             limit: int = Query(20, description="Number of results to return")):
    """Search injuries by player ID or status detail"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": 65,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 23,
                "sport_id": 30,
                "player_id": 67,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 33,
                "sport_id": 32,
                "player_id": 103,
                "status": "OUT",
                "status_detail": "ACL Tear (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            }
        ]
        
        # Apply filters
        if sport_id:
            mock_results = [r for r in mock_results if r['sport_id'] == sport_id]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in str(r['player_id']) or 
                   query_lower in r['status_detail'].lower()
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
            "sport_id": sport_id,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
'''
    
    # Add the endpoints before the anomaly endpoints
    if "# Brain Anomaly Detection Endpoints" in content:
        content = content.replace("# Brain Anomaly Detection Endpoints", injury_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += injury_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Injury tracking endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_injury_endpoints())
