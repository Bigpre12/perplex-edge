#!/usr/bin/env python3
"""
SPORTS ANALYSIS - Comprehensive analysis of the sports table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import json

async def analyze_sports():
    """Analyze the sports table structure and data"""
    
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
    
    try:
        conn = await asyncpg.connect(db_url)
        print("Connected to database")
        
        # Get all sports data
        sports = await conn.fetch("""
            SELECT * FROM sports 
            ORDER BY id
        """)
        
        print("SPORTS TABLE ANALYSIS")
        print("="*80)
        
        print(f"\nTotal Sports: {len(sports)}")
        
        # Analyze by sport category
        sport_categories = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN key LIKE 'basketball_%' THEN 'Basketball'
                    WHEN key LIKE 'americanfootball_%' THEN 'American Football'
                    WHEN key LIKE 'baseball_%' THEN 'Baseball'
                    WHEN key LIKE 'icehockey_%' THEN 'Ice Hockey'
                    WHEN key LIKE 'soccer_%' THEN 'Soccer'
                    WHEN key LIKE 'tennis_%' THEN 'Tennis'
                    ELSE 'Other'
                END as sport_category,
                COUNT(*) as total_sports,
                STRING_AGG(name, ', ') as sport_names,
                STRING_AGG(league_code, ', ') as league_codes,
                STRING_AGG(key, ', ') as sport_keys,
                MIN(created_at) as first_sport,
                MAX(created_at) as last_sport
            FROM sports
            GROUP BY sport_category
            ORDER BY total_sports DESC
        """)
        
        print(f"\nSports by Category:")
        for category in sport_categories:
            print(f"  {category['sport_category']}:")
            print(f"    Total Sports: {category['total_sports']}")
            print(f"    Sport Names: {category['sport_names']}")
            print(f"    League Codes: {category['league_codes']}")
            print(f"    Sport Keys: {category['sport_keys']}")
            print(f"    Period: {category['first_sport']} to {category['last_sport']}")
        
        # Analyze by league code patterns
        league_patterns = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN league_code LIKE 'NBA%' THEN 'NBA Family'
                    WHEN league_code LIKE 'NFL%' THEN 'NFL Family'
                    WHEN league_code LIKE 'MLB%' THEN 'MLB Family'
                    WHEN league_code LIKE 'NHL%' THEN 'NHL Family'
                    WHEN league_code LIKE 'NCAA%' THEN 'NCAA Family'
                    WHEN league_code LIKE 'UEFA%' THEN 'UEFA Family'
                    WHEN league_code LIKE 'ATP%' THEN 'ATP Family'
                    WHEN league_code LIKE 'WTA%' THEN 'WTA Family'
                    ELSE 'Other'
                END as league_family,
                COUNT(*) as total_sports,
                STRING_AGG(name, ', ') as sport_names,
                STRING_AGG(league_code, ', ') as league_codes,
                AVG(LENGTH(league_code)) as avg_code_length
            FROM sports
            GROUP BY league_family
            ORDER BY total_sports DESC
        """)
        
        print(f"\nSports by League Family:")
        for family in league_patterns:
            print(f"  {family['league_family']}:")
            print(f"    Total Sports: {family['total_sports']}")
            print(f"    Sport Names: {family['sport_names']}")
            print(f"    League Codes: {family['league_codes']}")
            print(f"    Avg Code Length: {family['avg_code_length']:.1f}")
        
        # Analyze key patterns
        key_patterns = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN key LIKE '%_nba' THEN 'NBA'
                    WHEN key LIKE '%_nfl' THEN 'NFL'
                    WHEN key LIKE '%_mlb' THEN 'MLB'
                    WHEN key LIKE '%_nhl' THEN 'NHL'
                    WHEN key LIKE '%_ncaab' THEN 'NCAA Basketball'
                    WHEN key LIKE '%_ncaaf' THEN 'NCAA Football'
                    WHEN key LIKE '%_uefa_%' THEN 'UEFA'
                    WHEN key LIKE '%_atp' THEN 'ATP'
                    WHEN key LIKE '%_wta' THEN 'WTA'
                    ELSE 'Other'
                END as key_pattern,
                COUNT(*) as total_sports,
                STRING_AGG(name, ', ') as sport_names,
                STRING_AGG(key, ', ') as sport_keys,
                AVG(LENGTH(key)) as avg_key_length
            FROM sports
            GROUP BY key_pattern
            ORDER BY total_sports DESC
        """)
        
        print(f"\nSports by Key Pattern:")
        for pattern in key_patterns:
            print(f"  {pattern['key_pattern']}:")
            print(f"    Total Sports: {pattern['total_sports']}")
            print(f"    Sport Names: {pattern['sport_names']}")
            print(f"    Sport Keys: {pattern['sport_keys']}")
            print(f"    Avg Key Length: {pattern['avg_key_length']:.1f}")
        
        # Analyze creation patterns
        creation_analysis = await conn.fetch("""
            SELECT 
                DATE(created_at) as creation_date,
                COUNT(*) as sports_created,
                STRING_AGG(name, ', ') as sport_names,
                STRING_AGG(league_code, ', ') as league_codes
            FROM sports
            GROUP BY DATE(created_at)
            ORDER BY creation_date DESC
        """)
        
        print(f"\nSports Creation Analysis:")
        for creation in creation_analysis:
            print(f"  {creation['creation_date']}:")
            print(f"    Sports Created: {creation['sports_created']}")
            print(f"    Sport Names: {creation['sport_names']}")
            print(f"    League Codes: {creation['league_codes']}")
        
        # Analyze name lengths
        name_analysis = await conn.fetch("""
            SELECT 
                name,
                league_code,
                key,
                LENGTH(name) as name_length,
                LENGTH(league_code) as code_length,
                LENGTH(key) as key_length,
                created_at
            FROM sports
            ORDER BY name_length DESC
            LIMIT 10
        """)
        
        print(f"\nName Length Analysis (Top 10):")
        for name in name_analysis:
            print(f"  {name['name']}:")
            print(f"    Name Length: {name['name_length']}")
            print(f"    League Code: {name['league_code']} ({name['code_length']} chars)")
            print(f"    Key: {name['key']} ({name['key_length']} chars)")
            print(f"    Created: {name['created_at']}")
        
        # Analyze code uniqueness
        code_analysis = await conn.fetch("""
            SELECT 
                league_code,
                COUNT(*) as occurrences,
                STRING_AGG(name, ', ') as sport_names,
                STRING_AGG(key, ', ') as sport_keys
            FROM sports
            GROUP BY league_code
            HAVING COUNT(*) > 1
            ORDER BY occurrences DESC
        """)
        
        print(f"\nDuplicate League Codes:")
        if code_analysis:
            for code in code_analysis:
                print(f"  {code['league_code']}:")
                print(f"    Occurrences: {code['occurrences']}")
                print(f"    Sport Names: {code['sport_names']}")
                print(f"    Sport Keys: {code['sport_keys']}")
        else:
            print("  No duplicate league codes found")
        
        # Analyze key uniqueness
        key_analysis = await conn.fetch("""
            SELECT 
                key,
                COUNT(*) as occurrences,
                STRING_AGG(name, ', ') as sport_names,
                STRING_AGG(league_code, ', ') as league_codes
            FROM sports
            GROUP BY key
            HAVING COUNT(*) > 1
            ORDER BY occurrences DESC
        """)
        
        print(f"\nDuplicate Keys:")
        if key_analysis:
            for key in key_analysis:
                print(f"  {key['key']}:")
                print(f"    Occurrences: {key['occurrences']}")
                print(f"    Sport Names: {key['sport_names']}")
                print(f"    League Codes: {key['league_codes']}")
        else:
            print("  No duplicate keys found")
        
        # Recent sports
        recent = await conn.fetch("""
            SELECT * FROM sports 
            ORDER BY created_at DESC, updated_at DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent Sports:")
        for sport in recent:
            print(f"  - {sport['name']} ({sport['league_code']})")
            print(f"    Key: {sport['key']}")
            print(f"    Created: {sport['created_at']}")
            print(f"    Updated: {sport['updated_at']}")
        
        # Sports by ID range
        id_analysis = await conn.fetch("""
            SELECT 
                MIN(id) as min_id,
                MAX(id) as max_id,
                COUNT(*) as total_sports,
                MAX(id) - MIN(id) + 1 as id_range,
                ROUND(COUNT(*) * 100.0 / (MAX(id) - MIN(id) + 1), 2) as id_density
            FROM sports
        """)
        
        print(f"\nID Range Analysis:")
        for analysis in id_analysis:
            print(f"  ID Range: {analysis['min_id']} to {analysis['max_id']}")
            print(f"  Total Sports: {analysis['total_sports']}")
            print(f"  Range Size: {analysis['id_range']}")
            print(f"  ID Density: {analysis['id_density']:.2f}%")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_sports())
