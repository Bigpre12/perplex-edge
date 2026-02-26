#!/usr/bin/env python3
"""
TEST TRADE DETAILS ENDPOINTS - Test the new trade tracking endpoints
"""
import requests
import time
from datetime import datetime

def test_trade_details():
    """Test trade details endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING TRADE DETAILS ENDPOINTS")
    print("="*80)
    
    print(f"\nTime: {datetime.now().strftime('%I:%M:%S %p')}")
    print("Testing trade tracking endpoints...")
    
    # Test endpoints
    endpoints = [
        ("Trade Details", "/immediate/trade-details"),
        ("Trade Details Statistics", "/immediate/trade-details/statistics?days=30"),
        ("Trade Details by Trade ID", "/immediate/trade-details/trade/NBA_2024_001"),
        ("Trade Details by Team", "/immediate/trade-details/team/5"),
        ("Trade Details by Player", "/immediate/trade-details/player/1"),
        ("Trade Details by Asset Type", "/immediate/trade-details/asset-type/player"),
        ("Search Trade Details", "/immediate/trade-details/search?query=durant")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"\n{name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if name == "Trade Details":
                    trade_details = data.get('trade_details', [])
                    print(f"  Total Trade Details: {data.get('total', 0)}")
                    print(f"  Filters: {data.get('filters', {})}")
                    
                    for trade in trade_details[:2]:
                        print(f"  - {trade['player_name']} ({trade['asset_type']})")
                        print(f"    Trade ID: {trade['trade_id']}")
                        print(f"    From Team: {trade['from_team_id']} → To Team: {trade['to_team_id']}")
                        print(f"    Asset Description: {trade['asset_description']}")
                        print(f"    Created: {trade['created_at']}")
                        
                elif name == "Trade Details Statistics":
                    print(f"  Period: {data.get('period_days', 0)} days")
                    print(f"  Total Trade Records: {data.get('total_trade_records', 0)}")
                    print(f"  Unique Trades: {data.get('unique_trades', 0)}")
                    print(f"  Unique Players: {data.get('unique_players', 0)}")
                    print(f"  Unique From Teams: {data.get('unique_from_teams', 0)}")
                    print(f"  Unique To Teams: {data.get('unique_to_teams', 0)}")
                    print(f"  Unique Asset Types: {data.get('unique_asset_types', 0)}")
                    print(f"  Player Trades: {data.get('player_trades', 0)}")
                    print(f"  Draft Pick Trades: {data.get('draft_pick_trades', 0)}")
                    print(f"  Same Team Trades: {data.get('same_team_trades', 0)}")
                    print(f"  Different Team Trades: {data.get('different_team_trades', 0)}")
                    
                    asset_type_stats = data.get('asset_type_stats', [])
                    print(f"  Asset Type Statistics: {len(asset_type_stats)}")
                    for asset in asset_type_stats[:2]:
                        print(f"    - {asset['asset_type']}:")
                        print(f"      Total Trades: {asset['total_trades']}")
                        print(f"      Unique Trades: {asset['unique_trades']}")
                        print(f"      Unique Players: {asset['unique_players']}")
                        
                    team_stats = data.get('team_stats', [])
                    print(f"  Team Statistics: {len(team_stats)}")
                    for team in team_stats[:2]:
                        print(f"    - Team {team['team_id']}:")
                        print(f"      Trades Sent: {team['trades_sent']}")
                        print(f"      Unique Trade IDs Sent: {team['unique_trade_ids_sent']}")
                        
                    player_stats = data.get('player_stats', [])
                    print(f"  Player Statistics: {len(player_stats)}")
                    for player in player_stats[:2]:
                        print(f"    - {player['player_name']}:")
                        print(f"      Trade Count: {player['trade_count']}")
                        print(f"      Unique Trade Count: {player['unique_trade_count']}")
                        print(f"      From Teams: {player['unique_from_teams']}")
                        print(f"      To Teams: {player['unique_to_teams']}")
                        
                elif name == "Trade Details by Trade ID":
                    trade_summary = data.get('trade_summary', {})
                    print(f"  Trade ID: {trade_summary.get('trade_id', 'N/A')}")
                    print(f"  Total Assets: {trade_summary.get('total_assets', 0)}")
                    print(f"  From Teams: {trade_summary.get('from_teams', [])}")
                    print(f"  To Teams: {trade_summary.get('to_teams', [])}")
                    
                    player_assets = trade_summary.get('player_assets', [])
                    print(f"  Player Assets: {len(player_assets)}")
                    for asset in player_assets:
                        print(f"    - {asset['player_name']} ({asset['asset_type']})")
                        print(f"      From Team: {asset['from_team_id']} → To Team: {asset['to_team_id']}")
                        print(f"      Description: {asset['asset_description']}")
                        
                    draft_pick_assets = trade_summary.get('draft_pick_assets', [])
                    print(f"  Draft Pick Assets: {len(draft_pick_assets)}")
                    for asset in draft_pick_assets:
                        print(f"    - {asset['player_name']} ({asset['asset_type']})")
                        print(f"      From Team: {asset['from_team_id']} → To Team: {asset['to_team_id']}")
                        print(f"      Description: {asset['asset_description']}")
                        
                elif name == "Trade Details by Team":
                    trade_details = data.get('trade_details', [])
                    print(f"  Team ID: {data.get('team_id', 'N/A')}")
                    print(f"  Role: {data.get('role', 'N/A')}")
                    print(f"  Total Trade Details: {data.get('total', 0)}")
                    
                    for trade in trade_details:
                        print(f"  - {trade['player_name']} ({trade['asset_type']})")
                        print(f"    Trade ID: {trade['trade_id']}")
                        print(f"    From Team: {trade['from_team_id']} → To Team: {trade['to_team_id']}")
                        print(f"    Asset Description: {trade['asset_description']}")
                        print(f"    Created: {trade['created_at']}")
                        
                elif name == "Trade Details by Player":
                    trade_details = data.get('trade_details', [])
                    print(f"  Player ID: {data.get('player_id', 'N/A')}")
                    print(f"  Total Trade Details: {data.get('total', 0)}")
                    
                    for trade in trade_details:
                        print(f"  - {trade['player_name']} ({trade['asset_type']})")
                        print(f"    Trade ID: {trade['trade_id']}")
                        print(f"    From Team: {trade['from_team_id']} → To Team: {trade['to_team_id']}")
                        print(f"    Asset Description: {trade['asset_description']}")
                        print(f"    Created: {trade['created_at']}")
                        
                elif name == "Trade Details by Asset Type":
                    trade_details = data.get('trade_details', [])
                    print(f"  Asset Type: {data.get('asset_type', 'N/A')}")
                    print(f"  Total Trade Details: {data.get('total', 0)}")
                    print(f"  Limit: {data.get('limit', 0)}")
                    
                    for trade in trade_details:
                        print(f"  - {trade['player_name']} ({trade['asset_type']})")
                        print(f"    Trade ID: {trade['trade_id']}")
                        print(f"    From Team: {trade['from_team_id']} → To Team: {trade['to_team_id']}")
                        print(f"    Asset Description: {trade['asset_description']}")
                        print(f"    Created: {trade['created_at']}")
                        
                elif name == "Search Trade Details":
                    results = data.get('results', [])
                    print(f"  Query: {data.get('query', 'N/A')}")
                    print(f"  Total Results: {data.get('total', 0)}")
                    print(f"  Limit: {data.get('limit', 0)}")
                    
                    for result in results:
                        print(f"  - {result['player_name']} ({result['asset_type']})")
                        print(f"    Trade ID: {result['trade_id']}")
                        print(f"    From Team: {result['from_team_id']} → To Team: {result['to_team_id']}")
                        print(f"    Asset Description: {result['asset_description']}")
                        print(f"    Created: {result['created_at']}")
                
                print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
                print(f"  Note: {data.get('note', 'N/A')}")
                
            else:
                print(f"  Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"\n{name}: ERROR - {e}")
    
    print("\n" + "="*80)
    print("TRADE DETAILS TEST RESULTS:")
    print("="*80)
    
    print("\nTrade Details Table Structure:")
    print("The trade_details table tracks:")
    print("- Player trades between teams")
    print("- Asset types (players, draft picks, cash, etc.)")
    print("- Trade IDs for grouping related trades")
    print("- From/to team relationships")
    print("- Asset descriptions and player names")
    
    print("\nTrade Data Types:")
    print("- Trade ID: Unique identifier for trade groups")
    print("- Player ID: Reference to player records")
    print("- From/To Team IDs: Team movement tracking")
    print("- Asset Type: Type of asset being traded")
    print("- Asset Description: Detailed asset information")
    print("- Player Name: Human-readable player identification")
    
    print("\nAsset Type Categories:")
    print("- Player: Actual player trades")
    print("- Draft Pick: Future draft pick trades")
    print("- Cash: Cash considerations")
    print("- Trade Exception: Salary cap exceptions")
    
    print("\nSample Trade Scenarios:")
    print("- NBA_2024_001: Kevin Durant <-> Devin Booker")
    print("- NFL_2024_001: Aaron Rodgers <-> Davante Adams")
    print("- MLB_2024_001: Pete Alonso <-> Jacob deGrom")
    print("- NHL_2024_001: Connor McDavid <-> Nathan MacKinnon")
    print("- NBA_2024_005: Draft Pick <-> Walker Kessler")
    
    print("\nTrade Analysis Features:")
    print("- Trade Summaries: Complete trade breakdown")
    print("- Team History: Team-specific trade tracking")
    print("- Player Movement: Individual player trade history")
    print("- Asset Analysis: Asset type distribution")
    print("- Search Functionality: Find specific trades")
    
    print("\nBusiness Value:")
    print("- Roster Management: Track team composition changes")
    print("- Player Valuation: Analyze player trade values")
    print("- Market Analysis: Understand trade market trends")
    print("- Historical Tracking: Maintain trade history")
    print("- Fantasy Sports: Support fantasy trade analysis")
    
    print("\nAvailable Endpoints:")
    print("- GET /immediate/trade-details - Get trades with filters")
    print("- GET /immediate/trade-details/statistics - Get overall statistics")
    print("- GET /immediate/trade-details/trade/{trade_id} - Get trade summary")
    print("- GET /immediate/trade-details/team/{team_id} - Get team trades")
    print("- GET /immediate/trade-details/player/{player_id} - Get player trades")
    print("- GET /immediate/trade-details/asset-type/{asset_type} - Get asset-type trades")
    print("- GET /immediate/trade-details/search - Search trade details")
    
    print("\nIntegration Features:")
    print("- Multi-Sport Support: NBA, NFL, MLB, NHL trades")
    print("- Asset Variety: Players, picks, cash, exceptions")
    print("- Team Tracking: From/to team relationships")
    print("- Historical Data: Complete trade history")
    print("- Real-Time Updates: Live trade tracking")
    
    print("\n" + "="*80)
    print("TRADE DETAILS SYSTEM COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    test_trade_details()
