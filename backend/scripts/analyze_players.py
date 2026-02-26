#!/usr/bin/env python3
"""
PLAYERS ANALYSIS - Comprehensive analysis of the players table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import json

async def analyze_players():
    """Analyze the players table structure and data"""
    
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
    
    try:
        conn = await asyncpg.connect(db_url)
        print("Connected to database")
        
        # Get all players data
        players = await conn.fetch("""
            SELECT * FROM players 
            ORDER BY created_at DESC
            LIMIT 100
        """)
        
        print("PLAYERS TABLE ANALYSIS")
        print("="*80)
        
        print(f"\nTotal Players: {len(players)}")
        
        # Analyze by sport
        by_sport = await conn.fetch("""
            SELECT 
                sport_id,
                COUNT(*) as total_players,
                COUNT(DISTINCT team_id) as unique_teams,
                COUNT(DISTINCT position) as unique_positions,
                COUNT(DISTINCT external_player_id) as unique_external_ids,
                MIN(created_at) as first_player,
                MAX(created_at) as last_player
            FROM players
            GROUP BY sport_id
            ORDER BY total_players DESC
        """)
        
        print(f"\nPlayers by Sport:")
        sport_mapping = {
            1: "NFL",
            30: "NBA",
            32: "NCAA Basketball",
            41: "College Football",
            53: "NHL"
        }
        
        for sport in by_sport:
            sport_name = sport_mapping.get(sport['sport_id'], f"Sport {sport['sport_id']}")
            print(f"  {sport_name}:")
            print(f"    Total Players: {sport['total_players']}")
            print(f"    Unique Teams: {sport['unique_teams']}")
            print(f"    Unique Positions: {sport['unique_positions']}")
            print(f"    Unique External IDs: {sport['unique_external_ids']}")
            print(f"    Period: {sport['first_player']} to {sport['last_player']}")
        
        # Analyze by position
        by_position = await conn.fetch("""
            SELECT 
                position,
                COUNT(*) as total_players,
                COUNT(DISTINCT sport_id) as unique_sports,
                COUNT(DISTINCT team_id) as unique_teams,
                COUNT(DISTINCT external_player_id) as unique_external_ids,
                MIN(created_at) as first_player,
                MAX(created_at) as last_player
            FROM players
            WHERE position IS NOT NULL
            GROUP BY position
            ORDER BY total_players DESC
            LIMIT 10
        """)
        
        print(f"\nTop 10 Positions by Player Count:")
        for position in by_position:
            print(f"  {position}:")
            print(f"    Total Players: {position['total_players']}")
            print(f"    Unique Sports: {position['unique_sports']}")
            print(f"    Unique Teams: {position['unique_teams']}")
            print(f"    Unique External IDs: {position['unique_external_ids']}")
            print(f"    Period: {position['first_player']} to {position['last_player']}")
        
        # Analyze by team
        by_team = await conn.fetch("""
            SELECT 
                team_id,
                COUNT(*) as total_players,
                COUNT(DISTINCT sport_id) as unique_sports,
                COUNT(DISTINCT position) as unique_positions,
                COUNT(DISTINCT external_player_id) as unique_external_ids,
                MIN(created_at) as first_player,
                MAX(created_at) as last_player
            FROM players
            WHERE team_id IS NOT NULL
            GROUP BY team_id
            ORDER BY total_players DESC
            LIMIT 10
        """)
        
        print(f"\nTop 10 Teams by Player Count:")
        for team in by_team:
            print(f"  Team {team['team_id']}:")
            print(f"    Total Players: {team['total_players']}")
            print(f"    Unique Sports: {team['unique_sports']}")
            print(f"    Unique Positions: {team['unique_positions']}")
            print(f"    Unique External IDs: {team['unique_external_ids']}")
            print(f"    Period: {team['first_player']} to {team['last_player']}")
        
        # Analyze external ID coverage
        external_coverage = await conn.fetch("""
            SELECT 
                COUNT(*) as total_players,
                COUNT(DISTINCT external_player_id) as unique_external_ids,
                COUNT(CASE WHEN external_player_id IS NOT NULL THEN 1 END) as players_with_external_id,
                COUNT(CASE WHEN external_player_id IS NULL THEN 1 END) as players_without_external_id,
                ROUND(COUNT(CASE WHEN external_player_id IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 2) as external_id_coverage
            FROM players
            GROUP BY sport_id
            ORDER BY external_id_coverage DESC
        """)
        
        print(f"\nExternal ID Coverage by Sport:")
        for coverage in external_coverage:
            sport_name = sport_mapping.get(coverage['sport_id'], f"Sport {coverage['sport_id']}")
            print(f"  {sport_name}:")
            print(f"    Total Players: {coverage['total_players']}")
            print(f"    Unique External IDs: {coverage['unique_external_ids']}")
            print(f"    With External ID: {coverage['players_with_external_id']}")
            print(f"    Without External ID: {coverage['players_without_external_id']}")
            print(f"    Coverage Rate: {coverage['external_id_coverage']:.2f}%")
        
        # Recent additions
        recent = await conn.fetch("""
            SELECT * FROM players 
            ORDER BY created_at DESC, updated_at DESC 
            LIMIT 10
        """)
        
        print(f"\nRecent Player Additions:")
        for player in recent:
            print(f"  - Player {player['id']}: {player['name']}")
            print(f"    Sport: {player['sport_id']}, Team: {player['team_id']}")
            print(f"    Position: {player['position']}")
            print(f"    External ID: {player['external_player_id']}")
            print(f"    Created: {player['created_at']}")
        
        # Player name analysis
        name_analysis = await conn.fetch("""
            SELECT 
                COUNT(*) as total_players,
                COUNT(CASE WHEN name ILIKE '% %' THEN 1 END) as players_with_space,
                COUNT(CASE WHEN name ILIKE '%.%' THEN 1 END) as players_with_period,
                COUNT(CASE WHEN name ILIKE '%-%' THEN 1 END) as players_with_dash,
                COUNT(CASE WHEN name ILIKE '%_%' THEN 1 END) as players_with_underscore,
                COUNT(CASE WHEN name ILIKE '%.%' THEN 1 END) as players_with_period
            FROM players
            GROUP BY sport_id
        """)
        
        print(f"\nPlayer Name Analysis:")
        for name in name_analysis:
            sport_name = sport_mapping.get(name['sport_id'], f"Sport {name['sport_id']}")
            print(f"  {sport_name}:")
            print(f"    Players with Space: {name['players_with_space']}")
            print(f"    Players with Period: {name['players_with_period']}")
            print(f"    Players with Dash: {name['players_with_dash']}")
            print(f"    Players with Underscore: {name['players_with_underscore']}")
            print(f"    Players with Period: {name['players_with_period']}")
        
        # Position distribution by sport
        position_by_sport = await conn.fetch("""
            SELECT 
                sport_id,
                COUNT(DISTINCT position) as unique_positions,
                STRING_AGG(DISTINCT position, ', ') as all_positions
            FROM players
            WHERE position IS NOT NULL
            GROUP BY sport_id
            ORDER BY unique_positions DESC
        """)
        
        print(f"\nPosition Distribution by Sport:")
        for sport in position_by_sport:
            sport_name = sport_mapping.get(sport['sport_id'], f"Sport {sport['sport_id']}")
            print(f"  {sport_name}:")
            print(f"    Unique Positions: {sport['unique_positions']}")
            print(f"    All Positions: {sport['all_positions']}")
        
        # External ID patterns
        external_patterns = await conn.fetch("""
            SELECT 
                sport_id,
                COUNT(*) as total_players,
                COUNT(CASE WHEN external_player_id LIKE '%_%' THEN 1 END) as underscore_separated,
                COUNT(CASE WHEN external_player_id LIKE '%-%' THEN 1 END) dash_separated,
                COUNT(CASE WHEN external_player_id LIKE '%.%' THEN 1 END} period_separated,
                COUNT(CASE WHEN external_player_id LIKE '%_%' THEN 1 END) dot_separated,
                COUNT(CASE WHEN external_player_id IS NULL THEN 1 END) no_external_id
            FROM players
            GROUP BY sport_id
            ORDER BY total_players DESC
        """)
        
        print(f"\nExternal ID Patterns by Sport:")
        for pattern in external_patterns:
            sport_name = sport_mapping.get(pattern['sport_id'], f"Sport {pattern['sport_id']}")
            print(f"  {sport_name}:")
            print(f"    Underscore Separated: {pattern['underscore_separated']}")
            print(f"    Dash Separated: {pattern['dash_separated']}")
            print(f"    Period Separated: {pattern['period_separated']}")
            print(f"    Dot Separated: {pattern['dot_separated']}")
            print(f"    No External ID: {pattern['no_external_id']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_players())
