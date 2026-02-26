#!/usr/bin/env python3
"""
ADD ODDS SNAPSHOTS ENDPOINTS - Add odds snapshots tracking endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_odds_snapshots_endpoints():
    """Add odds snapshots tracking endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the odds snapshots endpoints
    odds_snapshots_code = '''

# Odds Snapshots Tracking Endpoints
@router.get("/odds-snapshots")
async def get_odds_snapshots(game_id: int = Query(None, description="Game ID to filter"), 
                           player_id: int = Query(None, description="Player ID to filter"),
                           bookmaker: str = Query(None, description="Bookmaker to filter"),
                           hours: int = Query(24, description="Hours of data to analyze"),
                           limit: int = Query(50, description="Number of snapshots to return")):
    """Get odds snapshots with optional filters"""
    try:
        # Return mock odds snapshots data for now
        mock_snapshots = [
            {
                "id": 1,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 2,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 3,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.5",
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 4,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_92",
                "external_outcome_id": "over_28.5",
                "bookmaker": "DraftKings",
                "line_value": 28.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 5,
                "game_id": 664,
                "market_id": 101,
                "player_id": 101,
                "external_fixture_id": "nfl_2026_664",
                "external_market_id": "player_pass_yards_101",
                "external_outcome_id": "over_285.5",
                "bookmaker": "DraftKings",
                "line_value": 285.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            },
            {
                "id": 6,
                "game_id": 666,
                "market_id": 201,
                "player_id": 201,
                "external_fixture_id": "mlb_2026_666",
                "external_market_id": "player_hr_201",
                "external_outcome_id": "over_1.5",
                "bookmaker": "DraftKings",
                "line_value": 1.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(hours=1).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(hours=1).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=1).isoformat()
            },
            {
                "id": 7,
                "game_id": 668,
                "market_id": 301,
                "player_id": 301,
                "external_fixture_id": "nhl_2026_668",
                "external_market_id": "player_points_301",
                "external_outcome_id": "over_1.5",
                "bookmaker": "DraftKings",
                "line_value": 1.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            }
        ]
        
        # Apply filters
        filtered_snapshots = mock_snapshots
        if game_id:
            filtered_snapshots = [s for s in filtered_snapshots if s['game_id'] == game_id]
        if player_id:
            filtered_snapshots = [s for s in filtered_snapshots if s['player_id'] == player_id]
        if bookmaker:
            filtered_snapshots = [s for s in filtered_snapshots if s['bookmaker'].lower() == bookmaker.lower()]
        
        return {
            "snapshots": filtered_snapshots[:limit],
            "total": len(filtered_snapshots),
            "filters": {
                "game_id": game_id,
                "player_id": player_id,
                "bookmaker": bookmaker,
                "hours": hours,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock odds snapshots data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/movements/{game_id}")
async def get_odds_movements(game_id: int, market_id: int = Query(None, description="Market ID to filter"),
                           player_id: int = Query(None, description="Player ID to filter"),
                           hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds movements for a specific game"""
    try:
        # Return mock movements data for now
        mock_movements = [
            {
                "bookmaker": "DraftKings",
                "line_value": 13.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_price": None,
                "prev_american_odds": None
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9524,
                "american_odds": -105,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "line_movement": 0.5,
                "price_movement": 0.0433,
                "odds_movement": 5,
                "prev_line_value": 13.5,
                "prev_price": 1.9091,
                "prev_american_odds": -110
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9524,
                "american_odds": -105,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": 14.0,
                "prev_price": 1.9524,
                "prev_american_odds": -105
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9412,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "line_movement": 0,
                "price_movement": -0.0112,
                "odds_movement": -3,
                "prev_line_value": 14.0,
                "prev_price": 1.9524,
                "prev_american_odds": -105
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9615,
                "american_odds": -103,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0203,
                "odds_movement": 5,
                "prev_line_value": 14.0,
                "prev_price": 1.9412,
                "prev_american_odds": -108
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0091,
                "odds_movement": 1,
                "prev_line_value": 14.0,
                "prev_price": 1.9615,
                "prev_american_odds": -103
            },
            {
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_price": None,
                "prev_american_odds": None
            },
            {
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0115,
                "odds_movement": 2,
                "prev_line_value": 13.5,
                "prev_price": 1.9231,
                "prev_american_odds": -108
            },
            {
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_price": None,
                "prev_american_odds": None
            },
            {
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0140,
                "odds_movement": 2,
                "prev_line_value": 14.5,
                "prev_price": 1.9091,
                "prev_american_odds": -110
            }
        ]
        
        # Apply filters
        filtered_movements = mock_movements
        if market_id:
            # Filter by market_id logic would go here
            pass
        if player_id:
            # Filter by player_id logic would go here
            pass
        
        return {
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "movements": filtered_movements,
            "total_movements": len(filtered_movements),
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds movements for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/comparison/{game_id}")
async def get_odds_comparison(game_id: int, market_id: int = Query(None, description="Market ID to filter"),
                            player_id: int = Query(None, description="Player ID to filter"),
                            hours: int = Query(1, description="Hours of data to analyze")):
    """Compare odds across bookmakers for a specific game"""
    try:
        # Return mock comparison data for now
        mock_comparison = [
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Calculate best odds
        best_over = max(mock_comparison, key=lambda x: x['price'] if x['side'] == 'over' else float('inf'))
        best_under = max(mock_comparison, key=lambda x: x['price'] if x['side'] == 'under' else float('inf'))
        
        return {
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "comparison": mock_comparison,
            "best_over_odds": {
                "bookmaker": best_over['bookmaker'],
                "line_value": best_over['line_value'],
                "price": best_over['price'],
                "american_odds": best_over['american_odds']
            },
            "best_under_odds": {
                "bookmaker": best_under['bookmaker'],
                "line_value": best_under['line_value'],
                "price": best_under['price'],
                "american_odds": best_under['american_odds']
            },
            "total_bookmakers": len(mock_comparison),
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds comparison for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/statistics")
async def get_odds_snapshots_statistics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds snapshots statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_hours": hours,
            "total_snapshots": 25,
            "unique_games": 4,
            "unique_markets": 6,
            "unique_players": 6,
            "unique_bookmakers": 3,
            "unique_fixtures": 4,
            "unique_external_markets": 6,
            "unique_external_outcomes": 12,
            "avg_line_value": 45.2,
            "avg_price": 1.9345,
            "avg_american_odds": -106,
            "over_snapshots": 18,
            "under_snapshots": 7,
            "active_snapshots": 25,
            "by_bookmaker": [
                {
                    "bookmaker": "DraftKings",
                    "total_snapshots": 12,
                    "unique_games": 4,
                    "unique_markets": 5,
                    "avg_line_value": 48.5,
                    "avg_price": 1.9412,
                    "avg_american_odds": -104,
                    "over_snapshots": 9,
                    "under_snapshots": 3
                },
                {
                    "bookmaker": "FanDuel",
                    "total_snapshots": 8,
                    "unique_games": 3,
                    "unique_markets": 4,
                    "avg_line_value": 42.1,
                    "avg_price": 1.9286,
                    "avg_american_odds": -107,
                    "over_snapshots": 6,
                    "under_snapshots": 2
                },
                {
                    "bookmaker": "BetMGM",
                    "total_snapshots": 5,
                    "unique_games": 2,
                    "unique_markets": 3,
                    "avg_line_value": 38.7,
                    "avg_price": 1.9162,
                    "avg_american_odds": -109,
                    "over_snapshots": 3,
                    "under_snapshots": 2
                }
            ],
            "by_game": [
                {
                    "game_id": 662,
                    "total_snapshots": 12,
                    "unique_markets": 2,
                    "unique_players": 2,
                    "unique_bookmakers": 3,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                    "last_snapshot": datetime.now(timezone.utc).isoformat()
                },
                {
                    "game_id": 664,
                    "total_snapshots": 4,
                    "unique_markets": 2,
                    "unique_players": 1,
                    "unique_bookmakers": 1,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                    "last_snapshot": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
                },
                {
                    "game_id": 666,
                    "total_snapshots": 3,
                    "unique_markets": 2,
                    "unique_players": 1,
                    "unique_bookmakers": 1,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                    "last_snapshot": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
                },
                {
                    "game_id": 668,
                    "total_snapshots": 2,
                    "unique_markets": 1,
                    "unique_players": 1,
                    "unique_bookmakers": 1,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                    "last_snapshot": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
                }
            ],
            "by_side": [
                {
                    "side": "over",
                    "total_snapshots": 18,
                    "avg_line_value": 47.8,
                    "avg_price": 1.9456,
                    "avg_american_odds": -103,
                    "unique_bookmakers": 3,
                    "unique_games": 4
                },
                {
                    "side": "under",
                    "total_snapshots": 7,
                    "avg_line_value": 38.2,
                    "avg_price": 1.9091,
                    "avg_american_odds": -110,
                    "unique_bookmakers": 2,
                    "unique_games": 3
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock odds snapshots statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/bookmaker/{bookmaker}")
async def get_odds_by_bookmaker(bookmaker: str, hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds snapshots from a specific bookmaker"""
    try:
        # Return mock bookmaker data for now
        mock_bookmaker_snapshots = [
            {
                "id": 1,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": bookmaker,
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 4,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_92",
                "external_outcome_id": "over_28.5",
                "bookmaker": bookmaker,
                "line_value": 28.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(minutes=30).isoformat()
            },
            {
                "id": 5,
                "game_id": 664,
                "market_id": 101,
                "player_id": 101,
                "external_fixture_id": "nfl_2026_664",
                "external_market_id": "player_pass_yards_101",
                "external_outcome_id": "over_285.5",
                "bookmaker": bookmaker,
                "line_value": 285.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat(),
                "updated_at": datetime.now(timezone.utc) - timedelta(hours=2).isoformat()
            }
        ]
        
        return {
            "bookmaker": bookmaker,
            "snapshots": mock_bookmaker_snapshots,
            "total": len(mock_bookmaker_snapshots),
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds snapshots for {bookmaker}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "bookmaker": bookmaker,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/player/{player_id}")
async def get_odds_by_player(player_id: int, bookmaker: str = Query(None, description="Bookmaker to filter"),
                            hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds snapshots for a specific player"""
    try:
        # Return mock player data for now
        mock_player_snapshots = [
            {
                "id": 1,
                "game_id": 662,
                "market_id": 91,
                "player_id": player_id,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 2,
                "game_id": 662,
                "market_id": 91,
                "player_id": player_id,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 3,
                "game_id": 662,
                "market_id": 91,
                "player_id": player_id,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.5",
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Apply bookmaker filter
        if bookmaker:
            mock_player_snapshots = [s for s in mock_player_snapshots if s['bookmaker'].lower() == bookmaker.lower()]
        
        return {
            "player_id": player_id,
            "snapshots": mock_player_snapshots,
            "total": len(mock_player_snapshots),
            "bookmaker": bookmaker,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds snapshots for player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_id": player_id,
            "bookmaker": bookmaker,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/search")
async def search_odds_snapshots(query: str = Query(..., description="Search query"), 
                              bookmaker: str = Query(None, description="Bookmaker to filter"),
                              hours: int = Query(24, description="Hours of data to analyze"),
                              limit: int = Query(50, description="Number of results to return")):
    """Search odds snapshots by external IDs or bookmaker"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 2,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
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
                if query_lower in r['external_fixture_id'].lower() or 
                   query_lower in r['external_market_id'].lower() or
                   query_lower in r['external_outcome_id'].lower() or
                   query_lower in r['bookmaker'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "bookmaker": bookmaker,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "bookmaker": bookmaker,
            "hours": hours,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
'''
    
    # Add the endpoints before the anomaly endpoints
    if "# Brain Anomaly Detection Endpoints" in content:
        content = content.replace("# Brain Anomaly Detection Endpoints", odds_snapshots_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += odds_snapshots_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Odds snapshots endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_odds_snapshots_endpoints())
