#!/usr/bin/env python3
"""
POPULATE SEASON ROSTERS - Initialize and populate the season_rosters table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_season_rosters():
    """Populate season_rosters table with initial data"""
    
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
                WHERE table_name = 'season_rosters'
            )
        """)
        
        if not table_check:
            print("Creating season_rosters table...")
            await conn.execute("""
                CREATE TABLE season_rosters (
                    id SERIAL PRIMARY KEY,
                    season_id INTEGER NOT NULL,
                    team_id INTEGER NOT NULL,
                    player_id INTEGER,
                    jersey_number INTEGER,
                    position VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample season roster data
        print("Generating sample season roster data...")
        
        season_rosters = [
            # NBA Season 2026
            {
                'season_id': 2026,
                'team_id': 1,
                'player_id': 1,
                'jersey_number': 23,
                'position': 'SF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 1,
                'player_id': 2,
                'jersey_number': 6,
                'position': 'PG',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 1,
                'player_id': 3,
                'jersey_number': 39,
                'position': 'C',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 1,
                'player_id': 4,
                'jersey_number': 14,
                'position': 'PF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 2,
                'player_id': 5,
                'jersey_number': 30,
                'position': 'SF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 2,
                'player_id': 6,
                'jersey_number': 11,
                'position': 'PG',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 2,
                'player_id': 7,
                'jersey_number': 1,
                'position': 'C',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 3,
                'player_id': 8,
                'jersey_number': 3,
                'position': 'SG',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 3,
                'player_id': 9,
                'jersey_number': 24,
                'position': 'SF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 3,
                'player_id': 10,
                'jersey_number': 28,
                'position': 'PF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 3,
                'player_id': 11,
                'jersey_number': 33,
                'position': 'C',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 4,
                'player_id': 12,
                'jersey_number': 0,
                'position': 'C',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 4,
                'player_id': 13,
                'jersey_number': 42,
                'position': 'SF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 4,
                'player_id': 14,
                'jersey_number': 34,
                'position': 'PF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 4,
                'player_id': 15,
                'jersey_number': 1,
                'position': 'PG',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 5,
                'player_id': 16,
                'jersey_number': 5,
                'position': 'C',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 5,
                'player_id': 17,
                'jersey_number': 13,
                'position': 'SG',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 5,
                'player_id': 18,
                'jersey_number': 2,
                'position': 'SF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 5,
                'player_id': 19,
                'jersey_number': 20,
                'position': 'PF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 5,
                'player_id': 20,
                'jersey_number': 11,
                'position': 'C',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 6,
                'player_id': 21,
                'jersey_number': 4,
                'position': 'C',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 6,
                'player_id': 22,
                'jersey_number': 30,
                'position': 'SG',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 6,
                'player_id': 23,
                'jersey_number': 24,
                'position': 'SF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'season_id': 2026,
                'team_id': 6,
                'player_id': 24,
                'jersey_number': 35,
                'position': 'SF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            # NFL Season 2026
            {
                'season_id': 2026,
                'team_id': 101,
                'player_id': 101,
                'jersey_number': 15,
                'position': 'QB',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=25)
            },
            {
                'season_id': 2026,
                'team_id': 101,
                'player_id': 102,
                'jersey_number': 12,
                'position': 'RB',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=25)
            },
            {
                'season_id': 2026,
                'team_id': 101,
                'player_id': 103,
                'jersey_number': 89,
                'position': 'WR',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=25)
            },
            {
                'season_id': 2026,
                'team_id': 101,
                'player_id': 104,
                'jersey_number': 84,
                'position': 'TE',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=25)
            },
            {
                'season_id': 2026,
                'team_id': 101,
                'player_id': 105,
                'jersey_number': 87,
                'position': 'DE',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=25)
            },
            {
                'season_id': 2026,
                'team_id': 101,
                'player_id': 106,
                'jersey_number': 92,
                'position': 'LB',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=25)
            },
            {
                'season_id': 2026,
                'team_id': 102,
                'player_id': 107,
                'jersey_number': 11,
                'position': 'QB',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=24),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=24)
            },
            {
                'season_id': 2026,
                'team_id': 102,
                'player_id': 108,
                'jersey_number': 8,
                'position': 'RB',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=24),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=24)
            },
            {
                'season_id': 2026,
                'team_id': 102,
                'player_id': 109,
                'jersey_number': 22,
                'position': 'WR',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=24),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=24)
            },
            {
                'season_id': 2026,
                'team_id': 103,
                'player_id': 110,
                'jersey_number': 2,
                'position': 'QB',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=24),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=24)
            },
            # MLB Season 2026
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 201,
                'jersey_number': 99,
                'position': 'RF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 202,
                'jersey_number': 33,
                'position': 'CF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 203,
                'jersey_number': 27,
                'position': '1B',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 204,
                'jersey_number': 3,
                'position': 'SS',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 205,
                'jersey_number': 17,
                'position': 'LF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 206,
                'jersey_number': 5,
                'position': 'CF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 207,
                'jersey_number': 22,
                'position': 'RF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 208,
                'jersey_number': 29,
                'position': '3B',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 209,
                'jersey_number': 15,
                'position': 'SS',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 210,
                'jersey_number': 25,
                'position': 'CF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 211,
                'jersey_number': 19,
                'position': 'P',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 212,
                'jersey_number': 12,
                'position': '2B',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 213,
                'jersey_number': 31,
                'position': 'RF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 214,
                'jersey_number': 7,
                'position': 'CF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 215,
                'jersey_number': 18,
                'position': 'LF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 216,
                'jersey_number': 23,
                'position': 'RF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 217,
                'jersey_number': 16,
                'position': 'SS',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'season_id': 2026,
                'team_id': 201,
                'player_id': 218,
                'jersey_number': 21,
                'position': 'SF',
                'is_active': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            }
        ]
        
        # Insert season roster data
        for roster in season_rosters:
            await conn.execute("""
                INSERT INTO season_rosters (
                    season_id, team_id, player_id, jersey_number, position, is_active, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, 
                roster['season_id'],
                roster['team_id'],
                roster['player_id'],
                roster['jersey_number'],
                roster['position'],
                roster['is_active'],
                roster['created_at'],
                roster['updated_at']
            )
        
        print("Sample season roster data populated successfully")
        
        # Get season roster statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_rosters,
                COUNT(DISTINCT season_id) as unique_seasons,
                COUNT(DISTINCT team_id) as unique_teams,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT position) as unique_positions,
                COUNT(CASE WHEN is_active = true THEN 1 END) as active_rosters,
                COUNT(CASE WHEN is_active = false THEN 1 END) inactive_rosters,
                COUNT(CASE WHEN jersey_number IS NOT NULL THEN 1 END) rosters_with_jerseys,
                AVG(jersey_number) as avg_jersey_number,
                COUNT(DISTINCT position) as unique_positions_count
            FROM season_rosters
        """)
        
        print(f"\nSeason Roster Statistics:")
        print(f"  Total Rosters: {stats['total_rosters']}")
        print(f"  Unique Seasons: {stats['unique_seasons']}")
        print(f"  Unique Teams: {stats['unique_teams']}")
        print(f"  Unique Players: {stats['unique_players']}")
        print(f"  Unique Positions: {stats['unique_positions']}")
        print(f"  Active Rosters: {stats['active_rosters']}")
        print(f"  Inactive Rosters: {stats['inactive_rosters']}")
        print(f"  Rosters with Jerseys: {stats['rosters_with_jerseys']}")
        print(f"  Avg Jersey Number: {stats['avg_jersey_number']:.2f}")
        print(f"  Unique Positions Count: {stats['unique_positions_count']}")
        
        # Get rosters by season
        by_season = await conn.fetch("""
            SELECT 
                season_id,
                COUNT(*) as total_rosters,
                COUNT(DISTINCT team_id) as unique_teams,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT position) as unique_positions,
                COUNT(CASE WHEN is_active = true THEN 1 END) as active_rosters,
                COUNT(CASE WHEN is_active = false THEN 1 END) as inactive_rosters,
                MIN(created_at) as first_roster,
                MAX(created_at) as last_roster
            FROM season_rosters
            GROUP BY season_id
            ORDER BY season_id DESC
            LIMIT 10
        """)
        
        print(f"\nRosters by Season:")
        for season in by_season:
            print(f"  Season {season['season_id']}:")
            print(f"    Total Rosters: {season['total_rosters']}")
            print(f"    Unique Teams: {season['unique_teams']}")
            print(f"    Unique Players: {season['unique_players']}")
            print(f"    Unique Positions: {season['unique_positions']}")
            print(f"    Active Rosters: {season['active_rosters']}")
            print(f"    Period: {season['first_roster']} to {season['last_roster']}")
        
        # Get rosters by team
        by_team = await conn.fetch("""
            SELECT 
                team_id,
                COUNT(*) as total_rosters,
                COUNT(DISTINCT season_id) as unique_seasons,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT position) as unique_positions,
                COUNT(CASE WHEN is_active = true THEN 1 END) as active_rosters,
                COUNT(CASE WHEN is_active = false THEN 1 END) inactive_rosters,
                MIN(created_at) as first_roster,
                MAX(created_at) as last_roster
            FROM season_rosters
            GROUP BY team_id
            ORDER BY total_rosters DESC
            LIMIT 10
        """)
        
        print(f"\nTop 10 Teams by Roster Count:")
        for team in by_team:
            print(f"  Team {team['team_id']}:")
            print(f"    Total Rosters: {team['total_rosters']}")
            print(f"    Unique Seasons: {team['unique_seasons']}")
            print(f"    Unique Players: {team['unique_players']}")
            print(f"    Unique Positions: {team['unique_positions']}")
            print(f"    Active Rosters: {team['active_rosters']}")
            print(f"    Period: {team['first_roster']} to {team['last_roster']}")
        
        # Get rosters by position
        by_position = await conn.fetch("""
            SELECT 
                position,
                COUNT(*) as total_rosters,
                COUNT(DISTINCT season_id) as unique_seasons,
                COUNT(DISTINCT team_id) as unique_teams,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT team_id) as unique_teams_for_position,
                COUNT(CASE WHEN is_active = true THEN 1 END) as active_rosters,
                COUNT(CASE WHEN is_active = false THEN 1 END) inactive_rosters,
                AVG(jersey_number) as avg_jersey_number
            FROM season_rosters
            WHERE position IS NOT NULL
            GROUP BY position
            ORDER BY total_rosters DESC
            LIMIT 10
        """)
        
        print(f"\nTop 10 Positions by Roster Count:")
        for position in by_position:
            print(f"  {position}:")
            print(f"    Total Rosters: {position['total_rosters']}")
            print(f"    Unique Seasons: {position['unique_seasons']}")
            print(f"    Unique Teams: {position['unique_teams']}")
            print(f"    Unique Players: {position['unique_players']}")
            print(f"    Teams for Position: {position['unique_teams_for_position']}")
            print(f"    Active Rosters: {position['active_rosters']}")
            print(f"    Avg Jersey Number: {position['avg_jersey_number']:.2f}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_season_rosters())
