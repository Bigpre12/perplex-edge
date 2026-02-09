#!/usr/bin/env python3
"""
PLAYER MARKET HIT RATES ANALYSIS - Comprehensive analysis of the player_market_hit_rates table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import json

async def analyze_player_market_hit_rates():
    """Analyze the player_market_hit_rates table structure and data"""
    
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
    
    try:
        conn = await asyncpg.connect(self.db_url)
        print("Connected to database")
        
        # Get all player market hit rates data
        market_hit_rates = await conn.fetch("""
            SELECT * FROM player_market_hit_rates 
            ORDER BY hit_rate_all DESC, hit_rate_7d DESC
            LIMIT 100
        """)
        
        print("PLAYER MARKET HIT RATES TABLE ANALYSIS")
        print("="*80)
        
        print(f"\nTotal Player Market Hit Rates: {len(market_hit_rates)}")
        
        # Overall statistics
        overall = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_markets,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT sport_id) as unique_sports,
                COUNT(DISTINCT market) as unique_markets,
                COUNT(DISTINCT side) as unique_sides,
                AVG(hit_rate_7d) as avg_hit_rate_7d,
                AVG(hit_rate_all) as avg_hit_rate_all,
                AVG(current_streak) as avg_current_streak,
                AVG(best_streak) as avg_best_streak,
                AVG(worst_streak) as avg_worst_streak,
                COUNT(CASE WHEN hit_rate_7d >= 0.7 THEN 1 END) as hot_markets_7d,
                COUNT(CASE WHEN hit_rate_all >= 0.6 THEN 1 END) as solid_markets_all,
                COUNT(CASE WHEN current_streak >= 3 THEN 1 END) as on_fire_markets,
                COUNT(CASE WHEN current_streak <= -3 THEN 1 END) as cold_markets
            FROM player_market_hit_rates
        """)
        
        print(f"\nOverall Market Hit Rate Statistics:")
        print(f"  Total Markets: {overall['total_markets']}")
        print(f"  Unique Players: {overall['unique_players']}")
        print(f"  Unique Sports: {overall['unique_sports']}")
        print(f"  Unique Markets: {overall['unique_markets']}")
        print(f"  Unique Sides: {overall['unique_sides']}")
        print(f"  Avg 7-Day Hit Rate: {overall['avg_hit_rate_7d']:.4f}")
        print(f"  Avg All-Time Hit Rate: {overall['avg_hit_rate_all']:.4f}")
        print(f"  Avg Current Streak: {overall['avg_current_streak']:.1f}")
        print(f"  Avg Best Streak: {overall['avg_best_streak']:.1f}")
        print(f"  Avg Worst Streak: {overall['avg_worst_streak']:.1f}")
        print(f"  Hot Markets (7D >= 70%): {overall['hot_markets_7d']}")
        print(f"  Solid Markets (All >= 60%): {overall['solid_markets_all']}")
        print(f"  On Fire Markets (Streak >= 3): {overall['on_fire_markets']}")
        print(f"  Cold Markets (Streak <= -3): {overall['cold_markets']}")
        
        # Top performing markets
        top_markets = await conn.fetch("""
            SELECT 
                player_id,
                sport_id,
                market,
                side,
                hit_rate_7d,
                hit_rate_all,
                current_streak,
                best_streak,
                worst_streak,
                last_5_results,
                last_pick_at,
                updated_at
            FROM player_market_hit_rates
            WHERE total_all > 0
            ORDER BY hit_rate_all DESC, hit_rate_7d DESC
            LIMIT 10
        """)
        
        print(f"\nTop 10 Performing Markets:")
        for market in top_markets:
            print(f"  Player {market['player_id']} - {market['market'].upper()} {market['side'].upper()} (Sport {market['sport_id']}):")
            print(f"    7-Day Hit Rate: {market['hit_rate_7d']:.4f}")
            print(f"    All-Time Hit Rate: {market['hit_rate_all']:.4f}")
            print(f"    Current Streak: {market['current_streak']}")
            print(f"    Best/Worst Streak: {market['best_streak']}/{market['worst_streak']}")
            print(f"    Last 5: {market['last_5_results']}")
            print(f"    Last Pick: {market['last_pick_at']}")
        
        # Market type analysis
        market_analysis = await conn.fetch("""
            SELECT 
                market,
                side,
                COUNT(*) as total_markets,
                COUNT(DISTINCT player_id) as unique_players,
                AVG(hit_rate_7d) as avg_hit_rate_7d,
                AVG(hit_rate_all) as avg_hit_rate_all,
                AVG(current_streak) as avg_current_streak,
                AVG(best_streak) as avg_best_streak,
                COUNT(CASE WHEN hit_rate_7d >= 0.7 THEN 1 END) as hot_markets_7d,
                COUNT(CASE WHEN current_streak >= 3 THEN 1 END) as on_fire_markets,
                COUNT(CASE WHEN current_streak <= -3 THEN 1 END) as cold_markets
            FROM player_market_hit_rates
            WHERE total_all > 0
            GROUP BY market, side
            ORDER BY avg_hit_rate_all DESC
        """)
        
        print(f"\nMarket Type Performance:")
        for market in market_analysis:
            print(f"  {market['market'].upper()} {market['side'].upper()}:")
            print(f"    Total Markets: {market['total_markets']}")
            print(f"    Unique Players: {market['unique_players']}")
            print(f"    Avg 7-Day Hit Rate: {market['avg_hit_rate_7d']:.4f}")
            print(f"    Avg All-Time Hit Rate: {market['avg_hit_rate_all']:.4f}")
            print(f"    Avg Current Streak: {market['avg_current_streak']:.1f}")
            print(f"    Hot Markets: {market['hot_markets_7d']}")
            print(f"    On Fire Markets: {market['on_fire_markets']}")
            print(f"    Cold Markets: {market['cold_markets']}")
        
        # Side analysis (over/under)
        side_analysis = await conn.fetch("""
            SELECT 
                side,
                COUNT(*) as total_markets,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT market) as unique_market_types,
                AVG(hit_rate_7d) as avg_hit_rate_7d,
                AVG(hit_rate_all) as avg_hit_rate_all,
                AVG(current_streak) as avg_current_streak,
                AVG(best_streak) as avg_best_streak,
                COUNT(CASE WHEN hit_rate_7d >= 0.7 THEN 1 END) as hot_markets_7d,
                COUNT(CASE WHEN current_streak >= 3 THEN 1 END) as on_fire_markets,
                COUNT(CASE WHEN current_streak <= -3 THEN 1 END) as cold_markets
            FROM player_market_hit_rates
            WHERE total_all > 0
            GROUP BY side
            ORDER BY avg_hit_rate_all DESC
        """)
        
        print(f"\nSide Performance (Over/Under):")
        for side in side_analysis:
            print(f"  {side.upper()}:")
            print(f"    Total Markets: {side['total_markets']}")
            print(f"    Unique Players: {side['unique_players']}")
            print(f"    Market Types: {side['unique_market_types']}")
            print(f"    Avg 7-Day Hit Rate: {side['avg_hit_rate_7d']:.4f}")
            print(f"    Avg All-Time Hit Rate: {side['avg_hit_rate_all']:.4f}")
            print(f"    Avg Current Streak: {side['avg_current_streak']:.1f}")
            print(f"    Hot Markets: {side['hot_markets_7d']}")
            print(f"    On Fire Markets: {side['on_fire_markets']}")
            print(f"    Cold Markets: {side['cold_markets']}")
        
        # Player market specialization
        player_specialization = await conn.fetch("""
            SELECT 
                player_id,
                COUNT(*) as total_markets,
                COUNT(DISTINCT market) as unique_markets,
                COUNT(DISTINCT side) as unique_sides,
                AVG(hit_rate_7d) as avg_hit_rate_7d,
                AVG(hit_rate_all) as avg_hit_rate_all,
                AVG(current_streak) as avg_current_streak,
                AVG(best_streak) as avg_best_streak,
                MAX(hit_rate_all) as best_market_hit_rate,
                COUNT(CASE WHEN hit_rate_all >= 0.7 THEN 1 END) as elite_markets
            FROM player_market_hit_rates
            WHERE total_all > 0
            GROUP BY player_id
            HAVING COUNT(*) >= 2
            ORDER BY avg_hit_rate_all DESC
            LIMIT 10
        """)
        
        print(f"\nPlayer Market Specialization (2+ Markets):")
        for player in player_specialization:
            print(f"  Player {player['player_id']}:")
            print(f"    Total Markets: {player['total_markets']}")
            print(f"    Market Types: {player['unique_markets']}, Sides: {player['unique_sides']}")
            print(f"    Avg Hit Rate (7D/All): {player['avg_hit_rate_7d']:.4f}/{player['avg_hit_rate_all']:.4f}")
            print(f"    Current Streak: {player['avg_current_streak']:.1f}")
            print(f"    Best Market Hit Rate: {player['best_market_hit_rate']:.4f}")
            print(f"    Elite Markets (70%+): {player['elite_markets']}")
        
        # Streak analysis by market
        streak_by_market = await conn.fetch("""
            SELECT 
                market,
                side,
                CASE 
                    WHEN current_streak >= 5 THEN 'On Fire (5+)'
                    WHEN current_streak >= 3 THEN 'Hot Streak (3-4)'
                    WHEN current_streak >= 1 THEN 'Warm (1-2)'
                    WHEN current_streak = 0 THEN 'Neutral (0)'
                    WHEN current_streak >= -2 THEN 'Cool (-1 to -2)'
                    ELSE 'Cold Streak (-3 or worse)'
                END as streak_category,
                COUNT(*) as total_markets,
                AVG(hit_rate_7d) as avg_hit_rate_7d,
                AVG(hit_rate_all) as avg_hit_rate_all,
                AVG(best_streak) as avg_best_streak,
                AVG(worst_streak) as avg_worst_streak
            FROM player_market_hit_rates
            WHERE total_all > 0
            GROUP BY market, side, streak_category
            ORDER BY avg_hit_rate_all DESC
        """)
        
        print(f"\nStreak Analysis by Market Type:")
        for streak in streak_by_market:
            print(f"  {streak['market'].upper()} {streak['side'].upper()} - {streak['streak_category']}:")
            print(f"    Total Markets: {streak['total_markets']}")
            print(f"    Avg 7-Day Hit Rate: {streak['avg_hit_rate_7d']:.4f}")
            print(f"    Avg All-Time Hit Rate: {streak['avg_hit_rate_all']:.4f}")
            print(f"    Best/Worst Streak: {streak['avg_best_streak']:.1f}/{streak['avg_worst_streak']:.1f}")
        
        # Recent activity
        recent = await conn.fetch("""
            SELECT * FROM player_market_hit_rates 
            ORDER BY last_pick_at DESC, updated_at DESC 
            LIMIT 10
        """)
        
        print(f"\nMost Recent Market Activity:")
        for market in recent:
            print(f"  - Player {market['player_id']} - {market['market'].upper()} {market['side'].upper()} (Sport {market['sport_id']}):")
            print(f"    7-Day: {market['hits_7d']}/{market['total_7d']} ({market['hit_rate_7d']:.4f})")
            print(f"    All-Time: {market['hits_all']}/{market['total_all']} ({market['hit_rate_all']:.4f})")
            print(f"    Current Streak: {market['current_streak']}")
            print(f"    Last 5: {market['last_5_results']}")
            print(f"    Last Pick: {market['last_pick_at']}")
        
        # Zero activity markets (new/untracked)
        zero_activity = await conn.fetch("""
            SELECT 
                player_id,
                sport_id,
                market,
                side,
                last_pick_at,
                updated_at
            FROM player_market_hit_rates
            WHERE total_all = 0
            ORDER BY updated_at DESC
            LIMIT 10
        """)
        
        print(f"\nMarkets with Zero Activity:")
        for market in zero_activity:
            print(f"  - Player {market['player_id']} - {market['market'].upper()} {market['side'].upper()} (Sport {market['sport_id']}):")
            print(f"    No picks recorded yet")
            print(f"    Last Updated: {market['updated_at']}")
        
        # Hit rate distribution by market type
        hit_rate_dist = await conn.fetch("""
            SELECT 
                market,
                side,
                CASE 
                    WHEN hit_rate_all >= 0.8 THEN 'Elite (80%+)'
                    WHEN hit_rate_all >= 0.7 THEN 'Excellent (70-79%)'
                    WHEN hit_rate_all >= 0.6 THEN 'Good (60-69%)'
                    WHEN hit_rate_all >= 0.5 THEN 'Average (50-59%)'
                    WHEN hit_rate_all >= 0.4 THEN 'Below Average (40-49%)'
                    ELSE 'Poor (<40%)'
                END as hit_rate_category,
                COUNT(*) as total_markets,
                AVG(hit_rate_7d) as avg_hit_rate_7d,
                AVG(current_streak) as avg_current_streak,
                AVG(best_streak) as avg_best_streak
            FROM player_market_hit_rates
            WHERE total_all > 0
            GROUP BY market, side, hit_rate_category
            ORDER BY hit_rate_all DESC
        """)
        
        print(f"\nHit Rate Distribution by Market Type:")
        for rate in hit_rate_dist:
            print(f"  {rate['market'].upper()} {rate['side'].upper()} - {rate['hit_rate_category']}:")
            print(f"    Total Markets: {rate['total_markets']}")
            print(f"    Avg 7-Day Hit Rate: {rate['avg_hit_rate_7d']:.4f}")
            print(f"    Avg Current Streak: {rate['avg_current_streak']:.1f}")
            print(f"    Avg Best Streak: {rate['avg_best_streak']:.1f}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_player_market_hit_rates())
