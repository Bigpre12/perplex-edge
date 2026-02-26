#!/usr/bin/env python3
"""
POPULATE HISTORICAL ODDS NCAAB - Initialize and populate the historical_odds_ncaab table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_historical_odds_ncaab():
    """Populate historical_odds_ncaab table with initial data"""
    
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
                WHERE table_name = 'historical_odds_ncaab'
            )
        """)
        
        if not table_check:
            print("Creating historical_odds_ncaab table...")
            await conn.execute("""
                CREATE TABLE historical_odds_ncaab (
                    id SERIAL PRIMARY KEY,
                    sport INTEGER NOT NULL,
                    game_id INTEGER NOT NULL,
                    home_team VARCHAR(100) NOT NULL,
                    away_team VARCHAR(100) NOT NULL,
                    home_odds DECIMAL(10, 2),
                    away_odds DECIMAL(10, 2),
                    draw_odds DECIMAL(10, 2),
                    bookmaker VARCHAR(50) NOT NULL,
                    snapshot_date TIMESTAMP WITH TIME ZONE NOT NULL,
                    result VARCHAR(20),
                    season INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample NCAA basketball historical odds data
        print("Generating sample NCAA basketball historical odds data...")
        
        # Bookmakers
        bookmakers = ['DraftKings', 'FanDuel', 'BetMGM', 'Caesars', 'PointsBet', 'Bet365']
        
        # NCAA Basketball games with odds
        games_odds = [
            # Duke vs North Carolina rivalry
            {
                'sport': 32,  # NCAA Basketball
                'game_id': 1001,
                'home_team': 'Duke Blue Devils',
                'away_team': 'North Carolina Tar Heels',
                'odds_snapshots': [
                    {
                        'home_odds': -150,
                        'away_odds': 130,
                        'draw_odds': None,
                        'bookmaker': 'DraftKings',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=7, hours=12),
                        'result': 'home_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -145,
                        'away_odds': 125,
                        'draw_odds': None,
                        'bookmaker': 'FanDuel',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=7, hours=12),
                        'result': 'home_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -155,
                        'away_odds': 135,
                        'draw_odds': None,
                        'bookmaker': 'BetMGM',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=7, hours=12),
                        'result': 'home_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -140,
                        'away_odds': 120,
                        'draw_odds': None,
                        'bookmaker': 'DraftKings',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=7, hours=6),
                        'result': 'home_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -160,
                        'away_odds': 140,
                        'draw_odds': None,
                        'bookmaker': 'FanDuel',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=7, hours=6),
                        'result': 'home_win',
                        'season': 2026
                    }
                ]
            },
            # Kansas vs Kentucky
            {
                'sport': 32,
                'game_id': 1002,
                'home_team': 'Kansas Jayhawks',
                'away_team': 'Kentucky Wildcats',
                'odds_snapshots': [
                    {
                        'home_odds': -110,
                        'away_odds': -110,
                        'draw_odds': None,
                        'bookmaker': 'DraftKings',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=6, hours=12),
                        'result': 'home_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -105,
                        'away_odds': -115,
                        'draw_odds': None,
                        'bookmaker': 'FanDuel',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=6, hours=12),
                        'result': 'home_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -120,
                        'away_odds': 100,
                        'draw_odds': None,
                        'bookmaker': 'BetMGM',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=6, hours=12),
                        'result': 'home_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -115,
                        'away_odds': -105,
                        'draw_odds': None,
                        'bookmaker': 'Caesars',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=6, hours=6),
                        'result': 'home_win',
                        'season': 2026
                    }
                ]
            },
            # UCLA vs Gonzaga
            {
                'sport': 32,
                'game_id': 1003,
                'home_team': 'UCLA Bruins',
                'away_team': 'Gonzaga Bulldogs',
                'odds_snapshots': [
                    {
                        'home_odds': 180,
                        'away_odds': -220,
                        'draw_odds': None,
                        'bookmaker': 'DraftKings',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=5, hours=12),
                        'result': 'away_win',
                        'season': 2026
                    },
                    {
                        'home_odds': 175,
                        'away_odds': -215,
                        'draw_odds': None,
                        'bookmaker': 'FanDuel',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=5, hours=12),
                        'result': 'away_win',
                        'season': 2026
                    },
                    {
                        'home_odds': 190,
                        'away_odds': -230,
                        'draw_odds': None,
                        'bookmaker': 'BetMGM',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=5, hours=12),
                        'result': 'away_win',
                        'season': 2026
                    },
                    {
                        'home_odds': 170,
                        'away_odds': -210,
                        'draw_odds': None,
                        'bookmaker': 'PointsBet',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=5, hours=6),
                        'result': 'away_win',
                        'season': 2026
                    }
                ]
            },
            # Michigan vs Ohio State
            {
                'sport': 32,
                'game_id': 1004,
                'home_team': 'Michigan Wolverines',
                'away_team': 'Ohio State Buckeyes',
                'odds_snapshots': [
                    {
                        'home_odds': -125,
                        'away_odds': 105,
                        'draw_odds': None,
                        'bookmaker': 'DraftKings',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=4, hours=12),
                        'result': 'home_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -130,
                        'away_odds': 110,
                        'draw_odds': None,
                        'bookmaker': 'FanDuel',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=4, hours=12),
                        'result': 'home_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -120,
                        'away_odds': 100,
                        'draw_odds': None,
                        'bookmaker': 'Bet365',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=4, hours=12),
                        'result': 'home_win',
                        'season': 2026
                    }
                ]
            },
            # Arizona vs Oregon
            {
                'sport': 32,
                'game_id': 1005,
                'home_team': 'Arizona Wildcats',
                'away_team': 'Oregon Ducks',
                'odds_snapshots': [
                    {
                        'home_odds': -105,
                        'away_odds': -115,
                        'draw_odds': None,
                        'bookmaker': 'DraftKings',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=3, hours=12),
                        'result': 'away_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -100,
                        'away_odds': -120,
                        'draw_odds': None,
                        'bookmaker': 'FanDuel',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=3, hours=12),
                        'result': 'away_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -110,
                        'away_odds': -110,
                        'draw_odds': None,
                        'bookmaker': 'BetMGM',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=3, hours=12),
                        'result': 'away_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -95,
                        'away_odds': -125,
                        'draw_odds': None,
                        'bookmaker': 'Caesars',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=3, hours=6),
                        'result': 'away_win',
                        'season': 2026
                    }
                ]
            },
            # Purdue vs Indiana
            {
                'sport': 32,
                'game_id': 1006,
                'home_team': 'Purdue Boilermakers',
                'away_team': 'Indiana Hoosiers',
                'odds_snapshots': [
                    {
                        'home_odds': -200,
                        'away_odds': 170,
                        'draw_odds': None,
                        'bookmaker': 'DraftKings',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=2, hours=12),
                        'result': 'home_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -210,
                        'away_odds': 175,
                        'draw_odds': None,
                        'bookmaker': 'FanDuel',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=2, hours=12),
                        'result': 'home_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -195,
                        'away_odds': 165,
                        'draw_odds': None,
                        'bookmaker': 'BetMGM',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=2, hours=12),
                        'result': 'home_win',
                        'season': 2026
                    }
                ]
            },
            # Texas vs Baylor
            {
                'sport': 32,
                'game_id': 1007,
                'home_team': 'Texas Longhorns',
                'away_team': 'Baylor Bears',
                'odds_snapshots': [
                    {
                        'home_odds': -140,
                        'away_odds': 120,
                        'draw_odds': None,
                        'bookmaker': 'DraftKings',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=1, hours=12),
                        'result': 'home_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -135,
                        'away_odds': 115,
                        'draw_odds': None,
                        'bookmaker': 'FanDuel',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=1, hours=12),
                        'result': 'home_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -145,
                        'away_odds': 125,
                        'draw_odds': None,
                        'bookmaker': 'PointsBet',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=1, hours=12),
                        'result': 'home_win',
                        'season': 2026
                    },
                    {
                        'home_odds': -130,
                        'away_odds': 110,
                        'draw_odds': None,
                        'bookmaker': 'Bet365',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(days=1, hours=6),
                        'result': 'home_win',
                        'season': 2026
                    }
                ]
            },
            # Villanova vs UConn
            {
                'sport': 32,
                'game_id': 1008,
                'home_team': 'Villanova Wildcats',
                'away_team': 'UConn Huskies',
                'odds_snapshots': [
                    {
                        'home_odds': 250,
                        'away_odds': -300,
                        'draw_odds': None,
                        'bookmaker': 'DraftKings',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(hours=12),
                        'result': 'away_win',
                        'season': 2026
                    },
                    {
                        'home_odds': 240,
                        'away_odds': -290,
                        'draw_odds': None,
                        'bookmaker': 'FanDuel',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(hours=12),
                        'result': 'away_win',
                        'season': 2026
                    },
                    {
                        'home_odds': 260,
                        'away_odds': -320,
                        'draw_odds': None,
                        'bookmaker': 'BetMGM',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(hours=12),
                        'result': 'away_win',
                        'season': 2026
                    },
                    {
                        'home_odds': 235,
                        'away_odds': -285,
                        'draw_odds': None,
                        'bookmaker': 'Caesars',
                        'snapshot_date': datetime.now(timezone.utc) - timedelta(hours=6),
                        'result': 'away_win',
                        'season': 2026
                    }
                ]
            }
        ]
        
        # Insert odds data
        for game in games_odds:
            for snapshot in game['odds_snapshots']:
                await conn.execute("""
                    INSERT INTO historical_odds_ncaab (
                        sport, game_id, home_team, away_team, home_odds, away_odds, draw_odds,
                        bookmaker, snapshot_date, result, season, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """, 
                    game['sport'],
                    game['game_id'],
                    game['home_team'],
                    game['away_team'],
                    snapshot['home_odds'],
                    snapshot['away_odds'],
                    snapshot['draw_odds'],
                    snapshot['bookmaker'],
                    snapshot['snapshot_date'],
                    snapshot['result'],
                    snapshot['season'],
                    snapshot['snapshot_date'],
                    snapshot['snapshot_date']
                )
        
        print("Sample NCAA basketball historical odds data populated successfully")
        
        # Get odds statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_odds,
                COUNT(DISTINCT game_id) as unique_games,
                COUNT(DISTINCT bookmaker) as unique_bookmakers,
                COUNT(DISTINCT home_team) as unique_teams,
                COUNT(CASE WHEN result = 'home_win' THEN 1 END) as home_wins,
                COUNT(CASE WHEN result = 'away_win' THEN 1 END) as away_wins,
                COUNT(CASE WHEN result IS NULL THEN 1 END) as pending_games,
                AVG(home_odds) as avg_home_odds,
                AVG(away_odds) as avg_away_odds
            FROM historical_odds_ncaab
        """)
        
        print(f"\nHistorical Odds Statistics:")
        print(f"  Total Odds Records: {stats['total_odds']}")
        print(f"  Unique Games: {stats['unique_games']}")
        print(f"  Unique Bookmakers: {stats['unique_bookmakers']}")
        print(f"  Unique Teams: {stats['unique_teams']}")
        print(f"  Home Wins: {stats['home_wins']}")
        print(f"  Away Wins: {stats['away_wins']}")
        print(f"  Pending Games: {stats['pending_games']}")
        print(f"  Avg Home Odds: {stats['avg_home_odds']:.2f}")
        print(f"  Avg Away Odds: {stats['avg_away_odds']:.2f}")
        
        # Get bookmaker breakdown
        bookmakers = await conn.fetch("""
            SELECT 
                bookmaker,
                COUNT(*) as total_odds,
                COUNT(DISTINCT game_id) as unique_games,
                COUNT(CASE WHEN result = 'home_win' THEN 1 END) as home_wins,
                COUNT(CASE WHEN result = 'away_win' THEN 1 END) as away_wins,
                AVG(home_odds) as avg_home_odds,
                AVG(away_odds) as avg_away_odds
            FROM historical_odds_ncaab
            GROUP BY bookmaker
            ORDER BY total_odds DESC
        """)
        
        print(f"\nBookmaker Breakdown:")
        for bookmaker in bookmakers:
            print(f"  {bookmaker['bookmaker']}:")
            print(f"    Total Odds: {bookmaker['total_odds']}")
            print(f"    Unique Games: {bookmaker['unique_games']}")
            print(f"    Home Wins: {bookmaker['home_wins']}")
            print(f"    Away Wins: {bookmaker['away_wins']}")
            print(f"    Avg Home Odds: {bookmaker['avg_home_odds']:.2f}")
            print(f"    Avg Away Odds: {bookmaker['avg_away_odds']:.2f}")
        
        # Get recent odds
        recent = await conn.fetch("""
            SELECT * FROM historical_odds_ncaab 
            ORDER BY snapshot_date DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent Odds:")
        for odds in recent:
            print(f"  - {odds['home_team']} vs {odds['away_team']}")
            print(f"    Home: {odds['home_odds']}, Away: {odds['away_odds']}")
            print(f"    Bookmaker: {odds['bookmaker']}, Result: {odds['result']}")
            print(f"    Snapshot: {odds['snapshot_date']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_historical_odds_ncaab())
