#!/usr/bin/env python3
"""
ADD GAME RESULTS ENDPOINTS - Add game results tracking endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_game_results_endpoints():
    """Add game results endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the game results endpoints
    game_results_code = '''

# Game Results Tracking Endpoints
@router.get("/game-results")
async def get_game_results(date: str = Query(None, description="Date to filter (YYYY-MM-DD)"), sport_id: int = Query(None, description="Sport ID to filter")):
    """Get game results for a specific date"""
    try:
        # Return mock game results data for now
        mock_results = [
            {
                "id": 1,
                "game_id": 1001,
                "external_fixture_id": "nfl_2026_02_08_kc_buf",
                "home_score": 31,
                "away_score": 28,
                "period_scores": {
                    "Q1": {"home": 7, "away": 7},
                    "Q2": {"home": 10, "away": 14},
                    "Q3": {"home": 7, "away": 0},
                    "Q4": {"home": 7, "away": 7}
                },
                "is_settled": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
            },
            {
                "id": 2,
                "game_id": 1002,
                "external_fixture_id": "nfl_2026_02_08_phi_nyg",
                "home_score": 24,
                "away_score": 17,
                "period_scores": {
                    "Q1": {"home": 3, "away": 7},
                    "Q2": {"home": 14, "away": 3},
                    "Q3": {"home": 0, "away": 7},
                    "Q4": {"home": 7, "away": 0}
                },
                "is_settled": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
            },
            {
                "id": 3,
                "game_id": 1003,
                "external_fixture_id": "nfl_2026_02_08_dal_sf",
                "home_score": 35,
                "away_score": 42,
                "period_scores": {
                    "Q1": {"home": 14, "away": 7},
                    "Q2": {"home": 7, "away": 14},
                    "Q3": {"home": 7, "away": 14},
                    "Q4": {"home": 7, "away": 7}
                },
                "is_settled": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat()
            },
            {
                "id": 4,
                "game_id": 2001,
                "external_fixture_id": "nba_2026_02_08_lal_bos",
                "home_score": 118,
                "away_score": 112,
                "period_scores": {
                    "Q1": {"home": 28, "away": 24},
                    "Q2": {"home": 32, "away": 30},
                    "Q3": {"home": 29, "away": 28},
                    "Q4": {"home": 29, "away": 30}
                },
                "is_settled": True,
                "settled_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 5,
                "game_id": 1005,
                "external_fixture_id": "nfl_2026_02_09_ari_sea",
                "home_score": None,
                "away_score": None,
                "period_scores": {},
                "is_settled": False,
                "settled_at": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            }
        ]
        
        return {
            "results": mock_results,
            "total": len(mock_results),
            "date": date or datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock game results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/game-results/pending")
async def get_pending_games():
    """Get all pending games"""
    try:
        # Return mock pending games data for now
        mock_pending = [
            {
                "id": 5,
                "game_id": 1005,
                "external_fixture_id": "nfl_2026_02_09_ari_sea",
                "home_score": None,
                "away_score": None,
                "period_scores": {},
                "is_settled": False,
                "settled_at": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            },
            {
                "id": 6,
                "game_id": 2004,
                "external_fixture_id": "nba_2026_02_09_chi_cle",
                "home_score": None,
                "away_score": None,
                "period_scores": {},
                "is_settled": False,
                "settled_at": None,
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            }
        ]
        
        return {
            "pending_games": mock_pending,
            "total": len(mock_pending),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock pending games data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/game-results/statistics")
async def get_game_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get game statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_games": 8,
            "settled_games": 6,
            "pending_games": 2,
            "avg_home_score": 28.5,
            "avg_away_score": 26.8,
            "avg_total_score": 55.3,
            "home_wins": 4,
            "away_wins": 2,
            "ties": 0,
            "home_win_rate": 66.7,
            "away_win_rate": 33.3,
            "tie_rate": 0.0,
            "by_sport": [
                {
                    "sport_id": 32,
                    "total_games": 5,
                    "settled_games": 4,
                    "avg_home_score": 30.0,
                    "avg_away_score": 28.8,
                    "home_wins": 3,
                    "away_wins": 1
                },
                {
                    "sport_id": 30,
                    "total_games": 3,
                    "settled_games": 2,
                    "avg_home_score": 25.5,
                    "avg_away_score": 24.0,
                    "home_wins": 1,
                    "away_wins": 1
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock game statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/game-results/{game_id}")
async def get_game_result_detail(game_id: int):
    """Get detailed game result by ID"""
    try:
        # Return mock detailed game result data for now
        mock_detail = {
            "id": 1,
            "game_id": game_id,
            "external_fixture_id": "nfl_2026_02_08_kc_buf",
            "home_score": 31,
            "away_score": 28,
            "period_scores": {
                "Q1": {"home": 7, "away": 7},
                "Q2": {"home": 10, "away": 14},
                "Q3": {"home": 7, "away": 0},
                "Q4": {"home": 7, "away": 7}
            },
            "is_settled": True,
            "settled_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            "game_details": {
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "venue": "Arrowhead Stadium",
                "date": "2026-02-08",
                "start_time": "20:20 UTC",
                "duration": "3:15:00",
                "attendance": 76416,
                "weather": "Clear, 72°F"
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

@router.post("/game-results/settle")
async def settle_game_results(settlement_data: dict):
    """Settle game results"""
    try:
        # Simulate settling game results
        games_to_settle = settlement_data.get("games", [])
        
        settled_count = 0
        failed_count = 0
        settlement_results = []
        
        for game in games_to_settle:
            game_id = game.get("game_id")
            home_score = game.get("home_score")
            away_score = game.get("away_score")
            
            if not all([game_id, home_score is not None, away_score is not None]):
                failed_count += 1
                settlement_results.append({
                    "game_id": game_id,
                    "status": "failed",
                    "error": "Missing required fields"
                })
                continue
            
            # Simulate successful settlement
            settled_count += 1
            settlement_results.append({
                "game_id": game_id,
                "status": "settled",
                "home_score": home_score,
                "away_score": away_score,
                "settled_at": datetime.now(timezone.utc).isoformat()
            })
        
        return {
            "total_processed": len(games_to_settle),
            "settled_count": settled_count,
            "failed_count": failed_count,
            "settlement_results": settlement_results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock settlement completed for {settled_count} games"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.post("/game-results/create")
async def create_game_result(game_data: dict):
    """Create a new game result record"""
    try:
        # Simulate creating a game result
        game_id = game_data.get("game_id")
        external_fixture_id = game_data.get("external_fixture_id")
        
        if not all([game_id, external_fixture_id]):
            return {
                "status": "error",
                "error": "Missing required fields: game_id, external_fixture_id",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "status": "created",
            "game_id": game_id,
            "external_fixture_id": external_fixture_id,
            "home_score": None,
            "away_score": None,
            "is_settled": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock game result created for {game_id}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.put("/game-results/{game_id}")
async def update_game_result(game_id: int, result_data: dict):
    """Update game result with scores"""
    try:
        # Simulate updating game result
        home_score = result_data.get("home_score")
        away_score = result_data.get("away_score")
        period_scores = result_data.get("period_scores", {})
        
        if not all([home_score is not None, away_score is not None]):
            return {
                "status": "error",
                "error": "Missing required fields: home_score, away_score",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return {
            "status": "updated",
            "game_id": game_id,
            "home_score": home_score,
            "away_score": away_score,
            "period_scores": period_scores,
            "is_settled": True,
            "settled_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock game result updated for {game_id}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
'''
    
    # Add the endpoints before the anomaly endpoints
    if "# Brain Anomaly Detection Endpoints" in content:
        content = content.replace("# Brain Anomaly Detection Endpoints", game_results_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += game_results_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Game results endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_game_results_endpoints())
