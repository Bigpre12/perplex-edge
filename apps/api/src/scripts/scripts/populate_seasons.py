#!/usr/bin/env python3
"""
POPULATE SEASONS - Initialize and populate the seasons table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_seasons():
    """Populate seasons table with initial data"""
    
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
    
    try:
        conn = await asyncpg.connect(db_url)
        print("Connected to database")
        
        # Check if table exists
        table_check = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'seasons'
            )
        """)
        
        if not table_check:
            print("Creating seasons table...")
            await conn.execute("""
                CREATE TABLE seasons (
                    id SERIAL PRIMARY KEY,
                    sport_id INTEGER NOT NULL,
                    season_year INTEGER NOT NULL,
                    label VARCHAR(100) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    is_current BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample seasons data
        print("Generating sample seasons data...")
        
        seasons = [
            # NBA Seasons
            {
                'sport_id': 30,
                'season_year': 2026,
                'label': '2025-26 NBA Season',
                'start_date': datetime(2025, 10, 22).date(),
                'end_date': datetime(2026, 4, 15).date(),
                'is_current': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'sport_id': 30,
                'season_year': 2025,
                'label': '2024-25 NBA Season',
                'start_date': datetime(2024, 10, 24).date(),
                'end_date': datetime(2025, 4, 13).date(),
                'is_current': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days=365),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=365)
            },
            {
                'sport_id': 30,
                'season_year': 2024,
                'label': '2023-24 NBA Season',
                'start_date': datetime(2023, 10, 24).date(),
                'end_date': datetime(2024, 4, 14).date(),
                'is_current': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days=730),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=730)
            },
            # NFL Seasons
            {
                'sport_id': 1,
                'season_year': 2026,
                'label': '2025 NFL Season',
                'start_date': datetime(2025, 9, 4).date(),
                'end_date': datetime(2026, 2, 8).date(),
                'is_current': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=25)
            },
            {
                'sport_id': 1,
                'season_year': 2025,
                'label': '2024 NFL Season',
                'start_date': datetime(2024, 9, 5).date(),
                'end_date': datetime(2025, 2, 9).date(),
                'is_current': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days(390),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=390)
            },
            {
                'sport_id': 1,
                'season_year': 2024,
                'label': '2023 NFL Season',
                'start_date': datetime(2023, 9, 7).date(),
                'end_date': datetime(2024, 2, 11).date(),
                'is_current': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days(755),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=755)
            },
            # MLB Seasons
            {
                'sport_id': 2,
                'season_year': 2026,
                'label': '2026 MLB Season',
                'start_date': datetime(2026, 3, 28).date(),
                'end_date': datetime(2026, 10, 3).date(),
                'is_current': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'sport_id': 2,
                'season_year': 2025,
                'label': '2025 MLB Season',
                'start_date': datetime(2025, 3, 20).date(),
                'end_date': datetime(2025, 10, 4).date(),
                'is_current': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days(385),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=385)
            },
            {
                'sport_id': 2,
                'season_year': 2024,
                'label': '2024 MLB Season',
                'start_date': datetime(2024, 3, 28).date(),
                'end_date': datetime(2024, 10, 1).date(),
                'is_current': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days(750),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=750)
            },
            # NHL Seasons
            {
                'sport_id': 53,
                'season_year': 2026,
                'label': '2025-26 NHL Season',
                'start_date': datetime(2025, 10, 7).date(),
                'end_date': datetime(2026, 4, 11).date(),
                'is_current': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=15)
            },
            {
                'sport_id': 53,
                'season_year': 2025,
                'label': '2024-25 NHL Season',
                'start_date': datetime(2024, 10, 8).date(),
                'end_date': datetime(2025, 4, 18).date(),
                'is_current': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days=380),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=380)
            },
            {
                'sport_id': 53,
                'season_year': 2024,
                'label': '2023-24 NHL Season',
                'start_date': datetime(2023, 10, 10).date(),
                'end_date': datetime(2024, 4, 18).date(),
                'is_current': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days=745),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=745)
            },
            # NCAA Basketball Seasons
            {
                'sport_id': 32,
                'season_year': 2026,
                'label': '2025-26 NCAA Basketball Season',
                'start_date': datetime(2025, 11, 4).date(),
                'end_date': datetime(2026, 4, 6).date(),
                'is_current': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=10)
            },
            {
                'sport_id': 32,
                'season_year': 2025,
                'label': '2024-25 NCAA Basketball Season',
                'start_date': datetime(2024, 11, 5).date(),
                'end_date': datetime(2025, 4, 7).date(),
                'is_current': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days=375),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=375)
            },
            {
                'sport_id': 32,
                'season_year': 2024,
                'label': '2023-24 NCAA Basketball Season',
                'start_date': datetime(2023, 11, 7).date(),
                'end_date': datetime(2024, 4, 8).date(),
                'is_current': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days=740),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=740)
            },
            # College Football Seasons
            {
                'sport_id': 41,
                'season_year': 2026,
                'label': '2025 College Football Season',
                'start_date': datetime(2025, 8, 29).date(),
                'end_date': datetime(2026, 1, 11).date(),
                'is_current': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=5)
            },
            {
                'sport_id': 41,
                'season_year': 2025,
                'label': '2024 College Football Season',
                'start_date': datetime(2024, 8, 29).date(),
                'end_date': datetime(2025, 1, 20).date(),
                'is_current': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days=370),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=370)
            },
            {
                'sport_id': 41,
                'season_year': 2024,
                'label': '2023 College Football Season',
                'start_date': datetime(2023, 8, 26).date(),
                'end_date': datetime(2024, 1, 8).date(),
                'is_current': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days=735),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=735)
            }
        ]
        
        # Insert seasons data
        for season in seasons:
            await conn.execute("""
                INSERT INTO seasons (
                    sport_id, season_year, label, start_date, end_date, is_current, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, 
                season['sport_id'],
                season['season_year'],
                season['label'],
                season['start_date'],
                season['end_date'],
                season['is_current'],
                season['created_at'],
                season['updated_at']
            )
        
        print("Sample seasons data populated successfully")
        
        # Get seasons statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_seasons,
                COUNT(DISTINCT sport_id) as unique_sports,
                COUNT(DISTINCT season_year) as unique_years,
                COUNT(CASE WHEN is_current = true THEN 1 END) as current_seasons,
                COUNT(CASE WHEN is_current = false THEN 1 END) as past_seasons,
                MIN(start_date) as earliest_start,
                MAX(end_date) as latest_end,
                AVG(EXTRACT(DAY FROM (end_date - start_date))) as avg_season_length_days
            FROM seasons
        """)
        
        print(f"\nSeasons Statistics:")
        print(f"  Total Seasons: {stats['total_seasons']}")
        print(f"  Unique Sports: {stats['unique_sports']}")
        print(f"  Unique Years: {stats['unique_years']}")
        print(f"  Current Seasons: {stats['current_seasons']}")
        print(f"  Past Seasons: {stats['past_seasons']}")
        print(f"  Earliest Start: {stats['earliest_start']}")
        print(f"  Latest End: {stats['latest_end']}")
        print(f"  Avg Season Length: {stats['avg_season_length_days']:.1f} days")
        
        # Get seasons by sport
        by_sport = await conn.fetch("""
            SELECT 
                sport_id,
                COUNT(*) as total_seasons,
                COUNT(DISTINCT season_year) as unique_years,
                COUNT(CASE WHEN is_current = true THEN 1 END) as current_seasons,
                COUNT(CASE WHEN is_current = false THEN 1 END) as past_seasons,
                MIN(start_date) as earliest_start,
                MAX(end_date) as latest_end,
                AVG(EXTRACT(DAY FROM (end_date - start_date))) as avg_season_length_days
            FROM seasons
            GROUP BY sport_id
            ORDER BY total_seasons DESC
        """)
        
        print(f"\nSeasons by Sport:")
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
            print(f"    Total Seasons: {sport['total_seasons']}")
            print(f"    Unique Years: {sport['unique_years']}")
            print(f"    Current Seasons: {sport['current_seasons']}")
            print(f"    Past Seasons: {sport['past_seasons']}")
            print(f"    Period: {sport['earliest_start']} to {sport['latest_end']}")
            print(f"    Avg Season Length: {sport['avg_season_length_days']:.1f} days")
        
        # Get current seasons
        current = await conn.fetch("""
            SELECT 
                sport_id,
                season_year,
                label,
                start_date,
                end_date,
                is_current,
                created_at,
                updated_at
            FROM seasons
            WHERE is_current = true
            ORDER BY sport_id
        """)
        
        print(f"\nCurrent Seasons:")
        for season in current:
            sport_name = sport_mapping.get(season['sport_id'], f"Sport {season['sport_id']}")
            print(f"  {sport_name}:")
            print(f"    {season['label']}")
            print(f"    Period: {season['start_date']} to {season['end_date']}")
            print(f"    Days Active: {(season['end_date'] - season['start_date']).days}")
            print(f"    Created: {season['created_at']}")
        
        # Get season length analysis
        length_analysis = await conn.fetch("""
            SELECT 
                sport_id,
                season_year,
                label,
                start_date,
                end_date,
                EXTRACT(DAY FROM (end_date - start_date)) as season_length_days,
                CASE 
                    WHEN EXTRACT(DAY FROM (end_date - start_date)) < 100 THEN 'Short (< 100 days)'
                    WHEN EXTRACT(DAY FROM (end_date - start_date)) < 200 THEN 'Medium (100-200 days)'
                    WHEN EXTRACT(DAY FROM (end_date - start_date)) < 300 THEN 'Long (200-300 days)'
                    ELSE 'Very Long (300+ days)'
                END as length_category
            FROM seasons
            ORDER BY season_length_days DESC
            LIMIT 10
        """)
        
        print(f"\nSeason Length Analysis (Top 10):")
        for season in length_analysis:
            sport_name = sport_mapping.get(season['sport_id'], f"Sport {season['sport_id']}")
            print(f"  {sport_name} - {season['label']}:")
            print(f"    Length: {season['season_length_days']:.0f} days")
            print(f"    Category: {season['length_category']}")
            print(f"    Period: {season['start_date']} to {season['end_date']}")
        
        # Get recent seasons
        recent = await conn.fetch("""
            SELECT * FROM seasons 
            ORDER BY created_at DESC, updated_at DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent Seasons:")
        for season in recent:
            sport_name = sport_mapping.get(season['sport_id'], f"Sport {season['sport_id']}")
            print(f"  - {sport_name}: {season['label']}")
            print(f"    Period: {season['start_date']} to {season['end_date']}")
            print(f"    Current: {'Yes' if season['is_current'] else 'No'}")
            print(f"    Created: {season['created_at']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_seasons())
