#!/usr/bin/env python3
"""
PLAYER GAME STATS ANALYSIS - Comprehensive analysis of the player_game_stats table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import json

async def analyze_player_game_stats():
    """Analyze the player_game_stats table structure and data"""
    
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
    
    try:
        conn = await asyncpg.connect(db_url)
        print("Connected to database")
        
        # Get all player game stats data
        player_stats = await conn.fetch("""
            SELECT * FROM player_game_stats 
            ORDER BY created_at DESC, id DESC
            LIMIT 100
        """)
        
        print("PLAYER GAME STATS TABLE ANALYSIS")
        print("="*80)
        
        print(f"\nTotal Player Game Stats: {len(player_stats)}")
        
        # Analyze by player
        by_player = await conn.fetch("""
            SELECT 
                player_id,
                COUNT(*) as total_games,
                COUNT(DISTINCT game_id) as unique_games,
                COUNT(DISTINCT stat_type) as unique_stat_types,
                AVG(value) as avg_value,
                AVG(minutes) as avg_minutes,
                MIN(created_at) as first_game,
                MAX(created_at) as last_game
            FROM player_game_stats
            GROUP BY player_id
            ORDER BY total_games DESC
            LIMIT 10
        """)
        
        print(f"\nTop 10 Players by Game Count:")
        for player in by_player:
            print(f"  Player {player['player_id']}:")
            print(f"    Total Games: {player['total_games']}")
            print(f"    Unique Games: {player['unique_games']}")
            print(f"    Unique Stat Types: {player['unique_stat_types']}")
            print(f"    Avg Value: {player['avg_value']:.2f}")
            print(f"    Avg Minutes: {player['avg_minutes']:.1f}")
            print(f"    Period: {player['first_game']} to {player['last_game']}")
        
        # Analyze by stat type
        by_stat_type = await conn.fetch("""
            SELECT 
                stat_type,
                COUNT(*) as total_records,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT game_id) as unique_games,
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value,
                STDDEV(value) as stddev_value,
                AVG(minutes) as avg_minutes
            FROM player_game_stats
            GROUP BY stat_type
            ORDER BY total_records DESC
        """)
        
        print(f"\nStat Type Analysis:")
        for stat in by_stat_type:
            print(f"  {stat['stat_type']}:")
            print(f"    Total Records: {stat['total_records']}")
            print(f"    Unique Players: {stat['unique_players']}")
            print(f"    Unique Games: {stat['unique_games']}")
            print(f"    Avg Value: {stat['avg_value']:.2f}")
            print(f"    Min/Max: {stat['min_value']:.2f} / {stat['max_value']:.2f}")
            print(f"    Std Dev: {stat['stddev_value']:.2f}")
            print(f"    Avg Minutes: {stat['avg_minutes']:.1f}")
        
        # Analyze by game
        by_game = await conn.fetch("""
            SELECT 
                game_id,
                COUNT(*) as total_records,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT stat_type) as unique_stat_types,
                AVG(value) as avg_value,
                AVG(minutes) as avg_minutes,
                MIN(created_at) as game_date
            FROM player_game_stats
            GROUP BY game_id
            ORDER BY total_records DESC
            LIMIT 10
        """)
        
        print(f"\nTop 10 Games by Stat Count:")
        for game in by_game:
            print(f"  Game {game['game_id']}:")
            print(f"    Total Records: {game['total_records']}")
            print(f"    Unique Players: {game['unique_players']}")
            print(f"    Unique Stat Types: {game['unique_stat_types']}")
            print(f"    Avg Value: {game['avg_value']:.2f}")
            print(f"    Avg Minutes: {game['avg_minutes']:.1f}")
            print(f"    Game Date: {game['game_date']}")
        
        # Analyze minutes distribution
        minutes_analysis = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN minutes < 10 THEN 'Less than 10 min'
                    WHEN minutes < 20 THEN '10-19 min'
                    WHEN minutes < 30 THEN '20-29 min'
                    WHEN minutes < 40 THEN '30-39 min'
                    ELSE '40+ min'
                END as minutes_range,
                COUNT(*) as total_records,
                COUNT(DISTINCT player_id) as unique_players,
                AVG(value) as avg_value,
                AVG(minutes) as avg_minutes_actual
            FROM player_game_stats
            GROUP BY minutes_range
            ORDER BY avg_minutes_actual
        """)
        
        print(f"\nMinutes Distribution Analysis:")
        for minutes in minutes_analysis:
            print(f"  {minutes['minutes_range']}:")
            print(f"    Total Records: {minutes['total_records']}")
            print(f"    Unique Players: {minutes['unique_players']}")
            print(f"    Avg Value: {minutes['avg_value']:.2f}")
            print(f"    Actual Avg Minutes: {minutes['avg_minutes_actual']:.1f}")
        
        # Performance by minutes played
        performance_by_minutes = await conn.fetch("""
            SELECT 
                player_id,
                AVG(minutes) as avg_minutes,
                AVG(CASE WHEN stat_type = 'PTS' THEN value END) as avg_points,
                AVG(CASE WHEN stat_type = 'REB' THEN value END) as avg_rebounds,
                AVG(CASE WHEN stat_type = 'AST' THEN value END) as avg_assists,
                COUNT(*) as total_stats
            FROM player_game_stats
            WHERE stat_type IN ('PTS', 'REB', 'AST')
            GROUP BY player_id
            HAVING COUNT(*) >= 3
            ORDER BY avg_minutes DESC
            LIMIT 10
        """)
        
        print(f"\nPlayer Performance by Minutes Played:")
        for player in performance_by_minutes:
            print(f"  Player {player['player_id']}:")
            print(f"    Avg Minutes: {player['avg_minutes']:.1f}")
            print(f"    Avg Points: {player['avg_points']:.2f}")
            print(f"    Avg Rebounds: {player['avg_rebounds']:.2f}")
            print(f"    Avg Assists: {player['avg_assists']:.2f}")
            print(f"    Total Stats: {player['total_stats']}")
        
        # Recent performance
        recent = await conn.fetch("""
            SELECT * FROM player_game_stats 
            ORDER BY created_at DESC, id DESC 
            LIMIT 10
        """)
        
        print(f"\nRecent Player Game Stats:")
        for stat in recent:
            print(f"  - Player {stat['player_id']}, Game {stat['game_id']}")
            print(f"    {stat['stat_type']}: {stat['value']} in {stat['minutes']} minutes")
            print(f"    Created: {stat['created_at']}")
        
        # High performance games
        high_performance = await conn.fetch("""
            SELECT 
                player_id,
                game_id,
                created_at,
                SUM(CASE WHEN stat_type = 'PTS' THEN value END) as total_points,
                SUM(CASE WHEN stat_type = 'REB' THEN value END) as total_rebounds,
                SUM(CASE WHEN stat_type = 'AST' THEN value END) as total_assists,
                AVG(minutes) as avg_minutes,
                COUNT(*) as total_stats
            FROM player_game_stats
            WHERE stat_type IN ('PTS', 'REB', 'AST')
            GROUP BY player_id, game_id, created_at
            HAVING COUNT(*) >= 3
            ORDER BY total_points DESC
            LIMIT 10
        """)
        
        print(f"\nHigh Performance Games (Top Points):")
        for game in high_performance:
            print(f"  - Player {game['player_id']}, Game {game['game_id']}")
            print(f"    Points: {game['total_points']:.1f}, Rebounds: {game['total_rebounds']:.1f}, Assists: {game['total_assists']:.1f}")
            print(f"    Avg Minutes: {game['avg_minutes']:.1f}, Total Stats: {game['total_stats']}")
            print(f"    Game Date: {game['created_at']}")
        
        # Stat type correlations
        stat_correlations = await conn.fetch("""
            SELECT 
                player_id,
                game_id,
                AVG(CASE WHEN stat_type = 'PTS' THEN value END) as points,
                AVG(CASE WHEN stat_type = 'REB' THEN value END) as rebounds,
                AVG(CASE WHEN stat_type = 'AST' THEN value END) as assists,
                AVG(CASE WHEN stat_type = 'STL' THEN value END) as steals,
                AVG(CASE WHEN stat_type = 'BLK' THEN value END) as blocks,
                AVG(minutes) as avg_minutes
            FROM player_game_stats
            WHERE stat_type IN ('PTS', 'REB', 'AST', 'STL', 'BLK')
            GROUP BY player_id, game_id
            HAVING COUNT(*) >= 5
            ORDER BY points DESC
            LIMIT 5
        """)
        
        print(f"\nComplete Game Performance (5+ Stats):")
        for game in stat_correlations:
            print(f"  - Player {game['player_id']}, Game {game['game_id']}:")
            print(f"    PTS: {game['points']:.1f}, REB: {game['rebounds']:.1f}, AST: {game['assists']:.1f}")
            print(f"    STL: {game['steals']:.1f}, BLK: {game['blocks']:.1f}")
            print(f"    Minutes: {game['avg_minutes']:.1f}")
        
        # Daily activity
        daily_activity = await conn.fetch("""
            SELECT 
                DATE(created_at) as activity_date,
                COUNT(*) as total_records,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT game_id) as unique_games,
                COUNT(DISTINCT stat_type) as unique_stat_types
            FROM player_game_stats
            GROUP BY DATE(created_at)
            ORDER BY activity_date DESC
            LIMIT 10
        """)
        
        print(f"\nDaily Activity (Last 10 Days):")
        for day in daily_activity:
            print(f"  {day['activity_date']}:")
            print(f"    Total Records: {day['total_records']}")
            print(f"    Unique Players: {day['unique_players']}")
            print(f"    Unique Games: {day['unique_games']}")
            print(f"    Unique Stat Types: {day['unique_stat_types']}")
        
        # Value ranges by stat type
        value_ranges = await conn.fetch("""
            SELECT 
                stat_type,
                COUNT(*) as total_records,
                MIN(value) as min_value,
                MAX(value) as max_value,
                AVG(value) as avg_value,
                PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY value) as q1,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY value) as median,
                PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY value) as q3
            FROM player_game_stats
            GROUP BY stat_type
            ORDER BY stat_type
        """)
        
        print(f"\nValue Ranges by Stat Type:")
        for stat in value_ranges:
            print(f"  {stat['stat_type']}:")
            print(f"    Records: {stat['total_records']}")
            print(f"    Range: {stat['min_value']:.1f} - {stat['max_value']:.1f}")
            print(f"    Average: {stat['avg_value']:.2f}")
            print(f"    Median: {stat['median']:.2f}")
            print(f"    Q1-Q3: {stat['q1']:.2f} - {stat['q3']:.2f}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_player_game_stats())
