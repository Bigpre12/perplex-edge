#!/usr/bin/env python3
"""
POPULATE GAME RESULTS - Initialize and populate the game_results table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_game_results():
    """Populate game_results table with initial data"""
    
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
    
    try:
        conn = await asyncpg.connect(self.db_url)
        print("Connected to database")
        
        # Check if table exists
        table_check = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'game_results'
            )
        """)
        
        if not table_check:
            print("Creating game_results table...")
            await conn.execute("""
                CREATE TABLE game_results (
                    id SERIAL PRIMARY KEY,
                    game_id INTEGER NOT NULL,
                    external_fixture_id VARCHAR(100),
                    home_score INTEGER,
                    away_score INTEGER,
                    period_scores JSONB,
                    is_settled BOOLEAN DEFAULT FALSE,
                    settled_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample game results data
        print("Generating sample game results data...")
        
        game_results = [
            # NFL Games
            {
                'game_id': 1001,
                'external_fixture_id': 'nfl_2026_02_08_kc_buf',
                'home_score': 31,
                'away_score': 28,
                'period_scores': {
                    'Q1': {'home': 7, 'away': 7},
                    'Q2': {'home': 10, 'away': 14},
                    'Q3': {'home': 7, 'away': 0},
                    'Q4': {'home': 7, 'away': 7}
                },
                'is_settled': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(hours=6),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=8),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=6)
            },
            {
                'game_id': 1002,
                'external_fixture_id': 'nfl_2026_02_08_phi_nyg',
                'home_score': 24,
                'away_score': 17,
                'period_scores': {
                    'Q1': {'home': 3, 'away': 7},
                    'Q2': {'home': 14, 'away': 3},
                    'Q3': {'home': 0, 'away': 7},
                    'Q4': {'home': 7, 'away': 0}
                },
                'is_settled': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(hours=5),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=7),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=5)
            },
            {
                'game_id': 1003,
                'external_fixture_id': 'nfl_2026_02_08_dal_sf',
                'home_score': 35,
                'away_score': 42,
                'period_scores': {
                    'Q1': {'home': 14, 'away': 7},
                    'Q2': {'home': 7, 'away': 14},
                    'Q3': {'home': 7, 'away': 14},
                    'Q4': {'home': 7, 'away': 7}
                },
                'is_settled': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=6),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=4)
            },
            {
                'game_id': 1004,
                'external_fixture_id': 'nfl_2026_02_08_min_det',
                'home_score': 21,
                'away_score': 20,
                'period_scores': {
                    'Q1': {'home': 0, 'away': 7},
                    'Q2': {'home': 7, 'away': 7},
                    'Q3': {'home': 7, 'away': 3},
                    'Q4': {'home': 7, 'away': 3}
                },
                'is_settled': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=3)
            },
            # NBA Games
            {
                'game_id': 2001,
                'external_fixture_id': 'nba_2026_02_08_lal_bos',
                'home_score': 118,
                'away_score': 112,
                'period_scores': {
                    'Q1': {'home': 28, 'away': 24},
                    'Q2': {'home': 32, 'away': 30},
                    'Q3': {'home': 29, 'away': 28},
                    'Q4': {'home': 29, 'away': 30}
                },
                'is_settled': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'game_id': 2002,
                'external_fixture_id': 'nba_2026_02_08_gsw_nyk',
                'home_score': 125,
                'away_score': 119,
                'period_scores': {
                    'Q1': {'home': 31, 'away': 28},
                    'Q2': {'home': 32, 'away': 31},
                    'Q3': {'home': 30, 'away': 29},
                    'Q4': {'home': 32, 'away': 31}
                },
                'is_settled': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=1)
            },
            {
                'game_id': 2003,
                'external_fixture_id': 'nba_2026_02_08_mia_phi',
                'home_score': 108,
                'away_score': 115,
                'period_scores': {
                    'Q1': {'home': 25, 'away': 28},
                    'Q2': {'home': 27, 'away': 30},
                    'Q3': {'home': 28, 'away': 29},
                    'Q4': {'home': 28, 'away': 28}
                },
                'is_settled': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            # MLB Games (offseason, but sample data)
            {
                'game_id': 3001,
                'external_fixture_id': 'mlb_2026_02_08_nyy_bos',
                'home_score': 5,
                'away_score': 3,
                'period_scores': {
                    '1': {'home': 2, 'away': 0},
                    '2': {'home': 1, 'away': 1},
                    '3': {'home': 0, 'away': 1},
                    '4': {'home': 1, 'away': 0},
                    '5': {'home': 1, 'away': 1}
                },
                'is_settled': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(hours=8),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=8)
            },
            # Pending games (not yet settled)
            {
                'game_id': 1005,
                'external_fixture_id': 'nfl_2026_02_09_ari_sea',
                'home_score': None,
                'away_score': None,
                'period_scores': {},
                'is_settled': False,
                'settled_at': None,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=1)
            },
            {
                'game_id': 2004,
                'external_fixture_id': 'nba_2026_02_09_chi_cle',
                'home_score': None,
                'away_score': None,
                'period_scores': {},
                'is_settled': False,
                'settled_at': None,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            # Super Bowl special
            {
                'game_id': 9999,
                'external_fixture_id': 'nfl_super_bowl_2026',
                'home_score': 38,
                'away_score': 35,
                'period_scores': {
                    'Q1': {'home': 10, 'away': 7},
                    'Q2': {'home': 14, 'away': 14},
                    'Q3': {'home': 7, 'away': 7},
                    'Q4': {'home': 7, 'away': 7}
                },
                'is_settled': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(hours=12),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=14),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=12)
            }
        ]
        
        # Insert game results
        for result in game_results:
            await conn.execute("""
                INSERT INTO game_results (
                    game_id, external_fixture_id, home_score, away_score, period_scores,
                    is_settled, settled_at, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
                result['game_id'],
                result['external_fixture_id'],
                result['home_score'],
                result['away_score'],
                json.dumps(result['period_scores']),
                result['is_settled'],
                result['settled_at'],
                result['created_at'],
                result['updated_at']
            )
        
        print("Sample game results populated successfully")
        
        # Get game results statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_games,
                COUNT(CASE WHEN is_settled = TRUE THEN 1 END) as settled_games,
                COUNT(CASE WHEN is_settled = FALSE THEN 1 END) as pending_games,
                COUNT(CASE WHEN sport_id = 32 THEN 1 END) as nfl_games,
                COUNT(CASE WHEN sport_id = 30 THEN 1 END) as nba_games,
                COUNT(CASE WHEN sport_id = 29 THEN 1 END) as mlb_games,
                AVG(home_score) as avg_home_score,
                AVG(away_score) as avg_away_score
            FROM game_results
        """)
        
        print(f"\nGame Results Statistics:")
        print(f"  Total Games: {stats['total_games']}")
        print(f"  Settled: {stats['settled_games']}")
        print(f"  Pending: {stats['pending_games']}")
        print(f"  NFL Games: {stats['nfl_games']}")
        print(f"  NBA Games: {stats['nba_games']}")
        print(f"  MLB Games: {stats['mlb_games']}")
        print(f"  Avg Home Score: {stats['avg_home_score']:.1f}")
        print(f"  Avg Away Score: {stats['avg_away_score']:.1f}")
        
        # Get recent settled games
        recent = await conn.fetch("""
            SELECT * FROM game_results 
            WHERE is_settled = TRUE 
            ORDER BY settled_at DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent Settled Games:")
        for game in recent:
            print(f"  - {game['external_fixture_id']}: {game['home_score']}-{game['away_score']} (Settled: {game['settled_at']})")
        
        # Get pending games
        pending = await conn.fetch("""
            SELECT * FROM game_results 
            WHERE is_settled = FALSE 
            ORDER BY created_at DESC
        """)
        
        print(f"\nPending Games:")
        for game in pending:
            print(f"  - {game['external_fixture_id']}: Pending (Created: {game['created_at']})")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_game_results())
