#!/usr/bin/env python3
"""
POPULATE LIVE ODDS NFL - Initialize and populate the live_odds_nfl table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_live_odds_nfl():
    """Populate live_odds_nfl table with initial data"""
    
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
                WHERE table_name = 'live_odds_nfl'
            )
        """)
        
        if not table_check:
            print("Creating live_odds_nfl table...")
            await conn.execute("""
                CREATE TABLE live_odds_nfl (
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
                    week INTEGER,
                    season INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample live NFL odds data
        print("Generating sample live NFL odds data...")
        
        live_odds = [
            # Chiefs vs Bills - AFC Championship Game
            {
                'sport': 1,  # NFL
                'game_id': 2001,
                'home_team': 'Kansas City Chiefs',
                'away_team': 'Buffalo Bills',
                'home_odds': -165,
                'away_odds': 145,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=30),
                'week': 20,  # Playoffs
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'sport': 1,
                'game_id': 2001,
                'home_team': 'Kansas City Chiefs',
                'away_team': 'Buffalo Bills',
                'home_odds': -160,
                'away_odds': 140,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=30),
                'week': 20,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'sport': 1,
                'game_id': 2001,
                'home_team': 'Kansas City Chiefs',
                'away_team': 'Buffalo Bills',
                'home_odds': -170,
                'away_odds': 150,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=30),
                'week': 20,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            # 49ers vs Eagles - NFC Championship Game
            {
                'sport': 1,
                'game_id': 2002,
                'home_team': 'San Francisco 49ers',
                'away_team': 'Philadelphia Eagles',
                'home_odds': -125,
                'away_odds': 105,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=25),
                'week': 20,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=25)
            },
            {
                'sport': 1,
                'game_id': 2002,
                'home_team': 'San Francisco 49ers',
                'away_team': 'Philadelphia Eagles',
                'home_odds': -130,
                'away_odds': 110,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=25),
                'week': 20,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=25)
            },
            {
                'sport': 1,
                'game_id': 2002,
                'home_team': 'San Francisco 49ers',
                'away_team': 'Philadelphia Eagles',
                'home_odds': -120,
                'away_odds': 100,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=25),
                'week': 20,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=25)
            },
            # Cowboys vs Giants - NFC East Rivalry
            {
                'sport': 1,
                'game_id': 2003,
                'home_team': 'Dallas Cowboys',
                'away_team': 'New York Giants',
                'home_odds': -280,
                'away_odds': 230,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=20),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=20)
            },
            {
                'sport': 1,
                'game_id': 2003,
                'home_team': 'Dallas Cowboys',
                'away_team': 'New York Giants',
                'home_odds': -275,
                'away_odds': 225,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=20),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=20)
            },
            {
                'sport': 1,
                'game_id': 2003,
                'home_team': 'Dallas Cowboys',
                'away_team': 'New York Giants',
                'home_odds': -285,
                'away_odds': 235,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=20),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=20)
            },
            # Packers vs Bears - NFC North Rivalry
            {
                'sport': 1,
                'game_id': 2004,
                'home_team': 'Green Bay Packers',
                'away_team': 'Chicago Bears',
                'home_odds': -190,
                'away_odds': 160,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=15),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=15)
            },
            {
                'sport': 1,
                'game_id': 2004,
                'home_team': 'Green Bay Packers',
                'away_team': 'Chicago Bears',
                'home_odds': -185,
                'away_odds': 155,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=15),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=15)
            },
            {
                'sport': 1,
                'game_id': 2004,
                'home_team': 'Green Bay Packers',
                'away_team': 'Chicago Bears',
                'home_odds': -195,
                'away_odds': 165,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=15),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=15)
            },
            # Patriots vs Jets - AFC East Rivalry
            {
                'sport': 1,
                'game_id': 2005,
                'home_team': 'New England Patriots',
                'away_team': 'New York Jets',
                'home_odds': -140,
                'away_odds': 120,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=10),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=10)
            },
            {
                'sport': 1,
                'game_id': 2005,
                'home_team': 'New England Patriots',
                'away_team': 'New York Jets',
                'home_odds': -135,
                'away_odds': 115,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=10),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=10)
            },
            {
                'sport': 1,
                'game_id': 2005,
                'home_team': 'New England Patriots',
                'away_team': 'New York Jets',
                'home_odds': -145,
                'away_odds': 125,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=10),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=10)
            },
            # Ravens vs Steelers - AFC North Rivalry
            {
                'sport': 1,
                'game_id': 2006,
                'home_team': 'Baltimore Ravens',
                'away_team': 'Pittsburgh Steelers',
                'home_odds': -155,
                'away_odds': 135,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=5),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=5)
            },
            {
                'sport': 1,
                'game_id': 2006,
                'home_team': 'Baltimore Ravens',
                'away_team': 'Pittsburgh Steelers',
                'home_odds': -150,
                'away_odds': 130,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=5),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=5)
            },
            {
                'sport': 1,
                'game_id': 2006,
                'home_team': 'Baltimore Ravens',
                'away_team': 'Pittsburgh Steelers',
                'home_odds': -160,
                'away_odds': 140,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=5),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=5)
            },
            # Bengals vs Browns - AFC North Rivalry
            {
                'sport': 1,
                'game_id': 2007,
                'home_team': 'Cincinnati Bengals',
                'away_team': 'Cleveland Browns',
                'home_odds': -110,
                'away_odds': -110,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=2),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=2)
            },
            {
                'sport': 1,
                'game_id': 2007,
                'home_team': 'Cincinnati Bengals',
                'away_team': 'Cleveland Browns',
                'home_odds': -105,
                'away_odds': -115,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=2),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=2)
            },
            {
                'sport': 1,
                'game_id': 2007,
                'home_team': 'Cincinnati Bengals',
                'away_team': 'Cleveland Browns',
                'home_odds': -115,
                'away_odds': -105,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=2),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=2)
            },
            # Seahawks vs 49ers - NFC West Rivalry
            {
                'sport': 1,
                'game_id': 2008,
                'home_team': 'Seattle Seahawks',
                'away_team': 'San Francisco 49ers',
                'home_odds': 320,
                'away_odds': -400,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=1),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=1)
            },
            {
                'sport': 1,
                'game_id': 2008,
                'home_team': 'Seattle Seahawks',
                'away_team': 'San Francisco 49ers',
                'home_odds': 310,
                'away_odds': -390,
                'draw_odds': None,
                'bookmaker': 'FanDuel',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=1),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=1)
            },
            {
                'sport': 1,
                'game_id': 2008,
                'home_team': 'Seattle Seahawks',
                'away_team': 'San Francisco 49ers',
                'home_odds': 330,
                'away_odds': -410,
                'draw_odds': None,
                'bookmaker': 'BetMGM',
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=1),
                'week': 18,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=1)
            },
            # Recent line movements (showing real-time updates)
            {
                'sport': 1,
                'game_id': 2001,
                'home_team': 'Kansas City Chiefs',
                'away_team': 'Buffalo Bills',
                'home_odds': -162,
                'away_odds': 142,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(seconds=30),
                'week': 20,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(seconds=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(seconds=30)
            },
            {
                'sport': 1,
                'game_id': 2001,
                'home_team': 'Kansas City Chiefs',
                'away_team': 'Buffalo Bills',
                'home_odds': -168,
                'away_odds': 148,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc) - timedelta(seconds=15),
                'week': 20,
                'season': 2026,
                'created_at': datetime.now(timezone.utc) - timedelta(seconds=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(seconds=15)
            },
            {
                'sport': 1,
                'game_id': 2001,
                'home_team': 'Kansas City Chiefs',
                'away_team': 'Buffalo Bills',
                'home_odds': -165,
                'away_odds': 145,
                'draw_odds': None,
                'bookmaker': 'DraftKings',
                'timestamp': datetime.now(timezone.utc),
                'week': 20,
                'season': 2026,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
        ]
        
        # Insert live odds data
        for odds in live_odds:
            await conn.execute("""
                INSERT INTO live_odds_nfl (
                    sport, game_id, home_team, away_team, home_odds, away_odds, draw_odds,
                    bookmaker, timestamp, week, season, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
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
                odds['week'],
                odds['season'],
                odds['created_at'],
                odds['updated_at']
            )
        
        print("Sample live NFL odds data populated successfully")
        
        # Get live odds statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_odds,
                COUNT(DISTINCT game_id) as unique_games,
                COUNT(DISTINCT home_team) as unique_teams,
                COUNT(DISTINCT away_team) as unique_opponents,
                COUNT(DISTINCT bookmaker) as unique_bookmakers,
                COUNT(DISTINCT week) as unique_weeks,
                AVG(home_odds) as avg_home_odds,
                AVG(away_odds) as avg_away_odds,
                COUNT(CASE WHEN home_odds < 0 THEN 1 END) as home_favorites,
                COUNT(CASE WHEN away_odds < 0 THEN 1 END) as away_favorites,
                COUNT(CASE WHEN draw_odds IS NOT NULL THEN 1 END) as draw_markets
            FROM live_odds_nfl
        """)
        
        print(f"\nLive NFL Odds Statistics:")
        print(f"  Total Odds: {stats['total_odds']}")
        print(f"  Unique Games: {stats['unique_games']}")
        print(f"  Unique Teams: {stats['unique_teams']}")
        print(f"  Unique Opponents: {stats['unique_opponents']}")
        print(f"  Unique Bookmakers: {stats['unique_bookmakers']}")
        print(f"  Unique Weeks: {stats['unique_weeks']}")
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
                COUNT(DISTINCT week) as unique_weeks,
                AVG(home_odds) as avg_home_odds,
                AVG(away_odds) as avg_away_odds,
                COUNT(CASE WHEN home_odds < 0 THEN 1 END) as home_favorites,
                COUNT(CASE WHEN away_odds < 0 THEN 1 END) as away_favorites
            FROM live_odds_nfl
            GROUP BY bookmaker
            ORDER BY total_odds DESC
        """)
        
        print(f"\nOdds by Sportsbook:")
        for bookmaker in by_bookmaker:
            print(f"  {bookmaker}:")
            print(f"    Total Odds: {bookmaker['total_odds']}")
            print(f"    Unique Games: {bookmaker['unique_games']}")
            print(f"    Unique Weeks: {bookmaker['unique_weeks']}")
            print(f"    Avg Home Odds: {bookmaker['avg_home_odds']:.0f}")
            print(f"    Avg Away Odds: {bookmaker['avg_away_odds']:.0f}")
            print(f"    Home Favorites: {bookmaker['home_favorites']}")
            print(f"    Away Favorites: {bookmaker['away_favorites']}")
        
        # Get recent odds
        recent = await conn.fetch("""
            SELECT * FROM live_odds_nfl 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent Odds:")
        for odds in recent:
            print(f"  - {odds['home_team']} vs {odds['away_team']}")
            print(f"    {odds['bookmaker']}: {odds['home_odds']} / {odds['away_odds']}")
            print(f"    Week {odds['week']}, Timestamp: {odds['timestamp']}")
        
        # Get games with most odds movement potential
        games_with_movement = await conn.fetch("""
            SELECT 
                game_id,
                home_team,
                away_team,
                week,
                COUNT(*) as total_odds,
                COUNT(DISTINCT bookmaker) as bookmakers,
                MIN(home_odds) as best_home_odds,
                MAX(home_odds) as worst_home_odds,
                MIN(away_odds) as best_away_odds,
                MAX(away_odds) as worst_away_odds
            FROM live_odds_nfl
            GROUP BY game_id, home_team, away_team, week
            HAVING COUNT(*) >= 3
            ORDER BY (MAX(home_odds) - MIN(home_odds)) DESC
            LIMIT 5
        """)
        
        print(f"\nGames with Most Odds Movement Potential:")
        for game in games_with_movement:
            print(f"  - {game['home_team']} vs {game['away_team']} (Week {game['week']})")
            print(f"    Total Odds: {game['total_odds']}")
            print(f"    Bookmakers: {game['bookmakers']}")
            print(f"    Home Odds Range: {game['worst_home_odds']} to {game['best_home_odds']}")
            print(f"    Away Odds Range: {game['worst_away_odds']} to {game['best_away_odds']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_live_odds_nfl())
