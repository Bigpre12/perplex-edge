#!/usr/bin/env python3
"""
MARKETS ANALYSIS - Comprehensive analysis of the markets table and betting market types
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import json

async def analyze_markets():
    """Analyze the markets table structure and data"""
    
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
    
    try:
        conn = await asyncpg.connect(db_url)
        print("Connected to database")
        
        # Get all markets data
        markets = await conn.fetch("""
            SELECT * FROM markets 
            ORDER BY sport_id, market_type, stat_type
        """)
        
        print("MARKETS TABLE ANALYSIS")
        print("="*80)
        
        print(f"\nTotal Markets: {len(markets)}")
        
        # Group by sport
        sports = {}
        for market in markets:
            sport_id = market['sport_id']
            if sport_id not in sports:
                sports[sport_id] = []
            sports[sport_id].append(market)
        
        print(f"\nMarkets by Sport:")
        for sport_id, sport_markets in sports.items():
            print(f"  Sport ID {sport_id}: {len(sport_markets)} markets")
        
        # Analyze market types
        market_types = {}
        for market in markets:
            market_type = market['market_type']
            if market_type not in market_types:
                market_types[market_type] = []
            market_types[market_type].append(market)
        
        print(f"\nMarket Types:")
        for market_type, type_markets in market_types.items():
            print(f"  {market_type}: {len(type_markets)} markets")
        
        # Detailed breakdown by sport
        print(f"\nDETAILED MARKET BREAKDOWN:")
        print("="*80)
        
        sport_mapping = {
            1: "NFL",
            30: "NBA", 
            29: "MLB",
            32: "NCAA Basketball",
            41: "College Football",
            53: "NHL"
        }
        
        for sport_id, sport_markets in sports.items():
            sport_name = sport_mapping.get(sport_id, f"Sport {sport_id}")
            print(f"\n{sport_name} (Sport ID: {sport_id}):")
            print("-" * 40)
            
            # Group by market type within sport
            sport_market_types = {}
            for market in sport_markets:
                market_type = market['market_type']
                if market_type not in sport_market_types:
                    sport_market_types[market_type] = []
                sport_market_types[market_type].append(market)
            
            for market_type, type_markets in sport_market_types.items():
                print(f"\n  {market_type.upper()} Markets:")
                for market in type_markets:
                    stat_display = market['stat_type'] if market['stat_type'] else "N/A"
                    print(f"    - ID: {market['id']}")
                    print(f"      Stat Type: {stat_display}")
                    print(f"      Description: {market['description']}")
                    print(f"      Created: {market['created_at']}")
        
        # Market type analysis
        print(f"\nMARKET TYPE ANALYSIS:")
        print("="*80)
        
        market_type_descriptions = {
            "moneyline": "Straight win/loss betting on teams or players",
            "spread": "Point spread betting with handicap",
            "total": "Over/under betting on total points/goals",
            "player_prop": "Individual player performance betting",
            "team_prop": "Team-specific performance betting",
            "game_prop": "Game-specific event betting",
            "future": "Long-term outcome betting",
            "parlay": "Combined bet multiple selections"
        }
        
        for market_type, type_markets in market_types.items():
            description = market_type_descriptions.get(market_type, "Unknown market type")
            print(f"\n{market_type.upper()}:")
            print(f"  Description: {description}")
            print(f"  Total Markets: {len(type_markets)}")
            print(f"  Sports: {len(set(m['sport_id'] for m in type_markets))}")
            
            # Show unique stat types for this market type
            stat_types = list(set(m['stat_type'] for m in type_markets if m['stat_type']))
            if stat_types:
                print(f"  Stat Types: {', '.join(stat_types)}")
        
        # Stat type analysis
        print(f"\nSTAT TYPE ANALYSIS:")
        print("="*80)
        
        stat_types = {}
        for market in markets:
            if market['stat_type']:  # Skip NULL stat_types
                stat_type = market['stat_type']
                if stat_type not in stat_types:
                    stat_types[stat_type] = []
                stat_types[stat_type].append(market)
        
        print(f"\nUnique Stat Types: {len(stat_types)}")
        
        # Group stat types by category
        stat_categories = {
            "Passing": ["PASS_YDS", "PASS_TDS", "PASS_ATT", "PASS_CMP", "PASS_INT"],
            "Rushing": ["RUSH_YDS", "RUSH_TDS", "RUSH_ATT"],
            "Receiving": ["REC_YDS", "REC_TDS", "REC", "REC_YAC"],
            "Scoring": ["PTS", "TD", "FG", "XP"],
            "Basketball Offense": ["PTS", "AST", "REB", "BLK", "STL"],
            "Baseball Hitting": ["H", "HR", "RBI", "SB", "AVG"],
            "Baseball Pitching": ["K", "ERA", "WHIP", "W", "SV"],
            "Hockey": ["G", "A", "PTS", "SOG", "PIM"]
        }
        
        for category, stats in stat_categories.items():
            found_stats = [stat for stat in stats if stat in stat_types]
            if found_stats:
                print(f"\n{category}:")
                for stat in found_stats:
                    count = len(stat_types[stat])
                    sports = list(set(m['sport_id'] for m in stat_types[stat]))
                    print(f"  {stat}: {count} markets across sports {sports}")
        
        # Individual stat types not in categories
        uncategorized = [stat for stat in stat_types.keys() if not any(stat in stats for stats in stat_categories.values())]
        if uncategorized:
            print(f"\nUncategorized Stat Types:")
            for stat in uncategorized:
                count = len(stat_types[stat])
                sports = list(set(m['sport_id'] for m in stat_types[stat]))
                print(f"  {stat}: {count} markets across sports {sports}")
        
        # Market completeness analysis
        print(f"\nMARKET COMPLETENESS ANALYSIS:")
        print("="*80)
        
        # Check which sports have which market types
        sport_market_matrix = {}
        for sport_id, sport_markets in sports.items():
            sport_name = sport_mapping.get(sport_id, f"Sport {sport_id}")
            available_market_types = set(m['market_type'] for m in sport_markets)
            sport_market_matrix[sport_name] = available_market_types
        
        print(f"\nMarket Type Coverage by Sport:")
        all_market_types = set(market_types.keys())
        
        for sport_name, available_types in sport_market_matrix.items():
            print(f"\n{sport_name}:")
            for market_type in all_market_types:
                status = "✓" if market_type in available_types else "✗"
                print(f"  {status} {market_type}")
        
        # Missing market types by sport
        print(f"\nMISSING MARKET OPPORTUNITIES:")
        print("="*80)
        
        for sport_name, available_types in sport_market_matrix.items():
            missing = all_market_types - available_types
            if missing:
                print(f"\n{sport_name} missing:")
                for market_type in sorted(missing):
                    print(f"  - {market_type}")
        
        # Market creation timeline
        print(f"\nMARKET CREATION TIMELINE:")
        print("="*80)
        
        markets_by_date = {}
        for market in markets:
            date = market['created_at'].date()
            if date not in markets_by_date:
                markets_by_date[date] = []
            markets_by_date[date].append(market)
        
        for date in sorted(markets_by_date.keys()):
            day_markets = markets_by_date[date]
            print(f"\n{date}: {len(day_markets)} markets added")
            
            # Group by sport for that day
            sports_added = {}
            for market in day_markets:
                sport_name = sport_mapping.get(market['sport_id'], f"Sport {market['sport_id']}")
                if sport_name not in sports_added:
                    sports_added[sport_name] = []
                sports_added[sport_name].append(market)
            
            for sport_name, sport_markets in sports_added.items():
                market_types_added = set(m['market_type'] for m in sport_markets)
                print(f"  {sport_name}: {', '.join(sorted(market_types_added))}")
        
        # Summary statistics
        print(f"\nSUMMARY STATISTICS:")
        print("="*80)
        
        print(f"Total Markets: {len(markets)}")
        print(f"Total Sports: {len(sports)}")
        print(f"Total Market Types: {len(market_types)}")
        print(f"Total Stat Types: {len(stat_types)}")
        
        # Most common market types
        print(f"\nMost Common Market Types:")
        sorted_market_types = sorted(market_types.items(), key=lambda x: len(x[1]), reverse=True)
        for market_type, type_markets in sorted_market_types[:5]:
            print(f"  {market_type}: {len(type_markets)} markets")
        
        # Most common stat types
        print(f"\nMost Common Stat Types:")
        sorted_stat_types = sorted(stat_types.items(), key=lambda x: len(x[1]), reverse=True)
        for stat_type, stat_markets in sorted_stat_types[:10]:
            sports_covered = len(set(m['sport_id'] for m in stat_markets))
            print(f"  {stat_type}: {len(stat_markets)} markets across {sports_covered} sports")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_markets())
