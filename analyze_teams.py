#!/usr/bin/env python3
"""
TEAMS ANALYSIS - Comprehensive analysis of the teams table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import json

async def analyze_teams():
    """Analyze the teams table structure and data"""
    
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
    
    try:
        conn = await asyncpg.connect(db_url)
        print("Connected to database")
        
        # Get all teams data
        teams = await conn.fetch("""
            SELECT * FROM teams 
            ORDER BY id
            LIMIT 100
        """)
        
        print("TEAMS TABLE ANALYSIS")
        print("="*80)
        
        print(f"\nTotal Teams: {len(teams)}")
        
        # Analyze by sport
        by_sport = await conn.fetch("""
            SELECT 
                sport_id,
                COUNT(*) as total_teams,
                COUNT(DISTINCT external_team_id) as unique_external_ids,
                COUNT(DISTINCT abbreviation) as unique_abbreviations,
                STRING_AGG(name, ', ') as team_names,
                STRING_AGG(abbreviation, ', ') as abbreviations,
                MIN(created_at) as first_team,
                MAX(created_at) as last_team
            FROM teams
            GROUP BY sport_id
            ORDER BY total_teams DESC
        """)
        
        print(f"\nTeams by Sport:")
        sport_mapping = {
            1: "NFL",
            2: "MLB",
            30: "NBA",
            32: "NCAA Basketball",
            41: "College Football",
            53: "NHL"
        }
        
        for sport in by_sport:
            sport_name = sport_mapping.get(sport['sport_id'], f"Sport {sport['sport_id']}")
            print(f"  {sport_name}:")
            print(f"    Total Teams: {sport['total_teams']}")
            print(f"    Unique External IDs: {sport['unique_external_ids']}")
            print(f"    Unique Abbreviations: {sport['unique_abbreviations']}")
            print(f"    Team Names: {sport['team_names']}")
            print(f"    Abbreviations: {sport['abbreviations']}")
            print(f"    Period: {sport['first_team']} to {sport['last_team']}")
        
        # Analyze by abbreviation patterns
        abbreviation_patterns = await conn.fetch("""
            SELECT 
                LENGTH(abbreviation) as abbreviation_length,
                COUNT(*) as total_teams,
                COUNT(DISTINCT sport_id) as unique_sports,
                STRING_AGG(abbreviation, ', ') as abbreviations,
                STRING_AGG(name, ', ') as team_names
            FROM teams
            GROUP BY LENGTH(abbreviation)
            ORDER BY abbreviation_length
        """)
        
        print(f"\nTeams by Abbreviation Length:")
        for pattern in abbreviation_patterns:
            print(f"  Length {pattern['abbreviation_length']}:")
            print(f"    Total Teams: {pattern['total_teams']}")
            print(f"    Unique Sports: {pattern['unique_sports']}")
            print(f"    Abbreviations: {pattern['abbreviations']}")
            print(f"    Team Names: {pattern['team_names']}")
        
        # Analyze by external ID patterns
        external_id_patterns = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN external_team_id LIKE '%_los_angeles_%' THEN 'Los Angeles'
                    WHEN external_team_id LIKE '%_new_york_%' THEN 'New York'
                    WHEN external_team_id LIKE '%_chicago_%' THEN 'Chicago'
                    WHEN external_team_id LIKE '%_boston_%' THEN 'Boston'
                    WHEN external_team_id LIKE '%_miami_%' THEN 'Miami'
                    WHEN external_team_id LIKE '%_dallas_%' THEN 'Dallas'
                    WHEN external_team_id LIKE '%_san_francisco_%' THEN 'San Francisco'
                    ELSE 'Other'
                END as city_pattern,
                COUNT(*) as total_teams,
                COUNT(DISTINCT sport_id) as unique_sports,
                STRING_AGG(external_team_id, ', ') as external_ids,
                STRING_AGG(name, ', ') as team_names
            FROM teams
            GROUP BY city_pattern
            ORDER BY total_teams DESC
            LIMIT 10
        """)
        
        print(f"\nTeams by City Pattern:")
        for pattern in external_id_patterns:
            print(f"  {pattern['city_pattern']}:")
            print(f"    Total Teams: {pattern['total_teams']}")
            print(f"    Unique Sports: {pattern['unique_sports']}")
            print(f"    External IDs: {pattern['external_ids']}")
            print(f"    Team Names: {pattern['team_names']}")
        
        # Analyze by name patterns
        name_patterns = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN name ILIKE '%Los Angeles%' THEN 'Los Angeles Teams'
                    WHEN name ILIKE '%New York%' THEN 'New York Teams'
                    WHEN name ILIKE '%Chicago%' THEN 'Chicago Teams'
                    WHEN name ILIKE '%Boston%' THEN 'Boston Teams'
                    WHEN name ILIKE '%Miami%' THEN 'Miami Teams'
                    WHEN name ILIKE '%Dallas%' THEN 'Dallas Teams'
                    WHEN name ILIKE '%San Francisco%' THEN 'San Francisco Teams'
                    ELSE 'Other Teams'
                END as name_pattern,
                COUNT(*) as total_teams,
                COUNT(DISTINCT sport_id) as unique_sports,
                STRING_AGG(name, ', ') as team_names,
                STRING_AGG(abbreviation, ', ') as abbreviations
            FROM teams
            GROUP BY name_pattern
            ORDER BY total_teams DESC
            LIMIT 10
        """)
        
        print(f"\nTeams by Name Pattern:")
        for pattern in name_patterns:
            print(f"  {pattern['name_pattern']}:")
            print(f"    Total Teams: {pattern['total_teams']}")
            print(f"    Unique Sports: {pattern['unique_sports']}")
            print(f"    Team Names: {pattern['team_names']}")
            print(f"    Abbreviations: {pattern['abbreviations']}")
        
        # Analyze by creation date
        creation_analysis = await conn.fetch("""
            SELECT 
                DATE(created_at) as creation_date,
                COUNT(*) as teams_created,
                COUNT(DISTINCT sport_id) as unique_sports,
                STRING_AGG(name, ', ') as team_names,
                STRING_AGG(abbreviation, ', ') as abbreviations
            FROM teams
            GROUP BY DATE(created_at)
            ORDER BY creation_date DESC
            LIMIT 10
        """)
        
        print(f"\nTeams Creation Analysis:")
        for creation in creation_analysis:
            print(f"  {creation['creation_date']}:")
            print(f"    Teams Created: {creation['teams_created']}")
            print(f"    Unique Sports: {creation['unique_sports']}")
            print(f"    Team Names: {creation['team_names']}")
            print(f"    Abbreviations: {creation['abbreviations']}")
        
        # Analyze abbreviation uniqueness
        abbreviation_uniqueness = await conn.fetch("""
            SELECT 
                abbreviation,
                COUNT(*) as occurrences,
                COUNT(DISTINCT sport_id) as unique_sports,
                STRING_AGG(name, ', ') as team_names,
                STRING_AGG(sport_id::text, ', ') as sport_ids
            FROM teams
            GROUP BY abbreviation
            HAVING COUNT(*) > 1
            ORDER BY occurrences DESC
            LIMIT 10
        """)
        
        print(f"\nDuplicate Abbreviations:")
        if abbreviation_uniqueness:
            for abbrev in abbreviation_uniqueness:
                print(f"  {abbrev['abbreviation']}:")
                print(f"    Occurrences: {abbrev['occurrences']}")
                print(f"    Unique Sports: {abbrev['unique_sports']}")
                print(f"    Team Names: {abbrev['team_names']}")
                print(f"    Sport IDs: {abbrev['sport_ids']}")
        else:
            print("  No duplicate abbreviations found")
        
        # Analyze external ID uniqueness
        external_id_uniqueness = await conn.fetch("""
            SELECT 
                external_team_id,
                COUNT(*) as occurrences,
                COUNT(DISTINCT sport_id) as unique_sports,
                STRING_AGG(name, ', ') as team_names,
                STRING_AGG(sport_id::text, ', ') as sport_ids
            FROM teams
            GROUP BY external_team_id
            HAVING COUNT(*) > 1
            ORDER BY occurrences DESC
            LIMIT 10
        """)
        
        print(f"\nDuplicate External IDs:")
        if external_id_uniqueness:
            for external_id in external_id_uniqueness:
                print(f"  {external_id['external_team_id']}:")
                print(f"    Occurrences: {external_id['occurrences']}")
                print(f"    Unique Sports: {external_id['unique_sports']}")
                print(f"    Team Names: {external_id['team_names']}")
                print(f"    Sport IDs: {external_id['sport_ids']}")
        else:
            print("  No duplicate external IDs found")
        
        # Recent teams
        recent = await conn.fetch("""
            SELECT * FROM teams 
            ORDER BY created_at DESC, updated_at DESC 
            LIMIT 10
        """)
        
        print(f"\nRecent Teams:")
        for team in recent:
            sport_name = sport_mapping.get(team['sport_id'], f"Sport {team['sport_id']}")
            print(f"  - {team['name']} ({team['abbreviation']})")
            print(f"    Sport: {sport_name}")
            print(f"    External ID: {team['external_team_id']}")
            print(f"    Created: {team['created_at']}")
        
        # Teams by ID range
        id_analysis = await conn.fetch("""
            SELECT 
                MIN(id) as min_id,
                MAX(id) as max_id,
                COUNT(*) as total_teams,
                MAX(id) - MIN(id) + 1 as id_range,
                ROUND(COUNT(*) * 100.0 / (MAX(id) - MIN(id) + 1), 2) as id_density,
                COUNT(DISTINCT sport_id) as unique_sports
            FROM teams
        """)
        
        print(f"\nID Range Analysis:")
        for analysis in id_analysis:
            print(f"  ID Range: {analysis['min_id']} to {analysis['max_id']}")
            print(f"  Total Teams: {analysis['total_teams']}")
            print(f"  Range Size: {analysis['id_range']}")
            print(f"  ID Density: {analysis['id_density']:.2f}%")
            print(f"  Unique Sports: {analysis['unique_sports']}")
        
        # Team name length analysis
        name_length_analysis = await conn.fetch("""
            SELECT 
                name,
                abbreviation,
                external_team_id,
                LENGTH(name) as name_length,
                LENGTH(abbreviation) as abbreviation_length,
                LENGTH(external_team_id) as external_id_length,
                sport_id,
                created_at
            FROM teams
            ORDER BY name_length DESC
            LIMIT 10
        """)
        
        print(f"\nTeam Name Length Analysis (Top 10):")
        for name in name_length_analysis:
            sport_name = sport_mapping.get(name['sport_id'], f"Sport {name['sport_id']}")
            print(f"  {name['name']}:")
            print(f"    Name Length: {name['name_length']}")
            print(f"    Abbreviation: {name['abbreviation']} ({name['abbreviation_length']} chars)")
            print(f"    External ID: {name['external_team_id']} ({name['external_id_length']} chars)")
            print(f"    Sport: {sport_name}")
            print(f"    Created: {name['created_at']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_teams())
