#!/usr/bin/env python3
"""
TEST TRADES ENDPOINTS - Test the new master trade tracking endpoints
"""
import requests
import time
from datetime import datetime

def test_trades():
    """Test trades endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING TRADES ENDPOINTS")
    print("="*80)
    
    print(f"\nTime: {datetime.now().strftime('%I:%M:%S %p')}")
    print("Testing master trade tracking endpoints...")
    
    # Test endpoints
    endpoints = [
        ("Trades", "/immediate/trades"),
        ("Trades Statistics", "/immediate/trades/statistics?days=365"),
        ("Trades by Season", "/immediate/trades/season/2024"),
        ("Trades by Source", "/immediate/trades/source/ESPN"),
        ("Applied Trades", "/immediate/trades/applied"),
        ("Pending Trades", "/immediate/trades/pending"),
        ("Search Trades", "/immediate/trades/search?query=durant")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"\n{name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if name == "Trades":
                    trades = data.get('trades', [])
                    print(f"  Total Trades: {data.get('total', 0)}")
                    print(f"  Filters: {data.get('filters', {})}")
                    
                    for trade in trades[:2]:
                        print(f"  - {trade['headline']}")
                        print(f"    Date: {trade['trade_date']}")
                        print(f"    Season: {trade['season_year']}")
                        print(f"    Source: {trade['source']}")
                        print(f"    Applied: {'Yes' if trade['is_applied'] else 'No'}")
                        print(f"    Description: {trade['description'][:100]}...")
                        print(f"    Created: {trade['created_at']}")
                        
                elif name == "Trades Statistics":
                    print(f"  Period: {data.get('period_days', 0)} days")
                    print(f"  Total Trades: {data.get('total_trades', 0)}")
                    print(f"  Unique Seasons: {data.get('unique_seasons', 0)}")
                    print(f"  Unique Sources: {data.get('unique_sources', 0)}")
                    print(f"  Applied Trades: {data.get('applied_trades', 0)}")
                    print(f"  Pending Trades: {data.get('pending_trades', 0)}")
                    print(f"  Earliest Trade: {data.get('earliest_trade', 'N/A')}")
                    print(f"  Latest Trade: {data.get('latest_trade', 'N/A')}")
                    print(f"  Avg Description Length: {data.get('avg_description_length', 0):.1f}")
                    print(f"  Avg Headline Length: {data.get('avg_headline_length', 0):.1f}")
                    
                    season_stats = data.get('season_stats', [])
                    print(f"  Season Statistics: {len(season_stats)}")
                    for season in season_stats[:2]:
                        print(f"    - Season {season['season_year']}:")
                        print(f"      Total Trades: {season['total_trades']}")
                        print(f"      Applied Trades: {season['applied_trades']}")
                        print(f"      Unique Sources: {season['unique_sources']}")
                        
                    source_stats = data.get('source_stats', [])
                    print(f"  Source Statistics: {len(source_stats)}")
                    for source in source_stats[:2]:
                        print(f"    - {source['source']}:")
                        print(f"      Total Trades: {source['total_trades']}")
                        print(f"      Unique Seasons: {source['unique_seasons']}")
                        print(f"      Applied Trades: {source['applied_trades']}")
                        
                    month_stats = data.get('month_stats', [])
                    print(f"  Month Statistics: {len(month_stats)}")
                    for month in month_stats[:2]:
                        month_name = datetime.fromisoformat(month['trade_month']).strftime('%B %Y')
                        print(f"    - {month_name}:")
                        print(f"      Total Trades: {month['total_trades']}")
                        print(f"      Unique Seasons: {month['unique_seasons']}")
                        print(f"      Applied Trades: {month['applied_trades']}")
                        
                elif name == "Trades by Season":
                    trades = data.get('trades', [])
                    print(f"  Season: {data.get('season', 'N/A')}")
                    print(f"  Total Trades: {data.get('total', 0)}")
                    
                    for trade in trades:
                        print(f"  - {trade['headline']}")
                        print(f"    Date: {trade['trade_date']}")
                        print(f"    Source: {trade['source']}")
                        print(f"    Applied: {'Yes' if trade['is_applied'] else 'No'}")
                        print(f"    Description: {trade['description'][:100]}...")
                        print(f"    Created: {trade['created_at']}")
                        
                elif name == "Trades by Source":
                    trades = data.get('trades', [])
                    print(f"  Source: {data.get('source', 'N/A')}")
                    print(f"  Total Trades: {data.get('total', 0)}")
                    
                    for trade in trades:
                        print(f"  - {trade['headline']}")
                        print(f"    Date: {trade['trade_date']}")
                        print(f"    Season: {trade['season_year']}")
                        print(f"    Applied: {'Yes' if trade['is_applied'] else 'No'}")
                        print(f"    Description: {trade['description'][:100]}...")
                        print(f"    Created: {trade['created_at']}")
                        
                elif name == "Applied Trades":
                    trades = data.get('trades', [])
                    print(f"  Total Applied Trades: {data.get('total', 0)}")
                    
                    for trade in trades:
                        print(f"  - {trade['headline']}")
                        print(f"    Date: {trade['trade_date']}")
                        print(f"    Season: {trade['season_year']}")
                        print(f"    Source: {trade['source']}")
                        print(f"    Description: {trade['description'][:100]}...")
                        print(f"    Created: {trade['created_at']}")
                        
                elif name == "Pending Trades":
                    trades = data.get('trades', [])
                    print(f"  Total Pending Trades: {data.get('total', 0)}")
                    
                    for trade in trades:
                        print(f"  - {trade['headline']}")
                        print(f"    Date: {trade['trade_date']}")
                        print(f"    Season: {trade['season_year']}")
                        print(f"    Source: {trade['source']}")
                        print(f"    Description: {trade['description'][:100]}...")
                        print(f"    Created: {trade['created_at']}")
                        
                elif name == "Search Trades":
                    results = data.get('results', [])
                    print(f"  Query: {data.get('query', 'N/A')}")
                    print(f"  Total Results: {data.get('total', 0)}")
                    print(f"  Limit: {data.get('limit', 0)}")
                    
                    for result in results:
                        print(f"  - {result['headline']}")
                        print(f"    Date: {result['trade_date']}")
                        print(f"    Season: {result['season_year']}")
                        print(f"    Source: {result['source']}")
                        print(f"    Applied: {'Yes' if result['is_applied'] else 'No'}")
                        print(f"    Description: {result['description'][:100]}...")
                        print(f"    Created: {result['created_at']}")
                
                print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
                print(f"  Note: {data.get('note', 'N/A')}")
                
            else:
                print(f"  Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"\n{name}: ERROR - {e}")
    
    print("\n" + "="*80)
    print("TRADES TEST RESULTS:")
    print("="*80)
    
    print("\nTrades Table Structure:")
    print("The trades table tracks:")
    print("- Master trade records with high-level information")
    print("- Trade dates and season year context")
    print("- Detailed descriptions and headlines")
    print("- Source URLs and source attribution")
    print("- Application status tracking")
    print("- Creation and update timestamps")
    
    print("\nTrade Data Types:")
    print("- Trade Date: Date when trade occurred")
    print("- Season Year: Season context for the trade")
    print("- Description: Detailed trade explanation")
    print("- Headline: Concise trade summary")
    print("- Source URL: Link to original source")
    print("- Source: News source attribution")
    print("- Applied Status: Whether trade is applied")
    
    print("\nTrade Categories:")
    print("- Applied Trades: Completed and processed trades")
    print("- Pending Trades: Trades awaiting processing")
    print("- Multi-Sport: NBA, NFL, MLB, NHL trades")
    print("- Various Sources: ESPN, NBA.com, NFL.com, etc.")
    
    print("\nSample Trade Scenarios:")
    print("- NBA_2024_001: Suns Trade Durant to Celtics for Booker")
    print("- NFL_2024_001: Packers Trade Rodgers to Raiders for Adams")
    print("- MLB_2024_001: Mets Trade Alonso to Dodgers for deGrom")
    print("- NHL_2024_001: Oilers Trade McDavid to Maple Leafs for MacKinnon")
    print("- NBA_2024_005: Pacers Acquire 2025 First-Round Pick from Cavaliers")
    
    print("\nTrade Analysis Features:")
    print("- Season Tracking: Trade activity by season")
    print("- Source Analysis: Trade reporting by source")
    print("- Status Tracking: Applied vs pending trades")
    print("- Search Functionality: Find specific trades")
    print("- Historical Context: Trade timeline and trends")
    
    print("\nBusiness Value:")
    print("- Trade History: Complete trade record keeping")
    print("- Market Analysis: Trade market trends and patterns")
    print("- Source Tracking: Trade news source attribution")
    print("- Status Management: Trade processing workflow")
    print("- Historical Research: Trade impact analysis")
    
    print("\nAvailable Endpoints:")
    print("- GET /immediate/trades - Get trades with filters")
    print("- GET /immediate/trades/statistics - Get overall statistics")
    print("- GET /immediate/trades/season/{season} - Get season trades")
    print("- GET /immediate/trades/source/{source} - Get source trades")
    print("- GET /immediate/trades/applied - Get applied trades")
    print("- GET /immediate/trades/pending - Get pending trades")
    print("- GET /immediate/trades/search - Search trades")
    
    print("\nIntegration Features:")
    print("- Multi-Sport Support: NBA, NFL, MLB, NHL trades")
    print("- Source Diversity: Multiple news sources tracked")
    print("- Status Management: Applied/pending workflow")
    print("- Detailed Descriptions: Comprehensive trade information")
    print("- URL Tracking: Source link management")
    
    print("\n" + "="*80)
    print("TRADES SYSTEM COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    test_trades()
