#!/usr/bin/env python3
"""
POPULATE LIVE ODDS NCAAB - Initialize and populate the live_odds_ncaab table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_live_odds_ncaab():
    """Populate live_odds_ncaab table with initial data"""
    
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
                WHERE table_name = 'live_odds_ncaab'
            )
        """)
        
        if not table_check:
            print("Creating live_odds_ncaab table...")
            await conn.execute("""
                CREATE TABLE live_odds_ncaab (
                    id SERIAL PRIMARY KEY,
                    sport INTEGER NOT NULL,
                    game_id INTEGER NOT NULL,
                    home_team VARCHAR(100) NOT NULL,
                    away_team VARCHAR(100) NOT NULL,
                    home_odds INTEGER,
                    away_odds INTEGER,
                    draw_odds INTEGER,
                    bookmaker VARCHAR(50) NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    season INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample live NCAA basketball odds data
        print("Generating sample live NCAA basketball odds data...")
        
        live_odds = [
            # Duke vs North Carolina - Rivalry Game
            {
                'sport': 32,  # NCAA Basketball
                'game_id': 1001,
                'home_team': 'Duke Blue Devils',
                'away_team': 'North Carolina Tar Heels',
                'home_odds': -145,
                'away_odds': 125,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=30),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'sport': 32,
                'game_id': 1001,
                'home_team': 'Duke Blue Devils',
                'away_team': 'North Carolina Tar Heels',
                'home_odds': -140,
                'away_odds': 120,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=30),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'sport': 32,
                'game_id': 1001,
                'home_team': 'Duke Blue Devils',
                'away_team': 'North Carolina Tar Heels',
                'home_odds': -150,
                'away_odds': 130,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=30),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            # Kansas vs Kentucky - Blue Blood Matchup
            {
                'sport': 32,
                'game_id': 1002,
                'home_team': 'Kansas Jayhawks',
                'away_team': 'Kentucky Wildcats',
                'home_odds': -110,
                'away_odds': -110,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=25),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=25)
            },
            {
                'sport': 32,
                'game_id': 1002,
                'home_team': 'Kansas Jayhawks',
                'away_team': 'Kentucky Wildcats',
                'home_odds': -105,
                'away_odds': -115,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=25),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=25)
            },
            {
                'sport': 32,
                'game_id': 1002,
                'home_team': 'Kansas Jayhawks',
                'away_team': 'Kentucky Wildcats',
                'home_odds': -115,
                'away_odds': -105,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=25),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=25)
            },
            # UCLA vs Gonzaga - West Coast Powerhouse
            {
                'sport': 32,
                'game_id': 1003,
                'home_team': 'UCLA Bruins',
                'away_team': 'Gonzaga Bulldogs',
                'home_odds': 180,
                'away_odds': -220,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=20),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=20)
            },
            {
                'sport': 32,
                'game_id': 1003,
                'home_team': 'UCLA Bruins',
                'away_team': 'Gonzaga Bulldogs',
                'home_odds': 175,
                'away_odds': -215,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=20),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=20)
            },
            {
                'sport': 32,
                'game_id': 1003,
                'home_team': 'UCLA Bruins',
                'away_team': 'Gonzaga Bulldogs',
                'home_odds': 190,
                'away_odds': -230,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=20),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=20)
            },
            # Michigan vs Ohio State - Big Ten Rivalry
            {
                'sport': 32,
                'game_id': 1004,
                'home_team': 'Michigan Wolverines',
                'away_team': 'Ohio State Buckeyes',
                'home_odds': -125,
                'away_odds': 105,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=15),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=15)
            },
            {
                'sport': 32,
                'game_id': 1004,
                'home_team': 'Michigan Wolverines',
                'away_team': 'Ohio State Buckeyes',
                'home_odds': -130,
                'away_odds': 110,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=15),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=15)
            },
            {
                'sport': 32,
                'game_id': 1004,
                'home_team': 'Michigan Wolverines',
                'away_team': 'Ohio State Buckeyes',
                'home_odds': -120,
                'away_odds': 100,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=15),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=15)
            },
            # Arizona vs Oregon - Pac-12 Matchup
            {
                'sport': 32,
                'game_id': 1005,
                'home_team': 'Arizona Wildcats',
                'away_team': 'Oregon Ducks',
                'home_odds': -105,
                'away_odds': -115,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=10),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=10)
            },
            {
                'sport': 32,
                'game_id': 1005,
                'home_team': 'Arizona Wildcats',
                'away_team': 'Oregon Ducks',
                'home_odds': -100,
                'away_odds': -120,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=10),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=10)
            },
            {
                'sport': 32,
                'game_id': 1005,
                'home_team': 'Arizona Wildcats',
                'away_team': 'Oregon Ducks',
                'home_odds': -110,
                'away_odds': -110,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=10),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=10)
            },
            # Purdue vs Indiana - Big Ten Rivalry
            {
                'sport': 32,
                'game_id': 1006,
                'home_team': 'Purdue Boilermakers',
                'away_team': 'Indiana Hoosiers',
                'home_odds': -200,
                'away_odds': 170,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=5),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=5)
            },
            {
                'sport': 32,
                'game_id': 1006,
                'home_team': 'Purdue Boilermakers',
                'away_team': 'Indiana Hoosiers',
                'home_odds': -210,
                'away_odds': 175,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=5),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=5)
            },
            {
                'sport': 32,
                'game_id': 1006,
                'home_team': 'Purdue Boilermakers',
                'away_team': 'Indiana Hoosiers',
                'home_odds': -195,
                'away_odds': 165,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=5),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=5)
            },
            # Texas vs Baylor - Big 12 Matchup
            {
                'sport': 32,
                'game_id': 1007,
                'home_team': 'Texas Longhorns',
                'away_team': 'Baylor Bears',
                'home_odds': -140,
                'away_odds': 120,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=2),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=2)
            },
            {
                'sport': 32,
                'game_id': 1007,
                'home_team': 'Texas Longhorns',
                'away_team': 'Baylor Bears',
                'home_odds': -135,
                'away_odds': 115,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=2),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=2)
            },
            {
                'sport': 32,
                'game_id': 1007,
                'home_team': 'Texas Longhorns',
                'away_team': 'Baylor Bears',
                'home_odds': -145,
                'away_odds': 125,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=2),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=2)
            },
            # Villanova vs UConn - Big East vs Big East
            {
                'sport': 32,
                'game_id': 1008,
                'home_team': 'Villanova Wildcats',
                'away_team': 'UConn Huskies',
                'home_odds': 250,
                'away_odds': -300,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=1),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=1)
            },
            {
                'sport': 32,
                'game_id': 1008,
                'home_team': 'Villanova Wildcats',
                'away_team': 'UConn Huskies',
                'home_odds': 240,
                'away_odds': -290,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=1),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=1)
            },
            {
                'sport': 32,
                'game_id': 1008,
                'home_team': 'Villanova Wildcats',
                'away_team': 'UConn Huskies',
                'home_odds': 260,
                'away_odds': -320,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=1),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=1)
            },
            # Recent line movements (showing real-time updates)
            {
                'sport': 32,
                'game_id': 1001,
                'home_team': 'Duke Blue Devils',
                'away_team': 'North Carolina Tar Heels',
                'home_odds': -138,
                'away_odds': 118,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(seconds=30),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(seconds=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(seconds=30)
            },
            {
                'sport': 32,
                'game_id': 1001,
                'home_team': 'Duke Blue Devils',
                'away_team': 'North Carolina Tar Heels',
                'home_odds': -142,
                'away_odds': 122,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(seconds=15),
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(seconds=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(seconds=15)
            },
            {
                'sport': 32,
                'game_id': 1001,
                'home_team': 'Duke Blue Devils',
                'away_team': 'North Carolina Tar Heels',
                'home_odds': -140,
                'away_odds': 120,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc),
                'season': 2026,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
        ]
        
        # Insert live odds data
        for odds in live_odds:
            await conn.execute("""
                INSERT INTO live_odds_ncaab (
                    sport, game_id, home_team, away_team, home_odds, away_odds, draw_odds,
                    bookmaker, timestamp, season, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """, 
                odds['sport'],
                odds['game_id'],
                odds['home_team'],
                odds['away_team'],
                odds['home_odds'],
                odds['away_odds'],
                odds['draw_odds'],
                odds['bookmaker'],
                odds['timestamp'],
                odds['season'],
                odds['created_at'],
                odds['updated_at']
            )
        
        print("Sample live odds data populated successfully")
        
        # Get live odds statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_odds,
                COUNT(DISTINCT game_id) as unique_games,
                COUNT(DISTINCT home_team) as unique_teams,
                COUNT(DISTINCT away_team) as unique_opponents,
                COUNT(DISTINCT bookmaker) as unique_bookmakers,
                AVG(home_odds) as avg_home_odds,
                AVG(away_odds) as avg_away_odds,
                COUNT(CASE WHEN home_odds < 0 THEN 1 END) as home_favorites,
                COUNT(CASE WHEN away_odds < 0 THEN 1 END) as away_favorites,
                COUNT(CASE WHEN draw_odds IS NOT NULL THEN 1 END) as draw_markets
            FROM live_odds_ncaab
        """)
        
        print(f"\nLive Odds Statistics:")
        print(f"  Total Odds: {stats['total_odds']}")
        print(f"  Unique Games: {stats['unique_games']}")
        print(f"  Unique Teams: {stats['unique_teams']}")
        print(f"  Unique Opponents: {stats['unique_opponents']}")
        print(f" Unique Bookmakers: {stats['unique_bookmakers']}")
        print(f"  Avg Home Odds: {stats['avg_home_odds']:.0f}")
        print(f"  Avg Away Odds: {stats['avg_away_odds']:.0f}")
        print(f"  Home Favorites: {stats['home_favorites']}")
        print(f"  Away Favorites: {stats['away_favorites']}")
        print(f"  Draw Markets: {stats['draw_markets']}")
        
        # Get odds by sportsbook
        by_bookmaker = await conn.fetch("""
            SELECT 
                bookmaker,
                COUNT(*) as total_odds,
                COUNT(DISTINCT game_id) as unique_games,
                AVG(home_odds) as avg_home_odds,
                AVG(away_odds) as avg_away_odds,
                COUNT(CASE WHEN home_odds < 0 THEN 1 END) as home_favorites,
                COUNT(CASE WHEN away_odds < 0 THEN 1 END) as away_favorites
            FROM live_odds_ncaab
            GROUP BY bookmaker
            ORDER BY total_odds DESC
        """)
        
        print(f"\nOdds by Sportsbook:")
        for bookmaker in by_bookmaker:
            print(f"  {bookmaker}:")
            print(f"    Total Odds: {bookmaker['total_odds']}")
            print(f"    Unique Games: {bookmaker['unique_games']}")
            print(f"    Avg Home Odds: {bookmaker['avg_home_odds']:.0f}")
            print(f"    Avg Away Odds: {bookmaker['avg_away_odds']:.0f}")
            print(f"    Home Favorites: {bookmaker['home_favorites']}")
            print(f"    Away Favorites: {bookmaker['away_favorites']}")
        
        # Get recent odds
        recent = await conn.fetch("""
            SELECT * FROM live_odds_ncaab 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent Odds:")
        for odds in recent:
            print(f"  - {odds['home_team']} vs {odds['away_team']}")
            print(f"    {odds['bookmaker']}: {odds['home_odds']} / {odds['away_odds']}")
            print(f"    Timestamp: {odds['timestamp']}")
        
        # Get games with most odds movement potential
        games_with_movement = await conn.fetch("""
            SELECT 
                game_id,
                home_team,
                away_team,
                COUNT(*) as total_odds,
                COUNT(DISTINCT bookmaker) as bookmakers,
                MIN(home_odds) as best_home_odds,
                MAX(home_odds) as worst_home_odds,
                MIN(away_odds) as best_away_odds,
                MAX(away_odds) as worst_away_odds
            FROM live_odds_ncaab
            GROUP BY game_id, home_team, away_team
            HAVING COUNT(*) >= 3
            ORDER BY (MAX(home_odds) - MIN(home_odds)) DESC
            LIMIT 5
        """)
        
        print(f"\nGames with Most Odds Movement Potential:")
        for game in games_with_movement:
            print(f"  - {game['home_team']} vs {game['away_team']}")
            print(f"    Total Odds: {game['total_odds']}")
            print(f"    Bookmakers: {game['bookmakers']}")
            print(f"    Home Odds Range: {game['worst_home_odds']} to {game['best_home_odds']}")
            print(f"    Away Odds Range: {game['worst_away_odds']} to {game['best_away_odds']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_live_odds())
