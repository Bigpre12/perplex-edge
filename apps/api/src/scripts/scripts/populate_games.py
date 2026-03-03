#!/usr/bin/env python3
"""
POPULATE GAMES TABLE - Initialize and populate the games table with sample data
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_games():
    """Populate games table with initial data"""
    
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
                WHERE table_name = 'games'
            )
        """)
        
        if not table_check:
            print("Creating games table...")
            await conn.execute("""
                CREATE TABLE games (
                    id SERIAL PRIMARY KEY,
                    sport_id INTEGER NOT NULL,
                    external_game_id VARCHAR(100) NOT NULL,
                    home_team_id INTEGER,
                    away_team_id INTEGER,
                    start_time TIMESTAMP WITH TIME ZONE,
                    status VARCHAR(20) DEFAULT 'scheduled',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    season_id INTEGER
                )
            """)
            print("Table created")
        
        # Generate sample games data
        print("Generating sample games data...")
        
        games = [
            # NFL Games (sport_id = 32)
            {
                'sport_id': 32,
                'external_game_id': 'nfl_kc_buf_20260208',
                'home_team_id': 48,
                'away_team_id': 83,
                'start_time': datetime.now(timezone.utc) - timedelta(hours=6),
                'status': 'final',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=8),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=6),
                'season_id': 2026
            },
            {
                'sport_id': 32,
                'external_game_id': 'nfl_phi_nyg_20260208',
                'home_team_id': 84,
                'away_team_id': 50,
                'start_time': datetime.now(timezone.utc) - timedelta(hours=5),
                'status': 'final',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=7),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=5),
                'season_id': 2026
            },
            {
                'sport_id': 32,
                'external_game_id': 'nfl_dal_sf_20260208',
                'home_team_id': 85,
                'away_team_id': 86,
                'start_time': datetime.now(timezone.utc) - timedelta(hours=4),
                'status': 'final',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=6),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'season_id': 2026
            },
            {
                'sport_id': 32,
                'external_game_id': 'nfl_min_det_20260208',
                'home_team_id': 73,
                'away_team_id': 37,
                'start_time': datetime.now(timezone.utc) - timedelta(hours=3),
                'status': 'final',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'season_id': 2026
            },
            {
                'sport_id': 32,
                'external_game_id': 'nfl_ari_sea_20260209',
                'home_team_id': 390,
                'away_team_id': 391,
                'start_time': datetime.now(timezone.utc) + timedelta(hours=1),
                'status': 'scheduled',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'season_id': 2026
            },
            {
                'sport_id': 32,
                'external_game_id': 'nfl_gb_phi_20260209',
                'home_team_id': 295,
                'away_team_id': 84,
                'start_time': datetime.now(timezone.utc) + timedelta(hours=4),
                'status': 'scheduled',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'season_id': 2026
            },
            # NBA Games (sport_id = 30)
            {
                'sport_id': 30,
                'external_game_id': 'nba_lal_bos_20260208',
                'home_team_id': 17,
                'away_team_id': 27,
                'start_time': datetime.now(timezone.utc) - timedelta(hours=2),
                'status': 'final',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'season_id': 2026
            },
            {
                'sport_id': 30,
                'external_game_id': 'nba_gsw_nyk_20260208',
                'home_team_id': 26,
                'away_team_id': 10,
                'start_time': datetime.now(timezone.utc) - timedelta(hours=1),
                'status': 'final',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'season_id': 2026
            },
            {
                'sport_id': 30,
                'external_game_id': 'nba_mia_phi_20260208',
                'home_team_id': 161,
                'away_team_id': 37,
                'start_time': datetime.now(timezone.utc) - timedelta(minutes=30),
                'status': 'final',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'season_id': 2026
            },
            {
                'sport_id': 30,
                'external_game_id': 'nba_chi_cle_20260209',
                'home_team_id': 17,
                'away_team_id': 27,
                'start_time': datetime.now(timezone.utc) + timedelta(minutes=30),
                'status': 'scheduled',
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'season_id': 2026
            },
            {
                'sport_id': 30,
                'external_game_id': 'nba_det_cha_20260209',
                'home_team_id': 17,
                'away_team_id': 27,
                'start_time': datetime.now(timezone.utc) + timedelta(hours=1),
                'status': 'scheduled',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'season_id': 2026
            },
            # NHL Games (sport_id = 53)
            {
                'sport_id': 53,
                'external_game_id': 'nhl_ran_hur_20260206',
                'home_team_id': 390,
                'away_team_id': 391,
                'start_time': datetime.now(timezone.utc) - timedelta(hours=24),
                'status': 'final',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=26),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=24),
                'season_id': 2026
            },
            {
                'sport_id': 53,
                'external_game_id': 'nhl_tor_mon_20260208',
                'home_team_id': 295,
                'away_team_id': 84,
                'start_time': datetime.now(timezone.utc) + timedelta(hours=2),
                'status': 'scheduled',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'season_id': 2026
            },
            # NCAA Basketball Games (sport_id = 32 but different external IDs)
            {
                'sport_id': 32,
                'external_game_id': 'ncaab_espn_401825499',
                'home_team_id': 295,
                'away_team_id': 378,
                'start_time': datetime.now(timezone.utc) - timedelta(hours=6),
                'status': 'scheduled',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=8),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=6),
                'season_id': 2026
            },
            {
                'sport_id': 32,
                'external_game_id': 'ncaab_espn_401825481',
                'home_team_id': 73,
                'away_team_id': 37,
                'start_time': datetime.now(timezone.utc) - timedelta(hours=24),
                'status': 'scheduled',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=26),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=24),
                'season_id': 2026
            },
            {
                'sport_id': 32,
                'external_game_id': 'ncaab_espn_401828400',
                'home_team_id': 85,
                'away_team_id': 86,
                'start_time': datetime.now(timezone.utc) - timedelta(hours=24),
                'status': 'scheduled',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=26),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=24),
                'season_id': 2026
            },
            {
                'sport_id': 32,
                'external_game_id': 'ncaab_espn_401825498',
                'home_team_id': 38,
                'away_team_id': 84,
                'start_time': datetime.now(timezone.utc) - timedelta(hours=6),
                'status': 'scheduled',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=8),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=6),
                'season_id': 2026
            },
            {
                'sport_id': 32,
                'external_game_id': 'ncaab_espn_401808225',
                'home_team_id': 260,
                'away_team_id': 161,
                'start_time': datetime.now(timezone.utc) - timedelta(hours=3),
                'status': 'scheduled',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'season_id': 2026
            }
        ]
        
        # Insert games
        for game in games:
            await conn.execute("""
                INSERT INTO games (
                    sport_id, external_game_id, home_team_id, away_team_id,
                    start_time, status, created_at, updated_at, season_id
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
                game['sport_id'],
                game['external_game_id'],
                game['home_team_id'],
                game['away_team_id'],
                game['start_time'],
                game['status'],
                game['created_at'],
                game['updated_at'],
                game['season_id']
            )
        
        print("Sample games populated successfully")
        
        # Get games statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_games,
                COUNT(CASE WHEN status = 'final' THEN 1 END) as final_games,
                COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_games,
                COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_games,
                COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_games,
                COUNT(CASE WHEN sport_id = 32 THEN 1 END) as nfl_games,
                COUNT(CASE WHEN sport_id = 30 THEN 1 END) as nba_games,
                COUNT(CASE WHEN sport_id = 53 THEN 1 END) as nhl_games,
                COUNT(CASE WHEN sport_id = 32 AND external_game_id LIKE 'ncaab_%' THEN 1 END) as ncaab_games
            FROM games
        """)
        
        print(f"\nGames Statistics:")
        print(f"  Total: {stats['total_games']}")
        print(f"  Final: {stats['final_games']}")
        print(f"  Scheduled: {stats['scheduled_games']}")
        print(f"  In Progress: {stats['in_progress_games']}")
        print(f"  Cancelled: {stats['cancelled_games']}")
        print(f"  NFL: {stats['nfl_games']}")
        print(f"  NBA: {stats['nba_games']}")
        print(f"  NHL: {stats['nhl_games']}")
        print(f"  NCAA Basketball: {stats['ncaab_games']}")
        
        # Get recent games
        recent = await conn.fetch("""
            SELECT * FROM games 
            ORDER BY start_time DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent Games:")
        for game in recent:
            sport_name = {32: 'NFL', 30: 'NBA', 53: 'NHL'}.get(game['sport_id'], f"Sport {game['sport_id']}")
            print(f"  - {game['external_game_id']}: {sport_name}")
            print(f"    Status: {game['status']}, Start: {game['start_time']}")
        
        # Get upcoming games
        upcoming = await conn.fetch("""
            SELECT * FROM games 
            WHERE start_time > NOW()
            ORDER BY start_time ASC 
            LIMIT 5
        """)
        
        print(f"\nUpcoming Games:")
        for game in upcoming:
            sport_name = {32: 'NFL', 30: 'NBA', 53: 'NHL'}.get(game['sport_id'], f"Sport {game['sport_id']}")
            print(f"  - {game['external_game_id']}: {sport_name}")
            print(f"    Status: {game['status']}, Start: {game['start_time']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_games())
