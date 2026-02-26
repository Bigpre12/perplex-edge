#!/usr/bin/env python3
"""
ADD LIVE ODDS NFL ENDPOINTS - Add live odds NFL endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_live_odds_nfl_endpoints():
    """Add live odds NFL endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the live odds NFL endpoints
    live_odds_nfl_code = '''

# Live Odds NFL Endpoints
@router.get("/live-odds-nfl")
async def get_live_odds_nfl(game_id: int = Query(None, description="Game ID to filter"), 
                          team: str = Query(None, description="Team name to filter"),
                          bookmaker: str = Query(None, description="Sportsbook to filter"),
                          week: int = Query(None, description="Week to filter"),
                          limit: int = Query(50, description="Number of odds to return")):
    """Get live NFL odds with optional filters"""
    try:
        # Return mock live NFL odds data for now
        mock_odds = [
            {
                "id": 1,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -165,
                "away_odds": 145,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 2,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 3,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -170,
                "away_odds": 150,
                "draw_odds": None,
                "bookmaker": "BetMGM",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 4,
                "sport": 1,
                "game_id": 2002,
                "home_team": "San Francisco 49ers",
                "away_team": "Philadelphia Eagles",
                "home_odds": -125,
                "away_odds": 105,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat()
            },
            {
                "id": 5,
                "sport": 1,
                "game_id": 2002,
                "home_team": "San Francisco 49ers",
                "away_team": "Philadelphia Eagles",
                "home_odds": -130,
                "away_odds": 110,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=25)).isoformat()
            },
            {
                "id": 6,
                "sport": 1,
                "game_id": 2003,
                "home_team": "Dallas Cowboys",
                "away_team": "New York Giants",
                "home_odds": -280,
                "away_odds": 230,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
            },
            {
                "id": 7,
                "sport": 1,
                "game_id": 2004,
                "home_team": "Green Bay Packers",
                "away_team": "Chicago Bears",
                "home_odds": -190,
                "away_odds": 160,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
            },
            {
                "id": 8,
                "sport": 1,
                "game_id": 2005,
                "home_team": "New England Patriots",
                "away_team": "New York Jets",
                "home_odds": -140,
                "away_odds": 120,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
            },
            {
                "id": 9,
                "sport": 1,
                "game_id": 2006,
                "home_team": "Baltimore Ravens",
                "away_team": "Pittsburgh Steelers",
                "home_odds": -155,
                "away_odds": 135,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
            },
            {
                "id": 10,
                "sport": 1,
                "game_id": 2007,
                "home_team": "Cincinnati Bengals",
                "away_team": "Cleveland Browns",
                "home_odds": -110,
                "away_odds": -110,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_odds = mock_odds
        if game_id:
            filtered_odds = [o for o in filtered_odds if o['game_id'] == game_id]
        if team:
            filtered_odds = [o for o in filtered_odds if team.lower() in o['home_team'].lower() or team.lower() in o['away_team'].lower()]
        if bookmaker:
            filtered_odds = [o for o in filtered_odds if o['bookmaker'].lower() == bookmaker.lower()]
        if week:
            filtered_odds = [o for o in filtered_odds if o['week'] == week]
        
        return {
            "odds": filtered_odds[:limit],
            "total": len(filtered_odds),
            "filters": {
                "game_id": game_id,
                "team": team,
                "bookmaker": bookmaker,
                "week": week,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock live NFL odds data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/current")
async def get_current_live_odds_nfl(game_id: int = Query(None, description="Game ID to filter"), 
                                   bookmaker: str = Query(None, description="Sportsbook to filter")):
    """Get current live NFL odds"""
    try:
        # Return mock current live NFL odds data for now
        mock_current = [
            {
                "id": 11,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -165,
                "away_odds": 145,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 12,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "bookmaker": "FanDuel",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 13,
                "sport": 1,
                "game_id": 2002,
                "home_team": "San Francisco 49ers",
                "away_team": "Philadelphia Eagles",
                "home_odds": -125,
                "away_odds": 105,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 14,
                "sport": 1,
                "game_id": 2003,
                "home_team": "Dallas Cowboys",
                "away_team": "New York Giants",
                "home_odds": -280,
                "away_odds": 230,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 15,
                "sport": 1,
                "game_id": 2004,
                "home_team": "Green Bay Packers",
                "away_team": "Chicago Bears",
                "home_odds": -190,
                "away_odds": 160,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Apply filters
        if game_id:
            mock_current = [o for o in mock_current if o['game_id'] == game_id]
        if bookmaker:
            mock_current = [o for o in mock_current if o['bookmaker'].lower() == bookmaker.lower()]
        
        return {
            "current_odds": mock_current,
            "total": len(mock_current),
            "game_id": game_id,
            "bookmaker": bookmaker,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock current live NFL odds data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "bookmaker": bookmaker,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/movements/{game_id}")
async def get_live_odds_nfl_movements(game_id: int, minutes: int = Query(30, description="Minutes of data to analyze")):
    """Get live NFL odds movements for a specific game"""
    try:
        # Return mock movements data for now
        mock_movements = [
            {
                "sportsbook": "DraftKings",
                "home_odds": -162,
                "away_odds": 142,
                "draw_odds": None,
                "timestamp": (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat(),
                "home_movement": 3,
                "away_movement": -3,
                "prev_home_odds": -165,
                "prev_away_odds": 145,
                "prev_draw_odds": None
            },
            {
                "sportsbook": "DraftKings",
                "home_odds": -168,
                "away_odds": 148,
                "draw_odds": None,
                "timestamp": (datetime.now(timezone.utc) - timedelta(seconds=15)).isoformat(),
                "home_movement": -6,
                "away_movement": 6,
                "prev_home_odds": -162,
                "prev_away_odds": 142,
                "prev_draw_odds": None
            },
            {
                "sportsbook": "DraftKings",
                "home_odds": -165,
                "away_odds": 145,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "home_movement": 3,
                "away_movement": -3,
                "prev_home_odds": -168,
                "prev_away_odds": 148,
                "prev_draw_odds": None
            },
            {
                "sportsbook": "FanDuel",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "home_movement": 0,
                "away_movement": 0,
                "prev_home_odds": None,
                "prev_away_odds": None,
                "prev_draw_odds": None
            },
            {
                "sportsbook": "BetMGM",
                "home_odds": -170,
                "away_odds": 150,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "home_movement": 0,
                "away_movement": 0,
                "prev_home_odds": None,
                "prev_away_odds": None,
                "prev_draw_odds": None
            }
        ]
        
        return {
            "game_id": game_id,
            "movements": mock_movements,
            "total_movements": len(mock_movements),
            "minutes": minutes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock live NFL odds movements for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "minutes": minutes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/comparison/{game_id}")
async def get_live_odds_nfl_comparison(game_id: int, minutes: int = Query(30, description="Minutes of data to analyze")):
    """Compare live NFL odds across sportsbooks for a specific game"""
    try:
        # Return mock comparison data for now
        mock_comparison = [
            {
                "sportsbook": "DraftKings",
                "home_odds": -165,
                "away_odds": 145,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "sportsbook": "FanDuel",
                "home_odds": -160,
                "away_odds": 140,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "sportsbook": "BetMGM",
                "home_odds": -170,
                "away_odds": 150,
                "draw_odds": None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Calculate best odds
        best_home_odds = max(mock_comparison, key=lambda x: x['home_odds'] if x['home_odds'] < 0 else float('inf'))
        best_away_odds = max(mock_comparison, key=lambda x: x['away_odds'] if x['away_odds'] < 0 else float('inf'))
        
        return {
            "game_id": game_id,
            "comparison": mock_comparison,
            "best_home_odds": {
                "sportsbook": best_home_odds['sportsbook'],
                "line_value": best_home_odds['home_odds'],
                "odds": best_home_odds['odds']
            },
            "best_away_odds": {
                "best_away_odds": best_away_odds['sportsbook'],
                "line_value": best_away_odds['away_odds'],
                "odds": best_away_odds['odds']
            },
            "total_sportsbooks": len(mock_comparison),
            "minutes": minutes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock sportsbook comparison for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "minutes": minutes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/statistics")
async def get_live_odds_nfl_statistics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get live NFL odds statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_hours": hours,
            "total_odds": 24,
            "unique_games": 8,
            "unique_teams": 16,
            "unique_opponents": 16,
            "unique_bookmakers": 3,
            "unique_weeks": 4,
            "avg_home_odds": -140.5,
            "avg_away_odds": 120.5,
            "home_favorites": 18,
            "away_favorites": 6,
            "draw_markets": 0,
            "by_sportsbook": [
                {
                    "bookmaker": "DraftKings",
                    "total_odds": 10,
                    "unique_games": 8,
                    "unique_weeks": 4,
                    "avg_home_odds": -145.0,
                    "avg_away_odds": 125.0,
                    "home_favorites": 8,
                    "away_favorites": 2,
                    "unique_teams": 16,
                    "unique_opponents": 16
                },
                {
                    "bookmaker": "FanDuel",
                    "total_odds": 8,
                    "unique_games": 6,
                    "unique_weeks": 3,
                    "avg_home_odds": -135.0,
                    "avg_away_odds": 115.0,
                    "home_favorites": 6,
                    "away_favorites": 2,
                    "unique_teams": 12,
                    "unique_opponents": 12
                },
                {
                    "bookmaker": "BetMGM",
                    "total_odds": 6,
                    "unique_games": 4,
                    "unique_weeks": 2,
                    "avg_home_odds": -150.0,
                    "avg_away_odds": 130.0,
                    "home_favorites": 4,
                    "away_favorites": 2,
                    "unique_teams": 8,
                    "unique_opponents": 8
                }
            ],
            "by_week": [
                {
                    "week": 20,
                    "season": 2026,
                    "total_odds": 6,
                    "unique_games": 2,
                    "avg_home_odds": -147.5,
                    "avg_away_odds": 127.5,
                    "home_favorites": 4,
                    "away_favorites": 2
                },
                {
                    "week": 18,
                    "season": 2026,
                    "total_odds": 12,
                    "unique_games": 4,
                    "avg_home_odds": -138.3,
                    "avg_away_odds": 118.3,
                    "home_favorites": 10,
                    "away_favorites": 2
                }
            ],
            "by_team": [
                {
                    "team": "Kansas City Chiefs",
                    "total_games": 3,
                    "home_wins": 3,
                    "away_wins": 0,
                    "avg_home_odds": -165.0,
                    "avg_away_odds": 145.0,
                    "unique_games": 1,
                    "unique_weeks": 1
                },
                {
                    "team": "Dallas Cowboys",
                    "total_games": 3,
                    "home_wins": 3,
                    "away_wins": 0,
                    "avg_home_odds": -280.0,
                    "avg_away_odds": 230.0,
                    "unique_games": 1,
                    "unique_weeks": 1
                }
            ],
            "by_odds_range": [
                {
                    "odds_range": "Heavy Favorite",
                    "total_odds": 3,
                    "avg_odds": -280.0,
                    "avg_away_odds": 230.0
                },
                {
                    "odds_range": "Strong Favorite",
                    "total_odds": 5,
                    "avg_odds": -190.0,
                    "avg_away_odds": 160.0
                },
                {
                    "odds_range": "Moderate Favorite",
                    "total_odds": 8,
                    "avg_odds": -140.0,
                    "avg_away_odds": 120.0
                },
                {
                    "odds_range": "Light Favorite",
                    "total_odds": 6,
                    "avg_odds": -110.0,
                    "avg_away_odds": -110.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock live NFL odds statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/efficiency")
async def get_live_odds_nfl_efficiency(hours: int = Query(24, description="Hours of data to analyze")):
    """Analyze live NFL odds market efficiency and arbitrage opportunities"""
    try:
        # Return mock efficiency analysis data for now
        mock_efficiency = {
            "period_hours": hours,
            "total_arbitrage_opportunities": 8,
            "avg_home_range": 10.0,
            "avg_away_range": 10.0,
            "arbitrage_opportunities": [
                {
                    "game_id": 2001,
                    "home_team": "Kansas City Chiefs",
                    "away_team": "Buffalo Bills",
                    "week": 20,
                    "season": 2026,
                    "sportsbooks_count": 3,
                    "best_home_odds": -160,
                    "worst_home_odds": -170,
                    "best_away_odds": 140,
                    "worst_away_odds": 150,
                    "home_odds_range": 10,
                    "away_odds_range": 10,
                    "avg_home_odds": -165.0,
                    "avg_away_odds": 145.0
                },
                {
                    "game_id": 2002,
                    "home_team": "San Francisco 49ers",
                    "away_team": "Philadelphia Eagles",
                    "week": 20,
                    "season": 2026,
                    "sportsbooks_count": 2,
                    "best_home_odds": -125,
                    "worst_home_odds": -130,
                    "best_away_odds": 105,
                    "worst_away_odds": 110,
                    "home_odds_range": 5,
                    "away_odds_range": 5,
                    "avg_home_odds": -127.5,
                    "avg_away_odds": 107.5
                },
                {
                    "game_id": 2003,
                    "home_team": "Dallas Cowboys",
                    "away_team": "New York Giants",
                    "week": 18,
                    "season": 2026,
                    "sportsbooks_count": 3,
                    "best_home_odds": -275,
                    "worst_home_odds": -285,
                    "best_away_odds": 225,
                    "worst_away_odds": 235,
                    "home_odds_range": 10,
                    "away_odds_range": 10,
                    "avg_home_odds": -280.0,
                    "avg_away_odds": 230.0
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock live NFL odds efficiency analysis data"
        }
        
        return mock_efficiency
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/week/{week}")
async def get_live_odds_nfl_by_week(week: int, season: int = Query(2026, description="Season to filter"), 
                                   bookmaker: str = Query(None, description="Sportsbook to filter")):
    """Get live NFL odds for a specific week"""
    try:
        # Return mock week data for now
        mock_week_odds = [
            {
                "id": 16,
                "sport": 1,
                "game_id": 2003,
                "home_team": "Dallas Cowboys",
                "away_team": "New York Giants",
                "home_odds": -280,
                "away_odds": 230,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "week": week,
                "season": season,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
            },
            {
                "id": 17,
                "sport": 1,
                "game_id": 2004,
                "home_team": "Green Bay Packers",
                "away_team": "Chicago Bears",
                "home_odds": -190,
                "away_odds": 160,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "week": week,
                "season": season,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
            },
            {
                "id": 18,
                "sport": 1,
                "game_id": 2005,
                "home_team": "New England Patriots",
                "away_team": "New York Jets",
                "home_odds": -140,
                "away_odds": 120,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "week": week,
                "season": season,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
            }
        ]
        
        # Apply bookmaker filter
        if bookmaker:
            mock_week_odds = [o for o in mock_week_odds if o['bookmaker'].lower() == bookmaker.lower()]
        
        return {
            "week": week,
            "season": season,
            "odds": mock_week_odds,
            "total": len(mock_week_odds),
            "bookmaker": bookmaker,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock live NFL odds for week {week}, season {season}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "week": week,
            "season": season,
            "bookmaker": bookmaker,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/live-odds-nfl/search")
async def search_live_odds_nfl(query: str = Query(..., description="Search query"), 
                              bookmaker: str = Query(None, description="Sportsbook to filter"),
                              limit: int = Query(20, description="Number of results to return")):
    """Search live NFL odds by team name or sportsbook"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "sport": 1,
                "game_id": 2001,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_odds": -165,
                "away_odds": 145,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "week": 20,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 6,
                "sport": 1,
                "game_id": 2003,
                "home_team": "Dallas Cowboys",
                "away_team": "New York Giants",
                "home_odds": -280,
                "away_odds": 230,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=20)).isoformat()
            },
            {
                "id": 7,
                "sport": 1,
                "game_id": 2004,
                "home_team": "Green Bay Packers",
                "away_team": "Chicago Bears",
                "home_odds": -190,
                "away_odds": 160,
                "draw_odds": None,
                "bookmaker": "DraftKings",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "week": 18,
                "season": 2026,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
            }
        ]
        
        # Apply filters
        if bookmaker:
            mock_results = [r for r in mock_results if r['bookmaker'].lower() == bookmaker.lower()]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['home_team'].lower() or 
                   query_lower in r['away_team'].lower() or
                   query_lower in r['bookmaker'].lower()
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
            "bookmaker": bookmaker,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
'''
    
    # Add the endpoints before the anomaly endpoints
    if "# Brain Anomaly Detection Endpoints" in content:
        content = content.replace("# Brain Anomaly Detection Endpoints", live_odds_nfl_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += live_odds_nfl_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Live odds NFL endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_live_odds_nfl_endpoints())
