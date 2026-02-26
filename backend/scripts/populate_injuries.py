#!/usr/bin/env python3
"""
POPULATE INJURIES - Initialize and populate the injuries table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_injuries():
    """Populate injuries table with initial data"""
    
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
                WHERE table_name = 'injuries'
            )
        """)
        
        if not table_check:
            print("Creating injuries table...")
            await conn.execute("""
                CREATE TABLE injuries (
                    id SERIAL PRIMARY KEY,
                    sport_id INTEGER NOT NULL,
                    player_id INTEGER NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    status_detail TEXT,
                    is_starter_flag BOOLEAN DEFAULT FALSE,
                    probability DECIMAL(3, 2),
                    source VARCHAR(20) NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample injury data
        print("Generating sample injury data...")
        
        injuries = [
            # NBA injuries (sport_id = 30)
            {
                'sport_id': 30,
                'player_id': 65,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Knee',
                'is_starter_flag': False,
                'probability': 0.5,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7, hours=2)
            },
            {
                'sport_id': 30,
                'player_id': 66,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Back',
                'is_starter_flag': False,
                'probability': 0.5,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7, hours=2)
            },
            {
                'sport_id': 30,
                'player_id': 67,
                'status': 'OUT',
                'status_detail': 'Groin',
                'is_starter_flag': None,
                'probability': 0.0,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7, hours=2)
            },
            {
                'sport_id': 30,
                'player_id': 68,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Hip',
                'is_starter_flag': False,
                'probability': 0.5,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7, hours=2)
            },
            {
                'sport_id': 30,
                'player_id': 69,
                'status': 'OUT',
                'status_detail': 'Toe',
                'is_starter_flag': None,
                'probability': 0.0,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7, hours=2)
            },
            {
                'sport_id': 30,
                'player_id': 70,
                'status': 'OUT',
                'status_detail': 'Hamstring',
                'is_starter_flag': None,
                'probability': 0.0,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7, hours=2)
            },
            {
                'sport_id': 30,
                'player_id': 71,
                'status': 'OUT',
                'status_detail': 'Shoulder (Season-ending)',
                'is_starter_flag': None,
                'probability': 0.0,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7, hours=2)
            },
            {
                'sport_id': 30,
                'player_id': 72,
                'status': 'OUT',
                'status_detail': 'Oblique',
                'is_starter_flag': None,
                'probability': 0.0,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7, hours=2)
            },
            {
                'sport_id': 30,
                'player_id': 27,
                'status': 'OUT',
                'status_detail': 'Foot/Toe',
                'is_starter_flag': True,
                'probability': 0.0,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7, hours=2)
            },
            {
                'sport_id': 30,
                'player_id': 30,
                'status': 'OUT',
                'status_detail': 'Calf',
                'is_starter_flag': True,
                'probability': 0.0,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7, hours=2)
            },
            # NFL injuries (sport_id = 32)
            {
                'sport_id': 32,
                'player_id': 101,
                'status': 'QUESTIONABLE',
                'status_detail': 'Concussion',
                'is_starter_flag': False,
                'probability': 0.3,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=6, hours=4)
            },
            {
                'sport_id': 32,
                'player_id': 102,
                'status': 'DOUBTFUL',
                'status_detail': 'Ankle',
                'is_starter_flag': False,
                'probability': 0.4,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=6, hours=4)
            },
            {
                'sport_id': 32,
                'player_id': 103,
                'status': 'OUT',
                'status_detail': 'ACL Tear (Season-ending)',
                'is_starter_flag': None,
                'probability': 0.0,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=6, hours=4)
            },
            {
                'sport_id': 32,
                'player_id': 104,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Shoulder',
                'is_starter_flag': False,
                'probability': 0.6,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=6, hours=4)
            },
            {
                'sport_id': 32,
                'player_id': 105,
                'status': 'OUT',
                'status_detail': 'Hamstring',
                'is_starter_flag': None,
                'probability': 0.0,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=6, hours=4)
            },
            {
                'sport_id': 32,
                'player_id': 106,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Knee',
                'is_starter_flag': False,
                'probability': 0.7,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=6, hours=4)
            },
            # MLB injuries (sport_id = 29)
            {
                'sport_id': 29,
                'player_id': 201,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Elbow',
                'is_starter_flag': False,
                'probability': 0.4,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=5, hours=6)
            },
            {
                'sport_id': 29,
                'player_id': 202,
                'status': 'OUT',
                'status_detail': 'Shoulder Strain',
                'is_starter_flag': None,
                'probability': 0.0,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=5, hours=6)
            },
            {
                'sport_id': 29,
                'player_id': 203,
                'status': 'OUT',
                'status_detail': 'Tommy John Surgery',
                'is_starter_flag': None,
                'probability': 0.0,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=5, hours=6)
            },
            {
                'sport_id': 29,
                'player_id': 204,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Wrist',
                'is_starter_flag': False,
                'probability': 0.5,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=5, hours=6)
            },
            {
                'sport_id': 29,
                'player_id': 205,
                'status': 'OUT',
                'status_detail': 'Oblique',
                'is_starter_flag': None,
                'probability': 0.0,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=5, hours=6)
            },
            # NHL injuries (sport_id = 53)
            {
                'sport_id': 53,
                'player_id': 301,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Upper Body',
                'is_starter_flag': False,
                'probability': 0.3,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=4, hours=8)
            },
            {
                'sport_id': 53,
                'player_id': 302,
                'status': 'OUT',
                'status_detail': 'Lower Body',
                'is_starter_flag': None,
                'probability': 0.0,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=4, hours=8)
            },
            {
                'sport_id': 53,
                'player_id': 303,
                'status': 'QUESTIONABLE',
                'status_detail': 'Head',
                'is_starter_flag': False,
                'probability': 0.2,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=4, hours=8)
            },
            {
                'sport_id': 53,
                'player_id': 304,
                'status': 'OUT',
                'status_detail': 'Groin',
                'is_starter_flag': None,
                'probability': 0.0,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=4, hours=8)
            },
            # NCAA Basketball injuries (sport_id = 32 but different context)
            {
                'sport_id': 32,
                'player_id': 401,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Ankle Sprain',
                'is_starter_flag': False,
                'probability': 0.6,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=3, hours=10)
            },
            {
                'sport_id': 32,
                'player_id': 402,
                'status': 'OUT',
                'status_detail': 'Knee',
                'is_starter_flag': None,
                'probability': 0.0,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=3, hours=10)
            },
            {
                'sport_id': 32,
                'player_id': 403,
                'status': 'QUESTIONABLE',
                'status_detail': 'Concussion Protocol',
                'is_starter_flag': False,
                'probability': 0.25,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=3, hours=10)
            },
            {
                'sport_id': 32,
                'player_id': 404,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Back Strain',
                'is_starter_flag': False,
                'probability': 0.4,
                'source': 'official',
                'updated_at': datetime.now(timezone.utc) - timedelta(days=3, hours=10)
            }
        ]
        
        # Insert injury data
        for injury in injuries:
            await conn.execute("""
                INSERT INTO injuries (
                    sport_id, player_id, status, status_detail, is_starter_flag,
                    probability, source, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, 
                injury['sport_id'],
                injury['player_id'],
                injury['status'],
                injury['status_detail'],
                injury['is_starter_flag'],
                injury['probability'],
                injury['source'],
                injury['updated_at']
            )
        
        print("Sample injury data populated successfully")
        
        # Get injury statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_injuries,
                COUNT(DISTINCT sport_id) as unique_sports,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(CASE WHEN status = 'OUT' THEN 1 END) as out_injuries,
                COUNT(CASE WHEN status = 'DAY_TO_DAY' THEN 1 END) as day_to_day_injuries,
                COUNT(CASE WHEN status = 'QUESTIONABLE' THEN 1 END) as questionable_injuries,
                COUNT(CASE WHEN status = 'DOUBTFUL' THEN 1 END) as doubtful_injuries,
                COUNT(CASE WHEN is_starter_flag = TRUE THEN 1 END) as starter_injuries,
                AVG(probability) as avg_probability,
                COUNT(CASE WHEN source = 'official' THEN 1 END) as official_injuries
            FROM injuries
        """)
        
        print(f"\nInjury Statistics:")
        print(f"  Total Injuries: {stats['total_injuries']}")
        print(f"  Unique Sports: {stats['unique_sports']}")
        print(f"  Unique Players: {stats['unique_players']}")
        print(f"  Out Injuries: {stats['out_injuries']}")
        print(f" Day-to-Day: {stats['day_to_day_injuries']}")
        print(f" Questionable: {stats['questionable_injuries']}")
        print(f" Doubtful: {stats['doubtful_injuries']}")
        print(f" Starter Injuries: {stats['starter_injuries']}")
        print(f" Avg Probability: {stats['avg_probability']:.2f}")
        print(f" Official Sources: {stats['official_injuries']}")
        
        # Get injuries by sport
        by_sport = await conn.fetch("""
            SELECT 
                sport_id,
                COUNT(*) as total_injuries,
                COUNT(CASE WHEN status = 'OUT' THEN 1 END) as out_injuries,
                COUNT(CASE WHEN status = 'DAY_TO_DAY' THEN 1 END) as day_to_day_injuries,
                AVG(probability) as avg_probability
            FROM injuries
            GROUP BY sport_id
            ORDER BY total_injuries DESC
        """)
        
        print(f"\nInjuries by Sport:")
        sport_names = {30: 'NBA', 32: 'NFL/NCAA', 29: 'MLB', 53: 'NHL'}
        for sport in by_sport:
            sport_name = sport_names.get(sport['sport_id'], f"Sport {sport['sport_id']}")
            print(f"  {sport_name}:")
            print(f"    Total: {sport['total_injuries']}")
            print(f"    Out: {sport['out_injuries']}")
            print(f"    Day-to-Day: {sport['day_to_day_injuries']}")
            print(f"    Avg Probability: {sport['avg_probability']:.2f}")
        
        # Get recent injuries
        recent = await conn.fetch("""
            SELECT * FROM injuries 
            ORDER BY updated_at DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent Injuries:")
        for injury in recent:
            sport_name = {30: 'NBA', 32: 'NFL/NCAA', 29: 'MLB', 53: 'NHL'}.get(injury['sport_id'], f"Sport {injury['sport_id']}")
            print(f"  - {sport_name} Player {injury['player_id']}: {injury['status']}")
            print(f"    Detail: {injury['status_detail']}")
            print(f"    Starter: {injury['is_starter_flag']}")
            print(f"    Probability: {injury['probability']:.2f}")
            print(f"    Source: {injury['source']}")
            print(f"    Updated: {injury['updated_at']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_injuries())
