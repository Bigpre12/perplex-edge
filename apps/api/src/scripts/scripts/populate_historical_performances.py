#!/usr/bin/env python3
"""
POPULATE HISTORICAL PERFORMANCES - Initialize and populate the historical_performances table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_historical_performances():
    """Populate historical_performances table with initial data"""
    
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
                WHERE table_name = 'historical_performances'
            )
        """)
        
        if not table_check:
            print("Creating historical_performances table...")
            await conn.execute("""
                CREATE TABLE historical_performances (
                    id SERIAL PRIMARY KEY,
                    player_name VARCHAR(100) NOT NULL,
                    stat_type VARCHAR(50) NOT NULL,
                    total_picks INTEGER NOT NULL,
                    hits INTEGER NOT NULL,
                    misses INTEGER NOT NULL,
                    hit_rate_percentage DECIMAL(5, 2),
                    avg_ev DECIMAL(10, 4),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample historical performance data
        print("Generating sample historical performance data...")
        
        performances = [
            # Top performing players
            {
                'player_name': 'Patrick Mahomes',
                'stat_type': 'passing_yards',
                'total_picks': 156,
                'hits': 98,
                'misses': 58,
                'hit_rate_percentage': 62.82,
                'avg_ev': 0.0842,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Patrick Mahomes',
                'stat_type': 'passing_touchdowns',
                'total_picks': 89,
                'hits': 62,
                'misses': 27,
                'hit_rate_percentage': 69.66,
                'avg_ev': 0.0921,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Josh Allen',
                'stat_type': 'passing_yards',
                'total_picks': 142,
                'hits': 87,
                'misses': 55,
                'hit_rate_percentage': 61.27,
                'avg_ev': 0.0789,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Josh Allen',
                'stat_type': 'rushing_yards',
                'total_picks': 67,
                'hits': 41,
                'misses': 26,
                'hit_rate_percentage': 61.19,
                'avg_ev': 0.0815,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Lamar Jackson',
                'stat_type': 'passing_yards',
                'total_picks': 134,
                'hits': 79,
                'misses': 55,
                'hit_rate_percentage': 58.96,
                'avg_ev': 0.0723,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Lamar Jackson',
                'stat_type': 'rushing_yards',
                'total_picks': 98,
                'hits': 61,
                'misses': 37,
                'hit_rate_percentage': 62.24,
                'avg_ev': 0.0897,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            # NBA players
            {
                'player_name': 'LeBron James',
                'stat_type': 'points',
                'total_picks': 178,
                'hits': 112,
                'misses': 66,
                'hit_rate_percentage': 62.92,
                'avg_ev': 0.0768,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'LeBron James',
                'stat_type': 'rebounds',
                'total_picks': 145,
                'hits': 89,
                'misses': 56,
                'hit_rate_percentage': 61.38,
                'avg_ev': 0.0742,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Kevin Durant',
                'stat_type': 'points',
                'total_picks': 156,
                'hits': 98,
                'misses': 58,
                'hit_rate_percentage': 62.82,
                'avg_ev': 0.0811,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Stephen Curry',
                'stat_type': 'points',
                'total_picks': 189,
                'hits': 121,
                'misses': 68,
                'hit_rate_percentage': 64.02,
                'avg_ev': 0.0934,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Stephen Curry',
                'stat_type': 'three_pointers',
                'total_picks': 167,
                'hits': 103,
                'misses': 64,
                'hit_rate_percentage': 61.68,
                'avg_ev': 0.0889,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            # MLB players
            {
                'player_name': 'Aaron Judge',
                'stat_type': 'home_runs',
                'total_picks': 89,
                'hits': 56,
                'misses': 33,
                'hit_rate_percentage': 62.92,
                'avg_ev': 0.0912,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Aaron Judge',
                'stat_type': 'batting_average',
                'total_picks': 134,
                'hits': 83,
                'misses': 51,
                'hit_rate_percentage': 61.94,
                'avg_ev': 0.0787,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Shohei Ohtani',
                'stat_type': 'home_runs',
                'total_picks': 78,
                'hits': 48,
                'misses': 30,
                'hit_rate_percentage': 61.54,
                'avg_ev': 0.0834,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Shohei Ohtani',
                'stat_type': 'strikeouts',
                'total_picks': 92,
                'hits': 57,
                'misses': 35,
                'hit_rate_percentage': 61.96,
                'avg_ev': 0.0798,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            # System performances
            {
                'player_name': 'Brain System',
                'stat_type': 'overall_predictions',
                'total_picks': 1245,
                'hits': 789,
                'misses': 456,
                'hit_rate_percentage': 63.38,
                'avg_ev': 0.0823,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Brain System',
                'stat_type': 'nfl_predictions',
                'total_picks': 456,
                'hits': 289,
                'misses': 167,
                'hit_rate_percentage': 63.38,
                'avg_ev': 0.0845,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Brain System',
                'stat_type': 'nba_predictions',
                'total_picks': 523,
                'hits': 334,
                'misses': 189,
                'hit_rate_percentage': 63.86,
                'avg_ev': 0.0812,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Brain System',
                'stat_type': 'mlb_predictions',
                'total_picks': 266,
                'hits': 166,
                'misses': 100,
                'hit_rate_percentage': 62.41,
                'avg_ev': 0.0801,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            # Poor performing players (for contrast)
            {
                'player_name': 'Sam Darnold',
                'stat_type': 'passing_yards',
                'total_picks': 45,
                'hits': 22,
                'misses': 23,
                'hit_rate_percentage': 48.89,
                'avg_ev': -0.0234,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Russell Westbrook',
                'stat_type': 'field_goal_percentage',
                'total_picks': 67,
                'hits': 31,
                'misses': 36,
                'hit_rate_percentage': 46.27,
                'avg_ev': -0.0345,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'player_name': 'Mookie Betts',
                'stat_type': 'batting_average',
                'total_picks': 78,
                'hits': 36,
                'misses': 42,
                'hit_rate_percentage': 46.15,
                'avg_ev': -0.0289,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            }
        ]
        
        # Insert performance data
        for performance in performances:
            await conn.execute("""
                INSERT INTO historical_performances (
                    player_name, stat_type, total_picks, hits, misses, hit_rate_percentage,
                    avg_ev, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
                performance['player_name'],
                performance['stat_type'],
                performance['total_picks'],
                performance['hits'],
                performance['misses'],
                performance['hit_rate_percentage'],
                performance['avg_ev'],
                performance['created_at'],
                performance['updated_at']
            )
        
        print("Sample historical performance data populated successfully")
        
        # Get performance statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_performances,
                COUNT(DISTINCT player_name) as unique_players,
                COUNT(DISTINCT stat_type) as unique_stat_types,
                AVG(hit_rate_percentage) as avg_hit_rate,
                AVG(avg_ev) as avg_ev,
                SUM(total_picks) as total_picks_all,
                SUM(hits) as total_hits_all,
                SUM(misses) as total_misses_all
            FROM historical_performances
        """)
        
        print(f"\nHistorical Performance Statistics:")
        print(f"  Total Performances: {stats['total_performances']}")
        print(f"  Unique Players: {stats['unique_players']}")
        print(f"  Unique Stat Types: {stats['unique_stat_types']}")
        print(f"  Avg Hit Rate: {stats['avg_hit_rate']:.2f}%")
        print(f"  Avg EV: {stats['avg_ev']:.4f}")
        print(f"  Total Picks: {stats['total_picks_all']}")
        print(f"  Total Hits: {stats['total_hits_all']}")
        print(f"  Total Misses: {stats['total_misses_all']}")
        
        # Get top performers
        top_performers = await conn.fetch("""
            SELECT player_name, stat_type, hit_rate_percentage, avg_ev, total_picks
            FROM historical_performances
            ORDER BY hit_rate_percentage DESC
            LIMIT 10
        """)
        
        print(f"\nTop Performers by Hit Rate:")
        for performer in top_performers:
            print(f"  - {performer['player_name']} ({performer['stat_type']})")
            print(f"    Hit Rate: {performer['hit_rate_percentage']:.2f}%")
            print(f"    Avg EV: {performer['avg_ev']:.4f}")
            print(f"    Total Picks: {performer['total_picks']}")
        
        # Get best EV performers
        best_ev = await conn.fetch("""
            SELECT player_name, stat_type, hit_rate_percentage, avg_ev, total_picks
            FROM historical_performances
            ORDER BY avg_ev DESC
            LIMIT 10
        """)
        
        print(f"\nBest Performers by EV:")
        for performer in best_ev:
            print(f"  - {performer['player_name']} ({performer['stat_type']})")
            print(f"    Hit Rate: {performer['hit_rate_percentage']:.2f}%")
            print(f"    Avg EV: {performer['avg_ev']:.4f}")
            print(f"    Total Picks: {performer['total_picks']}")
        
        # Get worst performers
        worst_performers = await conn.fetch("""
            SELECT player_name, stat_type, hit_rate_percentage, avg_ev, total_picks
            FROM historical_performances
            ORDER BY hit_rate_percentage ASC
            LIMIT 5
        """)
        
        print(f"\nWorst Performers by Hit Rate:")
        for performer in worst_performers:
            print(f"  - {performer['player_name']} ({performer['stat_type']})")
            print(f"    Hit Rate: {performer['hit_rate_percentage']:.2f}%")
            print(f"    Avg EV: {performer['avg_ev']:.4f}")
            print(f"    Total Picks: {performer['total_picks']}")
        
        # Get by stat type breakdown
        stat_types = await conn.fetch("""
            SELECT 
                stat_type,
                COUNT(*) as total_performances,
                AVG(hit_rate_percentage) as avg_hit_rate,
                AVG(avg_ev) as avg_ev,
                SUM(total_picks) as total_picks,
                SUM(hits) as total_hits
            FROM historical_performances
            GROUP BY stat_type
            ORDER BY avg_hit_rate DESC
        """)
        
        print(f"\nPerformance by Stat Type:")
        for stat in stat_types:
            print(f"  - {stat['stat_type']}")
            print(f"    Total Performances: {stat['total_performances']}")
            print(f"    Avg Hit Rate: {stat['avg_hit_rate']:.2f}%")
            print(f"    Avg EV: {stat['avg_ev']:.4f}")
            print(f"    Total Picks: {stat['total_picks']}")
            print(f"    Total Hits: {stat['total_hits']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_historical_performances())
