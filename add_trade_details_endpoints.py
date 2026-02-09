#!/usr/bin/env python3
"""
ADD TRADE DETAILS ENDPOINTS - Add trade tracking endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_trade_details_endpoints():
    """Add trade tracking endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the trade details endpoints
    trade_details_code = '''

# Trade Details Tracking Endpoints
@router.get("/trade-details")
async def get_trade_details(trade_id: str = Query(None, description="Trade ID to filter"),
                           team_id: int = Query(None, description="Team ID to filter"),
                           player_id: int = Query(None, description="Player ID to filter"),
                           asset_type: str = Query(None, description="Asset type to filter"),
                           recent: bool = Query(False, description="Get recent trades"),
                           limit: int = Query(50, description="Number of trade details to return")):
    """Get trade details with optional filters"""
    try:
        # Return mock trade details data for now
        mock_trade_details = [
            {
                "id": 1,
                "trade_id": "NBA_2024_001",
                "player_id": 1,
                "from_team_id": 5,
                "to_team_id": 3,
                "asset_type": "player",
                "asset_description": "Star forward with championship experience",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_id": "NBA_2024_001",
                "player_id": 2,
                "from_team_id": 3,
                "to_team_id": 5,
                "asset_type": "player",
                "asset_description": "All-star guard with scoring ability",
                "player_name": "Devin Booker",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 3,
                "trade_id": "NBA_2024_002",
                "player_id": 3,
                "from_team_id": 4,
                "to_team_id": 7,
                "asset_type": "player",
                "asset_description": "Elite point guard with playmaking skills",
                "player_name": "Kyle Lowry",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            },
            {
                "id": 4,
                "trade_id": "NBA_2024_002",
                "player_id": 4,
                "from_team_id": 7,
                "to_team_id": 4,
                "asset_type": "player",
                "asset_description": "Veteran center with defensive presence",
                "player_name": "Nikola Jokic",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            },
            {
                "id": 5,
                "trade_id": "NFL_2024_001",
                "player_id": 101,
                "from_team_id": 101,
                "to_team_id": 102,
                "asset_type": "player",
                "asset_description": "Elite quarterback with Super Bowl experience",
                "player_name": "Aaron Rodgers",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
            },
            {
                "id": 6,
                "trade_id": "NFL_2024_001",
                "player_id": 102,
                "from_team_id": 102,
                "to_team_id": 101,
                "asset_type": "player",
                "asset_description": "Pro Bowl wide receiver with speed",
                "player_name": "Davante Adams",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
            },
            {
                "id": 7,
                "trade_id": "MLB_2024_001",
                "player_id": 201,
                "from_team_id": 201,
                "to_team_id": 202,
                "asset_type": "player",
                "asset_description": "Power-hitting first baseman with MVP potential",
                "player_name": "Pete Alonso",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
            },
            {
                "id": 8,
                "trade_id": "MLB_2024_001",
                "player_id": 202,
                "from_team_id": 202,
                "to_team_id": 201,
                "asset_type": "player",
                "asset_description": "Ace pitcher with strikeout ability",
                "player_name": "Jacob deGrom",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
            },
            {
                "id": 9,
                "trade_id": "NHL_2024_001",
                "player_id": 301,
                "from_team_id": 301,
                "to_team_id": 302,
                "asset_type": "player",
                "asset_description": "Elite center with scoring ability",
                "player_name": "Connor McDavid",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat()
            },
            {
                "id": 10,
                "trade_id": "NHL_2024_001",
                "player_id": 302,
                "from_team_id": 302,
                "to_team_id": 301,
                "asset_type": "player",
                "asset_description": "Power forward with physical presence",
                "player_name": "Nathan MacKinnon",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat()
            },
            {
                "id": 11,
                "trade_id": "NBA_2024_005",
                "player_id": 9,
                "from_team_id": 11,
                "to_team_id": 12,
                "asset_type": "draft_pick",
                "asset_description": "2025 first round draft pick (lottery protected)",
                "player_name": "2025 1st Round Pick",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
            },
            {
                "id": 12,
                "trade_id": "NBA_2024_005",
                "player_id": 10,
                "from_team_id": 12,
                "to_team_id": 11,
                "asset_type": "player",
                "asset_description": "Young center with defensive potential",
                "player_name": "Walker Kessler",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_trades = mock_trade_details
        if trade_id:
            filtered_trades = [t for t in filtered_trades if t['trade_id'] == trade_id]
        if team_id:
            filtered_trades = [t for t in filtered_trades if t['from_team_id'] == team_id or t['to_team_id'] == team_id]
        if player_id:
            filtered_trades = [t for t in filtered_trades if t['player_id'] == player_id]
        if asset_type:
            filtered_trades = [t for t in filtered_trades if t['asset_type'] == asset_type]
        
        # Apply sorting
        if recent:
            filtered_trades = sorted(filtered_trades, key=lambda x: x['created_at'], reverse=True)
        
        return {
            "trade_details": filtered_trades[:limit],
            "total": len(filtered_trades),
            "filters": {
                "trade_id": trade_id,
                "team_id": team_id,
                "player_id": player_id,
                "asset_type": asset_type,
                "recent": recent,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock trade details data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/statistics")
async def get_trade_details_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get trade details statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_trade_records": 28,
            "unique_trades": 14,
            "unique_players": 28,
            "unique_from_teams": 12,
            "unique_to_teams": 12,
            "unique_asset_types": 2,
            "player_trades": 26,
            "draft_pick_trades": 2,
            "same_team_trades": 0,
            "different_team_trades": 28,
            "asset_type_stats": [
                {
                    "asset_type": "player",
                    "total_trades": 26,
                    "unique_trades": 13,
                    "unique_players": 26
                },
                {
                    "asset_type": "draft_pick",
                    "total_trades": 2,
                    "unique_trades": 1,
                    "unique_players": 2
                }
            ],
            "team_stats": [
                {
                    "team_id": 5,
                    "trades_sent": 2,
                    "unique_trade_ids_sent": 2
                },
                {
                    "team_id": 3,
                    "trades_sent": 2,
                    "unique_trade_ids_sent": 2
                },
                {
                    "team_id": 4,
                    "trades_sent": 2,
                    "unique_trade_ids_sent": 2
                },
                {
                    "team_id": 7,
                    "trades_sent": 2,
                    "unique_trade_ids_sent": 2
                },
                {
                    "team_id": 101,
                    "trades_sent": 2,
                    "unique_trade_ids_sent": 2
                }
            ],
            "player_stats": [
                {
                    "player_id": 1,
                    "player_name": "Kevin Durant",
                    "trade_count": 1,
                    "unique_trade_count": 1,
                    "unique_from_teams": 1,
                    "unique_to_teams": 1
                },
                {
                    "player_id": 2,
                    "player_name": "Devin Booker",
                    "trade_count": 1,
                    "unique_trade_count": 1,
                    "unique_from_teams": 1,
                    "unique_to_teams": 1
                },
                {
                    "player_id": 3,
                    "player_name": "Kyle Lowry",
                    "trade_count": 1,
                    "unique_trade_count": 1,
                    "unique_from_teams": 1,
                    "unique_to_teams": 1
                },
                {
                    "player_id": 4,
                    "player_name": "Nikola Jokic",
                    "trade_count": 1,
                    "unique_trade_count": 1,
                    "unique_from_teams": 1,
                    "unique_to_teams": 1
                },
                {
                    "player_id": 101,
                    "player_name": "Aaron Rodgers",
                    "trade_count": 1,
                    "unique_trade_count": 1,
                    "unique_from_teams": 1,
                    "unique_to_teams": 1
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock trade details statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/trade/{trade_id}")
async def get_trade_details_by_trade_id(trade_id: str):
    """Get trade details for a specific trade"""
    try:
        # Return mock trade-specific data for now
        mock_trade_summary = {
            "trade_id": trade_id,
            "total_assets": 2,
            "from_teams": [5, 3],
            "to_teams": [3, 5],
            "player_assets": [
                {
                    "player_id": 1,
                    "player_name": "Kevin Durant",
                    "asset_type": "player",
                    "asset_description": "Star forward with championship experience",
                    "from_team_id": 5,
                    "to_team_id": 3
                },
                {
                    "player_id": 2,
                    "player_name": "Devin Booker",
                    "asset_type": "player",
                    "asset_description": "All-star guard with scoring ability",
                    "from_team_id": 3,
                    "to_team_id": 5
                }
            ],
            "draft_pick_assets": [],
            "other_assets": [],
            "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        }
        
        return {
            "trade_summary": mock_trade_summary,
            "trade_id": trade_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trade summary for {trade_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "trade_id": trade_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/team/{team_id}")
async def get_trade_details_by_team(team_id: int, role: str = Query("both", description="Team role: from, to, or both")):
    """Get trade details for a specific team"""
    try:
        # Return mock team-specific data for now
        mock_team_trades = [
            {
                "id": 1,
                "trade_id": "NBA_2024_001",
                "player_id": 1,
                "from_team_id": team_id,
                "to_team_id": 3,
                "asset_type": "player",
                "asset_description": "Star forward with championship experience",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_id": "NBA_2024_002",
                "player_id": 3,
                "from_team_id": 4,
                "to_team_id": team_id,
                "asset_type": "player",
                "asset_description": "Elite point guard with playmaking skills",
                "player_name": "Kyle Lowry",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            }
        ]
        
        # Filter by role
        if role == "from":
            mock_team_trades = [t for t in mock_team_trades if t['from_team_id'] == team_id]
        elif role == "to":
            mock_team_trades = [t for t in mock_team_trades if t['to_team_id'] == team_id]
        
        return {
            "team_id": team_id,
            "role": role,
            "trade_details": mock_team_trades,
            "total": len(mock_team_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trade details for team {team_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "team_id": team_id,
            "role": role,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/player/{player_id}")
async def get_trade_details_by_player(player_id: int):
    """Get trade details for a specific player"""
    try:
        # Return mock player-specific data for now
        mock_player_trades = [
            {
                "id": 1,
                "trade_id": "NBA_2024_001",
                "player_id": player_id,
                "from_team_id": 5,
                "to_team_id": 3,
                "asset_type": "player",
                "asset_description": "Star forward with championship experience",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_id": "NBA_2024_003",
                "player_id": player_id,
                "from_team_id": 6,
                "to_team_id": 8,
                "asset_type": "player",
                "asset_description": "Rising star with high potential",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
            }
        ]
        
        return {
            "player_id": player_id,
            "trade_details": mock_player_trades,
            "total": len(mock_player_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trade details for player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_id": player_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/asset-type/{asset_type}")
async def get_trade_details_by_asset_type(asset_type: str, limit: int = Query(50, description="Number of trade details to return")):
    """Get trade details by asset type"""
    try:
        # Return mock asset-type-specific data for now
        mock_asset_trades = [
            {
                "id": 1,
                "trade_id": "NBA_2024_001",
                "player_id": 1,
                "from_team_id": 5,
                "to_team_id": 3,
                "asset_type": asset_type,
                "asset_description": "Star forward with championship experience",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_id": "NBA_2024_002",
                "player_id": 3,
                "from_team_id": 4,
                "to_team_id": 7,
                "asset_type": asset_type,
                "asset_description": "Elite point guard with playmaking skills",
                "player_name": "Kyle Lowry",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            }
        ]
        
        return {
            "asset_type": asset_type,
            "trade_details": mock_asset_trades[:limit],
            "total": len(mock_asset_trades),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trade details for asset type {asset_type}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "asset_type": asset_type,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trade-details/search")
async def search_trade_details(query: str = Query(..., description="Search query"),
                              limit: int = Query(20, description="Number of results to return")):
    """Search trade details by player name or trade ID"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "trade_id": "NBA_2024_001",
                "player_id": 1,
                "from_team_id": 5,
                "to_team_id": 3,
                "asset_type": "player",
                "asset_description": "Star forward with championship experience",
                "player_name": "Kevin Durant",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_id": "NBA_2024_002",
                "player_id": 3,
                "from_team_id": 4,
                "to_team_id": 7,
                "asset_type": "player",
                "asset_description": "Elite point guard with playmaking skills",
                "player_name": "Kyle Lowry",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['trade_id'].lower() or 
                   query_lower in r['player_name'].lower() or 
                   (r['asset_description'] and query_lower in r['asset_description'].lower())
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
        content = content.replace("# Brain Anomaly Detection Endpoints", trade_details_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += trade_details_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Trade details endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_trade_details_endpoints())
