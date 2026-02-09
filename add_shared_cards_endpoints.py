#!/usr/bin/env python3
"""
ADD SHARED CARDS ENDPOINTS - Add shared betting cards tracking endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_shared_cards_endpoints():
    """Add shared betting cards tracking endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the shared cards endpoints
    shared_cards_code = '''

# Shared Betting Cards Tracking Endpoints
@router.get("/shared-cards")
async def get_shared_cards(platform: str = Query(None, description="Platform to filter"),
                            sport: str = Query(None, description="Sport to filter"),
                            grade: str = Query(None, description="Grade to filter"),
                            trending: bool = Query(False, description="Get trending cards"),
                            performing: bool = Query(False, description="Get top performing cards"),
                            limit: int = Query(50, description="Number of cards to return")):
    """Get shared betting cards with optional filters"""
    try:
        # Return mock shared cards data for now
        mock_cards = [
            {
                "id": 1,
                "platform": "twitter",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "LeBron James", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Stephen Curry", "market": "points", "line": 28.5, "odds": -110},
                    {"player": "Kevin Durant", "market": "points", "line": 26.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0286,
                "overall_grade": "A",
                "label": "NBA Stars Points Parlay - All Over",
                "kelly_suggested_units": 2.5,
                "kelly_risk_level": "Medium",
                "view_count": 1250,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "platform": "discord",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "LeBron James", "market": "rebounds", "line": 7.5, "odds": -110},
                    {"player": "Anthony Davis", "market": "rebounds", "line": 10.5, "odds": -110},
                    {"player": "Nikola Jokic", "market": "rebounds", "line": 11.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0143,
                "overall_grade": "B+",
                "label": "NBA Rebounds Master Parlay",
                "kelly_suggested_units": 1.8,
                "kelly_risk_level": "Medium",
                "view_count": 890,
                "settled": True,
                "won": False,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            },
            {
                "id": 3,
                "platform": "twitter",
                "sport_id": 1,
                "sport": "NFL",
                "legs": [
                    {"player": "Patrick Mahomes", "market": "passing_yards", "line": 285.5, "odds": -110},
                    {"player": "Josh Allen", "market": "passing_yards", "line": 265.5, "odds": -110},
                    {"player": "Justin Herbert", "market": "passing_yards", "line": 275.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0357,
                "overall_grade": "A-",
                "label": "NFL QB Passing Yards Parlay",
                "kelly_suggested_units": 3.2,
                "kelly_risk_level": "High",
                "view_count": 2100,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            },
            {
                "id": 4,
                "platform": "reddit",
                "sport_id": 1,
                "sport": "NFL",
                "legs": [
                    {"player": "Christian McCaffrey", "market": "rushing_yards", "line": 85.5, "odds": -110},
                    {"player": "Derrick Henry", "market": "rushing_yards", "line": 95.5, "odds": -110},
                    {"player": "Jonathan Taylor", "market": "rushing_yards", "line": 90.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0214,
                "overall_grade": "B",
                "label": "NFL RB Rushing Yards Parlay",
                "kelly_suggested_units": 2.1,
                "kelly_risk_level": "Medium",
                "view_count": 1560,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
            },
            {
                "id": 5,
                "platform": "twitter",
                "sport_id": 2,
                "sport": "MLB",
                "legs": [
                    {"player": "Aaron Judge", "market": "home_runs", "line": 1.5, "odds": -110},
                    {"player": "Mike Trout", "market": "hits", "line": 1.5, "odds": -110},
                    {"player": "Shohei Ohtani", "market": "strikeouts", "line": 7.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0429,
                "overall_grade": "A",
                "label": "MLB Stars Multi-Stat Parlay",
                "kelly_suggested_units": 3.8,
                "kelly_risk_level": "High",
                "view_count": 1890,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
            },
            {
                "id": 6,
                "platform": "discord",
                "sport_id": 32,
                "sport": "NCAA Basketball",
                "legs": [
                    {"player": "Zion Williamson", "market": "points", "line": 22.5, "odds": -110},
                    {"player": "Paolo Banchero", "market": "points", "line": 20.5, "odds": -110},
                    {"player": "Chet Holmgren", "market": "rebounds", "line": 8.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0214,
                "overall_grade": "B+",
                "label": "NCAA Basketball Stars Parlay",
                "kelly_suggested_units": 2.4,
                "kelly_risk_level": "Medium",
                "view_count": 1450,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=9)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
            },
            {
                "id": 7,
                "platform": "twitter",
                "sport_id": 99,
                "sport": "Multi-Sport",
                "legs": [
                    {"player": "LeBron James", "sport": "NBA", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Patrick Mahomes", "sport": "NFL", "market": "passing_yards", "line": 285.5, "odds": -110},
                    {"player": "Aaron Judge", "sport": "MLB", "market": "home_runs", "line": 1.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0250,
                "overall_grade": "A-",
                "label": "Multi-Sport Superstars Parlay",
                "kelly_suggested_units": 2.8,
                "kelly_risk_level": "High",
                "view_count": 2340,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=11)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
            },
            {
                "id": 8,
                "platform": "twitter",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "Stephen Curry", "market": "three_pointers", "line": 4.5, "odds": -110},
                    {"player": "Klay Thompson", "market": "three_pointers", "line": 3.5, "odds": -110},
                    {"player": "Damian Lillard", "market": "three_pointers", "line": 3.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0321,
                "overall_grade": "A",
                "label": "NBA Three-Point Specialists Parlay",
                "kelly_suggested_units": 3.0,
                "kelly_risk_level": "High",
                "view_count": 890,
                "settled": False,
                "won": None,
                "settled_at": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_cards = mock_cards
        if platform:
            filtered_cards = [c for c in filtered_cards if c['platform'].lower() == platform.lower()]
        if sport:
            filtered_cards = [c for c in filtered_cards if c['sport'].lower() == sport.lower()]
        if grade:
            filtered_cards = [c for c in filtered_cards if c['overall_grade'].lower() == grade.lower()]
        
        # Apply sorting
        if trending:
            filtered_cards = sorted(filtered_cards, key=lambda x: x['view_count'], reverse=True)
        elif performing:
            filtered_cards = sorted(filtered_cards, key=lambda x: x['parlay_ev'], reverse=True)
        
        return {
            "cards": filtered_cards[:limit],
            "total": len(filtered_cards),
            "filters": {
                "platform": platform,
                "sport": sport,
                "grade": grade,
                "trending": trending,
                "performing": performing,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock shared cards data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/statistics")
async def get_shared_cards_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get shared cards statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_cards": 12,
            "unique_platforms": 4,
            "unique_sports": 6,
            "avg_total_odds": 6.00,
            "avg_decimal_odds": 7.00,
            "avg_parlay_probability": 0.1429,
            "avg_parlay_ev": 0.0250,
            "grade_a_cards": 4,
            "settled_cards": 10,
            "won_cards": 7,
            "lost_cards": 3,
            "total_views": 15460,
            "avg_views_per_card": 1288.3,
            "platform_performance": [
                {
                    "platform": "twitter",
                    "total_cards": 6,
                    "settled_cards": 5,
                    "won_cards": 4,
                    "win_rate_percentage": 80.0,
                    "avg_parlay_ev": 0.0300,
                    "total_views": 9360,
                    "avg_views_per_card": 1560.0
                },
                {
                    "platform": "discord",
                    "total_cards": 3,
                    "settled_cards": 2,
                    "won_cards": 1,
                    "win_rate_percentage": 50.0,
                    "avg_parlay_ev": 0.0180,
                    "total_views": 4230,
                    "avg_views_per_card": 1410.0
                },
                {
                    "platform": "reddit",
                    "total_cards": 2,
                    "settled_cards": 2,
                    "won_cards": 1,
                    "win_rate_percentage": 50.0,
                    "avg_parlay_ev": 0.0210,
                    "total_views": 3010,
                    "avg_views_per_card": 1505.0
                },
                {
                    "platform": "telegram",
                    "total_cards": 1,
                    "settled_cards": 1,
                    "won_cards": 1,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0250,
                    "total_views": 860,
                    "avg_views_per_card": 860.0
                }
            ],
            "sport_performance": [
                {
                    "sport_id": 30,
                    "total_cards": 4,
                    "settled_cards": 3,
                    "won_cards": 2,
                    "win_rate_percentage": 66.7,
                    "avg_parlay_ev": 0.0250,
                    "total_views": 6480,
                    "avg_views_per_card": 1620.0
                },
                {
                    "sport_id": 1,
                    "total_cards": 2,
                    "settled_cards": 2,
                    "won_cards": 2,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0285,
                    "total_views": 3660,
                    "avg_views_per_card": 1830.0
                },
                {
                    "sport_id": 2,
                    "total_cards": 1,
                    "settled_cards": 1,
                    "won_cards": 1,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0429,
                    "total_views": 1890,
                    "avg_views_per_card": 1890.0
                },
                {
                    "sport_id": 32,
                    "total_cards": 1,
                    "settled_cards": 1,
                    "won_cards": 1,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0214,
                    "total_views": 1450,
                    "avg_views_per_card": 1450.0
                },
                {
                    "sport_id": 99,
                    "total_cards": 1,
                    "settled_cards": 1,
                    "won_cards": 1,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0250,
                    "total_views": 2340,
                    "avg_views_per_card": 2340.0
                }
            ],
            "grade_performance": [
                {
                    "overall_grade": "A",
                    "total_cards": 4,
                    "settled_cards": 3,
                    "won_cards": 3,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0340,
                    "avg_kelly_units": 3.1,
                    "total_views": 6920,
                    "avg_views_per_card": 1730.0
                },
                {
                    "overall_grade": "A-",
                    "total_cards": 2,
                    "settled_cards": 2,
                    "won_cards": 2,
                    "win_rate_percentage": 100.0,
                    "avg_parlay_ev": 0.0300,
                    "avg_kelly_units": 3.0,
                    "total_views": 4440,
                    "avg_views_per_card": 2220.0
                },
                {
                    "overall_grade": "B+",
                    "total_cards": 3,
                    "settled_cards": 2,
                    "won_cards": 1,
                    "win_rate_percentage": 50.0,
                    "avg_parlay_ev": 0.0180,
                    "avg_kelly_units": 2.1,
                    "total_views": 3930,
                    "avg_views_per_card": 1310.0
                },
                {
                    "overall_grade": "B",
                    "total_cards": 1,
                    "settled_cards": 1,
                    "won_cards": 0,
                    "win_rate_percentage": 0.0,
                    "avg_parlay_ev": 0.0214,
                    "avg_kelly_units": 2.1,
                    "total_views": 1560,
                    "avg_views_per_card": 1560.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock shared cards statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/platform/{platform}")
async def get_shared_cards_by_platform(platform: str, limit: int = Query(50, description="Number of cards to return")):
    """Get shared cards for a specific platform"""
    try:
        # Return mock platform-specific cards data for now
        mock_platform_cards = [
            {
                "id": 1,
                "platform": platform,
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "LeBron James", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Stephen Curry", "market": "points", "line": 28.5, "odds": -110},
                    {"player": "Kevin Durant", "market": "points", "line": 26.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0286,
                "overall_grade": "A",
                "label": "NBA Stars Points Parlay - All Over",
                "kelly_suggested_units": 2.5,
                "kelly_risk_level": "Medium",
                "view_count": 1250,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 3,
                "platform": platform,
                "sport_id": 1,
                "sport": "NFL",
                "legs": [
                    {"player": "Patrick Mahomes", "market": "passing_yards", "line": 285.5, "odds": -110},
                    {"player": "Josh Allen", "market": "passing_yards", "line": 265.5, "odds": -110},
                    {"player": "Justin Herbert", "market": "passing_yards", "line": 275.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0357,
                "overall_grade": "A-",
                "label": "NFL QB Passing Yards Parlay",
                "kelly_suggested_units": 3.2,
                "kelly_risk_level": "High",
                "view_count": 2100,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
            }
        ]
        
        return {
            "platform": platform,
            "cards": mock_platform_cards[:limit],
            "total": len(mock_platform_cards),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock shared cards for {platform}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "platform": platform,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/sport/{sport}")
async def get_shared_cards_by_sport(sport: str, limit: int = Query(50, description="Number of cards to return")):
    """Get shared cards for a specific sport"""
    try:
        # Return mock sport-specific cards data for now
        mock_sport_cards = [
            {
                "id": 1,
                "platform": "twitter",
                "sport_id": 30,
                "sport": sport,
                "legs": [
                    {"player": "LeBron James", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Stephen Curry", "market": "points", "line": 28.5, "odds": -110},
                    {"player": "Kevin Durant", "market": "points", "line": 26.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0286,
                "overall_grade": "A",
                "label": "NBA Stars Points Parlay - All Over",
                "kelly_suggested_units": 2.5,
                "kelly_risk_level": "Medium",
                "view_count": 1250,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 2,
                "platform": "discord",
                "sport_id": 30,
                "sport": sport,
                "legs": [
                    {"player": "LeBron James", "market": "rebounds", "line": 7.5, "odds": -110},
                    {"player": "Anthony Davis", "market": "rebounds", "line": 10.5, "odds": -110},
                    {"player": "Nikola Jokic", "market": "rebounds", "line": 11.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0143,
                "overall_grade": "B+",
                "label": "NBA Rebounds Master Parlay",
                "kelly_suggested_units": 1.8,
                "kelly_risk_level": "Medium",
                "view_count": 890,
                "settled": True,
                "won": False,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            }
        ]
        
        return {
            "sport": sport,
            "cards": mock_sport_cards[:limit],
            "total": len(mock_sport_cards),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock shared cards for {sport}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport": sport,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/grade/{grade}")
async def get_shared_cards_by_grade(grade: str, limit: int = Query(50, description="Number of cards to return")):
    """Get shared cards by grade"""
    try:
        # Return mock grade-specific cards data for now
        mock_grade_cards = [
            {
                "id": 1,
                "platform": "twitter",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "LeBron James", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Stephen Curry", "market": "points", "line": 28.5, "odds": -110},
                    {"player": "Kevin Durant", "market": "points", "line": 26.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0286,
                "overall_grade": grade,
                "label": "NBA Stars Points Parlay - All Over",
                "kelly_suggested_units": 2.5,
                "kelly_risk_level": "Medium",
                "view_count": 1250,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 5,
                "platform": "twitter",
                "sport_id": 2,
                "sport": "MLB",
                "legs": [
                    {"player": "Aaron Judge", "market": "home_runs", "line": 1.5, "odds": -110},
                    {"player": "Mike Trout", "market": "hits", "line": 1.5, "odds": -110},
                    {"player": "Shohei Ohtani", "market": "strikeouts", "line": 7.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0429,
                "overall_grade": grade,
                "label": "MLB Stars Multi-Stat Parlay",
                "kelly_suggested_units": 3.8,
                "kelly_risk_level": "High",
                "view_count": 1890,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
            }
        ]
        
        return {
            "grade": grade,
            "cards": mock_grade_cards[:limit],
            "total": len(mock_grade_cards),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock shared cards for grade {grade}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "grade": grade,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/search")
async def search_shared_cards(query: str = Query(..., description="Search query"),
                              limit: int = Query(20, description="Number of results to return")):
    """Search shared cards by label or legs"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "platform": "twitter",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "LeBron James", "market": "points", "line": 24.5, "odds": -110},
                    {"player": "Stephen Curry", "market": "points", "line": 28.5, "odds": -110},
                    {"player": "Kevin Durant", "market": "points", "line": 26.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0286,
                "overall_grade": "A",
                "label": "NBA Stars Points Parlay - All Over",
                "kelly_suggested_units": 2.5,
                "kelly_risk_level": "Medium",
                "view_count": 1250,
                "settled": True,
                "won": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            },
            {
                "id": 8,
                "platform": "twitter",
                "sport_id": 30,
                "sport": "NBA",
                "legs": [
                    {"player": "Stephen Curry", "market": "three_pointers", "line": 4.5, "odds": -110},
                    {"player": "Klay Thompson", "market": "three_pointers", "line": 3.5, "odds": -110},
                    {"player": "Damian Lillard", "market": "three_pointers", "line": 3.5, "odds": -110}
                ],
                "leg_count": 3,
                "total_odds": 6.00,
                "decimal_odds": 7.00,
                "parlay_probability": 0.1429,
                "parlay_ev": 0.0321,
                "overall_grade": "A",
                "label": "NBA Three-Point Specialists Parlay",
                "kelly_suggested_units": 3.0,
                "kelly_risk_level": "High",
                "view_count": 890,
                "settled": False,
                "won": None,
                "settled_at": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['label'].lower() or 
                   any(query_lower in leg['player'].lower() or 
                       query_lower in leg['market'].lower() 
                       for leg in r['legs'])
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
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
'''
    
    # Add the endpoints before the anomaly endpoints
    if "# Brain Anomaly Detection Endpoints" in content:
        content = content.replace("# Brain Anomaly Detection Endpoints", shared_cards_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += shared_cards_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Shared cards endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_shared_cards_endpoints())
