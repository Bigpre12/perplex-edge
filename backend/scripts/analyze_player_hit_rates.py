#!/usr/bin/env python3
"""
PLAYER HIT RATES ANALYSIS - Comprehensive analysis of the player_hit_rates table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import json

async def analyze_player_hit_rates():
    """Analyze the player_hit_rates table structure and data"""
    
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
    
    try:
        conn = await asyncpg.connect(db_url)
        print("Connected to database")
        
        # Get all player hit rates data
        hit_rates = await conn.fetch("""
            SELECT * FROM player_hit_rates 
            ORDER BY hit_rate_all DESC, hit_rate_7d DESC
            LIMIT 100
        """)
        
        print("PLAYER HIT RATES TABLE ANALYSIS")
        print("="*80)
        
        print(f"\nTotal Player Hit Rates: {len(hit_rates)}")
        
        # Overall statistics
        overall = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_players,
                COUNT(DISTINCT sport_id) as unique_sports,
                AVG(hit_rate_7d) as avg_hit_rate_7d,
                AVG(hit_rate_all) as avg_hit_rate_all,
                AVG(current_streak) as avg_current_streak,
                AVG(best_streak) as avg_best_streak,
                AVG(worst_streak) as avg_worst_streak,
                COUNT(CASE WHEN hit_rate_7d >= 0.8 THEN 1 END) as hot_players_7d,
                COUNT(CASE WHEN hit_rate_all >= 0.6 THEN 1 END) as solid_players_all,
                COUNT(CASE WHEN current_streak >= 5 THEN 1 END) as on_fire_players,
                COUNT(CASE WHEN current_streak <= -3 THEN 1 END) as cold_players
            FROM player_hit_rates
        """)
        
        print(f"\nOverall Hit Rate Statistics:")
        print(f"  Total Players: {overall['total_players']}")
        print(f"  Unique Sports: {overall['unique_sports']}")
        print(f"  Avg 7-Day Hit Rate: {overall['avg_hit_rate_7d']:.4f}")
        print(f"  Avg All-Time Hit Rate: {overall['avg_hit_rate_all']:.4f}")
        print(f"  Avg Current Streak: {overall['avg_current_streak']:.1f}")
        print(f"  Avg Best Streak: {overall['avg_best_streak']:.1f}")
        print(f"  Avg Worst Streak: {overall['avg_worst_streak']:.1f}")
        print(f"  Hot Players (7D >= 80%): {overall['hot_players_7d']}")
        print(f"  Solid Players (All >= 60%): {overall['solid_players_all']}")
        print(f"  On Fire Players (Streak >= 5): {overall['on_fire_players']}")
        print(f"  Cold Players (Streak <= -3): {overall['cold_players']}")
        
        # Top performers by hit rate
        top_performers = await conn.fetch("""
            SELECT 
                player_id,
                sport_id,
                hit_rate_7d,
                hit_rate_all,
                current_streak,
                best_streak,
                worst_streak,
                last_5_results,
                last_pick_at,
                updated_at
            FROM player_hit_rates
            ORDER BY hit_rate_all DESC, hit_rate_7d DESC
            LIMIT 10
        """)
        
        print(f"\nTop 10 Players by Hit Rate:")
        for player in top_performers:
            print(f"  Player {player['player_id']} (Sport {player['sport_id']}):")
            print(f"    7-Day Hit Rate: {player['hit_rate_7d']:.4f}")
            print(f"    All-Time Hit Rate: {player['hit_rate_all']:.4f}")
            print(f"    Current Streak: {player['current_streak']}")
            print(f"    Best/Worst Streak: {player['best_streak']}/{player['worst_streak']}")
            print(f"    Last 5: {player['last_5_results']}")
            print(f"    Last Pick: {player['last_pick_at']}")
        
        # Hottest players (current streak)
        hottest_players = await conn.fetch("""
            SELECT 
                player_id,
                sport_id,
                hit_rate_7d,
                hit_rate_all,
                current_streak,
                best_streak,
                worst_streak,
                last_5_results,
                last_pick_at
            FROM player_hit_rates
            WHERE current_streak >= 5
            ORDER BY current_streak DESC
            LIMIT 10
        """)
        
        print(f"\nHottest Players (Current Streak >= 5):")
        for player in hottest_players:
            print(f"  Player {player['player_id']} (Sport {player['sport_id']}):")
            print(f"    Current Streak: {player['current_streak']}")
            print(f"    7-Day Hit Rate: {player['hit_rate_7d']:.4f}")
            print(f"    All-Time Hit Rate: {player['hit_rate_all']:.4f}")
            print(f"    Best Streak: {player['best_streak']}")
            print(f"    Last 5: {player['last_5_results']}")
        
        # Coldest players (negative streak)
        coldest_players = await conn.fetch("""
            SELECT 
                player_id,
                sport_id,
                hit_rate_7d,
                hit_rate_all,
                current_streak,
                best_streak,
                worst_streak,
                last_5_results,
                last_pick_at
            FROM player_hit_rates
            WHERE current_streak <= -3
            ORDER BY current_streak ASC
            LIMIT 10
        """)
        
        print(f"\nColdest Players (Current Streak <= -3):")
        for player in coldest_players:
            print(f"  Player {player['player_id']} (Sport {player['sport_id']}):")
            print(f"    Current Streak: {player['current_streak']}")
            print(f"    7-Day Hit Rate: {player['hit_rate_7d']:.4f}")
            print(f"    All-Time Hit Rate: {player['hit_rate_all']:.4f}")
            print(f"    Worst Streak: {player['worst_streak']}")
            print(f"    Last 5: {player['last_5_results']}")
        
        # By sport analysis
        by_sport = await conn.fetch("""
            SELECT 
                sport_id,
                COUNT(*) as total_players,
                AVG(hit_rate_7d) as avg_hit_rate_7d,
                AVG(hit_rate_all) as avg_hit_rate_all,
                AVG(current_streak) as avg_current_streak,
                AVG(best_streak) as avg_best_streak,
                COUNT(CASE WHEN hit_rate_7d >= 0.8 THEN 1 END) as hot_players_7d,
                COUNT(CASE WHEN current_streak >= 5 THEN 1 END) as on_fire_players,
                COUNT(CASE WHEN current_streak <= -3 THEN 1 END) as cold_players
            FROM player_hit_rates
            GROUP BY sport_id
            ORDER BY avg_hit_rate_all DESC
        """)
        
        print(f"\nHit Rate Analysis by Sport:")
        for sport in by_sport:
            print(f"  Sport {sport['sport_id']}:")
            print(f"    Total Players: {sport['total_players']}")
            print(f"    Avg 7-Day Hit Rate: {sport['avg_hit_rate_7d']:.4f}")
            print(f"    Avg All-Time Hit Rate: {sport['avg_hit_rate_all']:.4f}")
            print(f"    Avg Current Streak: {sport['avg_current_streak']:.1f}")
            print(f"    Hot Players (7D): {sport['hot_players_7d']}")
            print(f"    On Fire Players: {sport['on_fire_players']}")
            print(f"    Cold Players: {sport['cold_players']}")
        
        # Streak analysis
        streak_analysis = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN current_streak >= 10 THEN 'On Fire (10+)'
                    WHEN current_streak >= 5 THEN 'Hot Streak (5-9)'
                    WHEN current_streak >= 1 THEN 'Warm (1-4)'
                    WHEN current_streak = 0 THEN 'Neutral (0)'
                    WHEN current_streak >= -3 THEN 'Cool (-1 to -3)'
                    ELSE 'Cold Streak (-4 or worse)'
                END as streak_category,
                COUNT(*) as total_players,
                AVG(hit_rate_7d) as avg_hit_rate_7d,
                AVG(hit_rate_all) as avg_hit_rate_all,
                AVG(best_streak) as avg_best_streak,
                AVG(worst_streak) as avg_worst_streak
            FROM player_hit_rates
            GROUP BY streak_category
            ORDER BY avg_current_streak DESC
        """)
        
        print(f"\nStreak Category Analysis:")
        for streak in streak_analysis:
            print(f"  {streak['streak_category']}:")
            print(f"    Total Players: {streak['total_players']}")
            print(f"    Avg 7-Day Hit Rate: {streak['avg_hit_rate_7d']:.4f}")
            print(f"    Avg All-Time Hit Rate: {streak['avg_hit_rate_all']:.4f}")
            print(f"    Avg Best Streak: {streak['avg_best_streak']:.1f}")
            print(f"    Avg Worst Streak: {streak['avg_worst_streak']:.1f}")
        
        # Hit rate distribution
        hit_rate_dist = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN hit_rate_all >= 0.8 THEN 'Elite (80%+)'
                    WHEN hit_rate_all >= 0.7 THEN 'Excellent (70-79%)'
                    WHEN hit_rate_all >= 0.6 THEN 'Good (60-69%)'
                    WHEN hit_rate_all >= 0.5 THEN 'Average (50-59%)'
                    WHEN hit_rate_all >= 0.4 THEN 'Below Average (40-49%)'
                    ELSE 'Poor (<40%)'
                END as hit_rate_category,
                COUNT(*) as total_players,
                AVG(hit_rate_7d) as avg_hit_rate_7d,
                AVG(current_streak) as avg_current_streak,
                AVG(best_streak) as avg_best_streak
            FROM player_hit_rates
            GROUP BY hit_rate_category
            ORDER BY avg_hit_rate_all DESC
        """)
        
        print(f"\nHit Rate Distribution:")
        for rate in hit_rate_dist:
            print(f"  {rate['hit_rate_category']}:")
            print(f"    Total Players: {rate['total_players']}")
            print(f"    Avg 7-Day Hit Rate: {rate['avg_hit_rate_7d']:.4f}")
            print(f"    Avg Current Streak: {rate['avg_current_streak']:.1f}")
            print(f"    Avg Best Streak: {rate['avg_best_streak']:.1f}")
        
        # Recent activity
        recent = await conn.fetch("""
            SELECT * FROM player_hit_rates 
            ORDER BY last_pick_at DESC, updated_at DESC 
            LIMIT 10
        """)
        
        print(f"\nMost Recent Player Activity:")
        for player in recent:
            print(f"  - Player {player['player_id']} (Sport {player['sport_id']}):")
            print(f"    7-Day: {player['hits_7d']}/{player['total_7d']} ({player['hit_rate_7d']:.4f})")
            print(f"    All-Time: {player['hits_all']}/{player['total_all']} ({player['hit_rate_all']:.4f})")
            print(f"    Current Streak: {player['current_streak']}")
            print(f"    Last 5: {player['last_5_results']}")
            print(f"    Last Pick: {player['last_pick_at']}")
        
        # Consistency analysis (low variance)
        consistent_players = await conn.fetch("""
            SELECT 
                player_id,
                sport_id,
                hit_rate_7d,
                hit_rate_all,
                current_streak,
                best_streak,
                worst_streak,
                ABS(best_streak - worst_streak) as streak_variance,
                last_5_results
            FROM player_hit_rates
            WHERE total_all >= 10
            ORDER BY streak_variance ASC
            LIMIT 10
        """)
        
        print(f"\nMost Consistent Players (Low Streak Variance):")
        for player in consistent_players:
            print(f"  Player {player['player_id']} (Sport {player['sport_id']}):")
            print(f"    Hit Rate (7D/All): {player['hit_rate_7d']:.4f}/{player['hit_rate_all']:.4f}")
            print(f"    Streak Variance: {player['streak_variance']}")
            print(f"    Best/Worst: {player['best_streak']}/{player['worst_streak']}")
            print(f"    Current Streak: {player['current_streak']}")
        
        # Volatile players (high variance)
        volatile_players = await conn.fetch("""
            SELECT 
                player_id,
                sport_id,
                hit_rate_7d,
                hit_rate_all,
                current_streak,
                best_streak,
                worst_streak,
                ABS(best_streak - worst_streak) as streak_variance,
                last_5_results
            FROM player_hit_rates
            WHERE total_all >= 10
            ORDER BY streak_variance DESC
            LIMIT 10
        """)
        
        print(f"\nMost Volatile Players (High Streak Variance):")
        for player in volatile_players:
            print(f"  Player {player['player_id']} (Sport {player['sport_id']}):")
            print(f"    Hit Rate (7D/All): {player['hit_rate_7d']:.4f}/{player['hit_rate_all']:.4f}")
            print(f"    Streak Variance: {player['streak_variance']}")
            print(f"    Best/Worst: {player['best_streak']}/{player['worst_streak']}")
            print(f"    Current Streak: {player['current_streak']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_player_hit_rates())
