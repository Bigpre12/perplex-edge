#!/usr/bin/env python3
"""
POPULATE PLAYER STATS - Initialize and populate the player_stats table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_player_stats():
    """Populate player_stats table with initial data"""
    
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
                WHERE table_name = 'player_stats'
            )
        """)
        
        if not table_check:
            print("Creating player_stats table...")
            await conn.execute("""
                CREATE TABLE player_stats (
                    id SERIAL PRIMARY KEY,
                    player_name VARCHAR(100) NOT NULL,
                    team VARCHAR(100) NOT NULL,
                    opponent VARCHAR(100) NOT NULL,
                    date DATE NOT NULL,
                    stat_type VARCHAR(50) NOT NULL,
                    actual_value DECIMAL(10, 2) NOT NULL,
                    line DECIMAL(10, 2),
                    result BOOLEAN,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample player stats data
        print("Generating sample player stats data...")
        
        player_stats = [
            # NBA Games
            {
                'player_name': 'LeBron James',
                'team': 'Los Angeles Lakers',
                'opponent': 'Boston Celtics',
                'date': datetime.now(timezone.utc).date() - timedelta(days=1),
                'stat_type': 'points',
                'actual_value': 27.5,
                'line': 24.5,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'LeBron James',
                'team': 'Los Angeles Lakers',
                'opponent': 'Boston Celtics',
                'date': datetime.now(timezone.utc).date() - timedelta(days=1),
                'stat_type': 'rebounds',
                'actual_value': 8.2,
                'line': 7.5,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'LeBron James',
                'team': 'Los Angeles Lakers',
                'opponent': 'Boston Celtics',
                'date': datetime.now(timezone.utc).date() - timedelta(days=1),
                'stat_type': 'assists',
                'actual_value': 7.8,
                'line': 6.5,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Stephen Curry',
                'team': 'Golden State Warriors',
                'opponent': 'Los Angeles Lakers',
                'date': datetime.now(timezone.utc).date() - timedelta(days=2),
                'stat_type': 'points',
                'actual_value': 31.2,
                'line': 28.5,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=2)
            },
            {
                'player_name': 'Stephen Curry',
                'team': 'Golden State Warriors',
                'opponent': 'Los Angeles Lakers',
                'date': datetime.now(timezone.utc).date() - timedelta(days=2),
                'stat_type': 'three_pointers',
                'actual_value': 4.5,
                'line': 4.0,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=2)
            },
            {
                'player_name': 'Kevin Durant',
                'team': 'Phoenix Suns',
                'opponent': 'Denver Nuggets',
                'date': datetime.now(timezone.utc).date() - timedelta(days=3),
                'stat_type': 'points',
                'actual_value': 25.8,
                'line': 26.5,
                'result': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=3)
            },
            {
                'player_name': 'Kevin Durant',
                'team': 'Phoenix Suns',
                'opponent': 'Denver Nuggets',
                'date': datetime.now(timezone.utc).date() - timedelta(days=3),
                'stat_type': 'rebounds',
                'actual_value': 6.5,
                'line': 7.0,
                'result': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=3)
            },
            # NFL Games
            {
                'player_name': 'Patrick Mahomes',
                'team': 'Kansas City Chiefs',
                'opponent': 'Buffalo Bills',
                'date': datetime.now(timezone.utc).date() - timedelta(days=4),
                'stat_type': 'passing_yards',
                'actual_value': 298.5,
                'line': 285.5,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=4)
            },
            {
                'player_name': 'Patrick Mahomes',
                'team': 'Kansas City Chiefs',
                'opponent': 'Buffalo Bills',
                'date': datetime.now(timezone.utc).date() - timedelta(days=4),
                'stat_type': 'passing_touchdowns',
                'actual_value': 3.0,
                'line': 2.5,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=4)
            },
            {
                'player_name': 'Josh Allen',
                'team': 'Buffalo Bills',
                'opponent': 'Kansas City Chiefs',
                'date': datetime.now(timezone.utc).date() - timedelta(days=4),
                'stat_type': 'passing_yards',
                'actual_value': 255.2,
                'line': 265.5,
                'result': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=4)
            },
            {
                'player_name': 'Josh Allen',
                'team': 'Buffalo Bills',
                'opponent': 'Kansas City Chiefs',
                'date': datetime.now(timezone.utc).date() - timedelta(days=4),
                'stat_type': 'rushing_yards',
                'actual_value': 42.8,
                'line': 35.5,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=4)
            },
            {
                'player_name': 'Justin Herbert',
                'team': 'Los Angeles Chargers',
                'opponent': 'Las Vegas Raiders',
                'date': datetime.now(timezone.utc).date() - timedelta(days=5),
                'stat_type': 'passing_yards',
                'actual_value': 278.9,
                'line': 275.5,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=5)
            },
            {
                'player_name': 'Justin Herbert',
                'team': 'Los Angeles Chargers',
                'opponent': 'Las Vegas Raiders',
                'date': datetime.now(timezone.utc).date() - timedelta(days=5),
                'stat_type': 'passing_touchdowns',
                'actual_value': 2.0,
                'line': 2.5,
                'result': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=5)
            },
            # MLB Games
            {
                'player_name': 'Aaron Judge',
                'team': 'New York Yankees',
                'opponent': 'Boston Red Sox',
                'date': datetime.now(timezone.utc).date() - timedelta(days=6),
                'stat_type': 'home_runs',
                'actual_value': 2.0,
                'line': 1.5,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=6),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=6)
            },
            {
                'player_name': 'Aaron Judge',
                'team': 'New York Yankees',
                'opponent': 'Boston Red Sox',
                'date': datetime.now(timezone.utc).date() - timedelta(days=6),
                'stat_type': 'rbis',
                'actual_value': 3.0,
                'line': 2.5,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=6),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=6)
            },
            {
                'player_name': 'Mike Trout',
                'team': 'Los Angeles Angels',
                'opponent': 'Seattle Mariners',
                'date': datetime.now(timezone.utc).date() - timedelta(days=7),
                'stat_type': 'hits',
                'actual_value': 2.0,
                'line': 1.5,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=7),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7)
            },
            {
                'player_name': 'Mike Trout',
                'team': 'Los Angeles Angels',
                'opponent': 'Seattle Mariners',
                'date': datetime.now(timezone.utc).date() - timedelta(days=7),
                'stat_type': 'batting_average',
                'actual_value': 0.286,
                'line': 0.275,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=7),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7)
            },
            {
                'player_name': 'Shohei Ohtani',
                'team': 'Los Angeles Angels',
                'opponent': 'Seattle Mariners',
                'date': datetime.now(timezone.utc).date() - timedelta(days=7),
                'stat_type': 'strikeouts',
                'actual_value': 8.0,
                'line': 7.5,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=7),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7)
            },
            {
                'player_name': 'Shohei Ohtani',
                'team': 'Los Angeles Angels',
                'opponent': 'Seattle Mariners',
                'date': datetime.now(timezone.utc).date() - timedelta(days=7),
                'stat_type': 'hits',
                'actual_value': 1.0,
                'line': 1.5,
                'result': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days=7),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7)
            },
            # NHL Games
            {
                'player_name': 'Connor McDavid',
                'team': 'Edmonton Oilers',
                'opponent': 'Calgary Flames',
                'date': datetime.now(timezone.utc).date() - timedelta(days=8),
                'stat_type': 'points',
                'actual_value': 2.0,
                'line': 1.5,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=8),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=8)
            },
            {
                'player_name': 'Connor McDavid',
                'team': 'Edmonton Oilers',
                'opponent': 'Calgary Flames',
                'date': datetime.now(timezone.utc).date() - timedelta(days=8),
                'stat_type': 'assists',
                'actual_value': 1.0,
                'line': 1.5,
                'result': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days=8),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=8)
            },
            {
                'player_name': 'Nathan MacKinnon',
                'team': 'Colorado Avalanche',
                'opponent': 'Vancouver Canucks',
                'date': datetime.now(timezone.utc).date() - timedelta(days=9),
                'stat_type': 'points',
                'actual_value': 1.0,
                'line': 1.5,
                'result': False,
                'created_at': datetime.now(timezone.utc) - timedelta(days=9),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=9)
            },
            {
                'player_name': 'Nathan MacKinnon',
                'team': 'Colorado Avalanche',
                'opponent': 'Vancouver Canucks',
                'date': datetime.now(timezone.utc).date() - timedelta(days=9),
                'stat_type': 'shots',
                'actual_value': 6.0,
                'line': 5.5,
                'result': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=9),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=9)
            },
            # Recent games with mixed results
            {
                'player_name': 'LeBron James',
                'team': 'Los Angeles Lakers',
                'opponent': 'Miami Heat',
                'date': datetime.now(timezone.utc).date(),
                'stat_type': 'points',
                'actual_value': 22.5,
                'line': 25.0,
                'result': False,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            },
            {
                'player_name': 'LeBron James',
                'team': 'Los Angeles Lakers',
                'opponent': 'Miami Heat',
                'date': datetime.now(timezone.utc).date(),
                'stat_type': 'rebounds',
                'actual_value': 6.8,
                'line': 7.5,
                'result': False,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            },
            {
                'player_name': 'Stephen Curry',
                'team': 'Golden State Warriors',
                'opponent': 'Phoenix Suns',
                'date': datetime.now(timezone.utc).date(),
                'stat_type': 'points',
                'actual_value': 29.5,
                'line': 29.0,
                'result': True,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            },
            {
                'player_name': 'Patrick Mahomes',
                'team': 'Kansas City Chiefs',
                'opponent': 'Cincinnati Bengals',
                'date': datetime.now(timezone.utc).date(),
                'stat_type': 'passing_yards',
                'actual_value': 312.0,
                'line': 295.0,
                'result': True,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            },
            {
                'player_name': 'Patrick Mahomes',
                'team': 'Kansas City Chiefs',
                'opponent': 'Cincinnati Bengals',
                'date': datetime.now(timezone.utc).date(),
                'stat_type': 'passing_touchdowns',
                'actual_value': 2.0,
                'line': 2.5,
                'result': False,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
        ]
        
        # Insert player stats data
        for stat in player_stats:
            await conn.execute("""
                INSERT INTO player_stats (
                    player_name, team, opponent, date, stat_type, actual_value, line, result,
                    created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, 
                stat['player_name'],
                stat['team'],
                stat['opponent'],
                stat['date'],
                stat['stat_type'],
                stat['actual_value'],
                stat['line'],
                stat['result'],
                stat['created_at'],
                stat['updated_at']
            )
        
        print("Sample player stats data populated successfully")
        
        # Get player statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_stats,
                COUNT(DISTINCT player_name) as unique_players,
                COUNT(DISTINCT team) as unique_teams,
                COUNT(DISTINCT opponent) as unique_opponents,
                COUNT(DISTINCT stat_type) as unique_stat_types,
                COUNT(DISTINCT date) as unique_dates,
                AVG(actual_value) as avg_actual_value,
                AVG(line) as avg_line,
                COUNT(CASE WHEN result = true THEN 1 END) as hits,
                COUNT(CASE WHEN result = false THEN 1 END) as misses,
                ROUND(COUNT(CASE WHEN result = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage
            FROM player_stats
        """)
        
        print(f"\nPlayer Statistics Summary:")
        print(f"  Total Stats: {stats['total_stats']}")
        print(f"  Unique Players: {stats['unique_players']}")
        print(f"  Unique Teams: {stats['unique_teams']}")
        print(f"  Unique Opponents: {stats['unique_opponents']}")
        print(f"  Unique Stat Types: {stats['unique_stat_types']}")
        print(f"  Unique Dates: {stats['unique_dates']}")
        print(f"  Avg Actual Value: {stats['avg_actual_value']:.2f}")
        print(f"  Avg Line: {stats['avg_line']:.2f}")
        print(f"  Hits: {stats['hits']}")
        print(f"  Misses: {stats['misses']}")
        print(f"  Hit Rate: {stats['hit_rate_percentage']:.2f}%")
        
        # Get stats by player
        by_player = await conn.fetch("""
            SELECT 
                player_name,
                COUNT(*) as total_stats,
                COUNT(CASE WHEN result = true THEN 1 END) as hits,
                COUNT(CASE WHEN result = false THEN 1 END) as misses,
                ROUND(COUNT(CASE WHEN result = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage,
                AVG(actual_value) as avg_actual_value,
                AVG(line) as avg_line,
                COUNT(DISTINCT stat_type) as unique_stat_types,
                MIN(date) as first_game,
                MAX(date) as last_game
            FROM player_stats
            GROUP BY player_name
            ORDER BY hit_rate_percentage DESC
            LIMIT 10
        """)
        
        print(f"\nTop 10 Players by Hit Rate:")
        for player in by_player:
            print(f"  {player}:")
            print(f"    Total Stats: {player['total_stats']}")
            print(f"    Hit Rate: {player['hit_rate_percentage']:.2f}%")
            print(f"    Hits/Misses: {player['hits']}/{player['misses']}")
            print(f"    Avg Actual: {player['avg_actual_value']:.2f}, Avg Line: {player['avg_line']:.2f}")
            print(f"    Stat Types: {player['unique_stat_types']}")
            print(f"    Period: {player['first_game']} to {player['last_game']}")
        
        # Get stats by stat type
        by_stat_type = await conn.fetch("""
            SELECT 
                stat_type,
                COUNT(*) as total_stats,
                COUNT(CASE WHEN result = true THEN 1 END) as hits,
                COUNT(CASE WHEN result = false THEN 1 END) as misses,
                ROUND(COUNT(CASE WHEN result = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage,
                AVG(actual_value) as avg_actual_value,
                AVG(line) as avg_line,
                COUNT(DISTINCT player_name) as unique_players
            FROM player_stats
            GROUP BY stat_type
            ORDER BY hit_rate_percentage DESC
        """)
        
        print(f"\nPerformance by Stat Type:")
        for stat in by_stat_type:
            print(f"  {stat}:")
            print(f"    Total Stats: {stat['total_stats']}")
            print(f"    Hit Rate: {stat['hit_rate_percentage']:.2f}%")
            print(f"    Hits/Misses: {stat['hits']}/{stat['misses']}")
            print(f"    Avg Actual: {stat['avg_actual_value']:.2f}, Avg Line: {stat['avg_line']:.2f}")
            print(f"    Unique Players: {stat['unique_players']}")
        
        # Get recent stats
        recent = await conn.fetch("""
            SELECT * FROM player_stats 
            ORDER BY date DESC, created_at DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent Player Stats:")
        for stat in recent:
            print(f"  - {stat['player_name']} ({stat['team']} vs {stat['opponent']})")
            print(f"    {stat['stat_type']}: {stat['actual_value']} vs line {stat['line']}")
            print(f"    Result: {'HIT' if stat['result'] else 'MISS'}")
            print(f"    Date: {stat['date']}")
        
        # Get over/under performance
        over_under = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN actual_value > line THEN 'OVER'
                    WHEN actual_value < line THEN 'UNDER'
                    WHEN actual_value = line THEN 'PUSH'
                END as over_under_result,
                COUNT(*) as total_stats,
                COUNT(CASE WHEN result = true THEN 1 END) as hits,
                COUNT(CASE WHEN result = false THEN 1 END) as misses,
                ROUND(COUNT(CASE WHEN result = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage
            FROM player_stats
            WHERE line IS NOT NULL
            GROUP BY over_under_result
            ORDER BY hit_rate_percentage DESC
        """)
        
        print(f"\nOver/Under Performance:")
        for result in over_under:
            print(f"  {result['over_under_result']}:")
            print(f"    Total Stats: {result['total_stats']}")
            print(f"    Hit Rate: {result['hit_rate_percentage']:.2f}%")
            print(f"    Hits/Misses: {result['hits']}/{result['misses']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_player_stats())
