#!/usr/bin/env python3
"""
POPULATE LINES - Initialize and populate the lines table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_lines():
    """Populate lines table with initial data"""
    
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
                WHERE table_name = 'lines'
            )
        """)
        
        if not table_check:
            print("Creating lines table...")
            await conn.execute("""
                CREATE TABLE lines (
                    id SERIAL PRIMARY KEY,
                    game_id INTEGER NOT NULL,
                    market_id INTEGER NOT NULL,
                    player_id INTEGER,
                    sportsbook VARCHAR(50) NOT NULL,
                    line_value DECIMAL(10, 2),
                    odds INTEGER,
                    side VARCHAR(10) NOT NULL,
                    is_current BOOLEAN DEFAULT FALSE,
                    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample line data
        print("Generating sample line data...")
        
        lines = [
            # NBA Player Props - Game 662, Player 91 (LeBron James)
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 13.5,
                'odds': -110,
                'side': 'over',
                'is_current': False,
                'fetched_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 13.5,
                'odds': -110,
                'side': 'under',
                'is_current': False,
                'fetched_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 15.5,
                'odds': -110,
                'side': 'over',
                'is_current': False,
                'fetched_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 15.5,
                'odds': -110,
                'side': 'under',
                'is_current': False,
                'fetched_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 16.5,
                'odds': -110,
                'side': 'over',
                'is_current': False,
                'fetched_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 16.5,
                'odds': -110,
                'side': 'under',
                'is_current': False,
                'fetched_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 14.5,
                'odds': -110,
                'side': 'over',
                'is_current': False,
                'fetched_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 14.5,
                'odds': -110,
                'side': 'under',
                'is_current': False,
                'fetched_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 12.5,
                'odds': -110,
                'side': 'over',
                'is_current': False,
                'fetched_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 12.5,
                'odds': -110,
                'side': 'under',
                'is_current': False,
                'fetched_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            # Current lines for LeBron James
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 14.0,
                'odds': -105,
                'side': 'over',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 14.0,
                'odds': -105,
                'side': 'under',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            # FanDuel lines for LeBron James
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'fanduel',
                'line_value': 13.5,
                'odds': -108,
                'side': 'over',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'fanduel',
                'line_value': 13.5,
                'odds': -108,
                'side': 'under',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            # BetMGM lines for LeBron James
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'betmgm',
                'line_value': 14.5,
                'odds': -110,
                'side': 'over',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'betmgm',
                'line_value': 14.5,
                'odds': -110,
                'side': 'under',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            # NBA Player Props - Game 662, Player 92 (Stephen Curry)
            {
                'game_id': 662,
                'market_id': 92,
                'player_id': 92,
                'sportsbook': 'draftkings',
                'line_value': 28.5,
                'odds': -110,
                'side': 'over',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 662,
                'market_id': 92,
                'player_id': 92,
                'sportsbook': 'draftkings',
                'line_value': 28.5,
                'odds': -110,
                'side': 'under',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 662,
                'market_id': 92,
                'player_id': 92,
                'sportsbook': 'fanduel',
                'line_value': 29.0,
                'odds': -108,
                'side': 'over',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 662,
                'market_id': 92,
                'player_id': 92,
                'sportsbook': 'fanduel',
                'line_value': 29.0,
                'odds': -108,
                'side': 'under',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            # NBA Player Props - Game 663, Player 93 (Kevin Durant)
            {
                'game_id': 663,
                'market_id': 93,
                'player_id': 93,
                'sportsbook': 'draftkings',
                'line_value': 25.5,
                'odds': -110,
                'side': 'over',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 663,
                'market_id': 93,
                'player_id': 93,
                'sportsbook': 'draftkings',
                'line_value': 25.5,
                'odds': -110,
                'side': 'under',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            # NFL Player Props - Game 664, Player 101 (Patrick Mahomes)
            {
                'game_id': 664,
                'market_id': 101,
                'player_id': 101,
                'sportsbook': 'draftkings',
                'line_value': 285.5,
                'odds': -110,
                'side': 'over',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 664,
                'market_id': 101,
                'player_id': 101,
                'sportsbook': 'draftkings',
                'line_value': 285.5,
                'odds': -110,
                'side': 'under',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 664,
                'market_id': 102,
                'player_id': 101,
                'sportsbook': 'draftkings',
                'line_value': 2.5,
                'odds': -110,
                'side': 'over',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 664,
                'market_id': 102,
                'player_id': 101,
                'sportsbook': 'draftkings',
                'line_value': 2.5,
                'odds': -110,
                'side': 'under',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            # NFL Player Props - Game 665, Player 102 (Josh Allen)
            {
                'game_id': 665,
                'market_id': 103,
                'player_id': 102,
                'sportsbook': 'draftkings',
                'line_value': 245.5,
                'odds': -110,
                'side': 'over',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 665,
                'market_id': 103,
                'player_id': 102,
                'sportsbook': 'draftkings',
                'line_value': 245.5,
                'odds': -110,
                'side': 'under',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            # MLB Player Props - Game 666, Player 201 (Aaron Judge)
            {
                'game_id': 666,
                'market_id': 201,
                'player_id': 201,
                'sportsbook': 'draftkings',
                'line_value': 1.5,
                'odds': -110,
                'side': 'over',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 666,
                'market_id': 201,
                'player_id': 201,
                'sportsbook': 'draftkings',
                'line_value': 1.5,
                'odds': -110,
                'side': 'under',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 666,
                'market_id': 202,
                'player_id': 201,
                'sportsbook': 'draftkings',
                'line_value': 0.275,
                'odds': -110,
                'side': 'over',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 666,
                'market_id': 202,
                'player_id': 201,
                'sportsbook': 'draftkings',
                'line_value': 0.275,
                'odds': -110,
                'side': 'under',
                'is_current': True,
                'fetched_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            # Historical lines showing movement
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 13.5,
                'odds': -110,
                'side': 'over',
                'is_current': False,
                'fetched_at': datetime.now(timezone.utc) - timedelta(hours=6)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 13.5,
                'odds': -110,
                'side': 'under',
                'is_current': False,
                'fetched_at': datetime.now(timezone.utc) - timedelta(hours=6)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 14.0,
                'odds': -110,
                'side': 'over',
                'is_current': False,
                'fetched_at': datetime.now(timezone.utc) - timedelta(hours=4)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'sportsbook': 'draftkings',
                'line_value': 14.0,
                'odds': -110,
                'side': 'under',
                'is_current': False,
                'fetched_at': datetime.now(timezone.utc) - timedelta(hours=4)
            }
        ]
        
        # Insert line data
        for line in lines:
            await conn.execute("""
                INSERT INTO lines (
                    game_id, market_id, player_id, sportsbook, line_value, odds, side,
                    is_current, fetched_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
                line['game_id'],
                line['market_id'],
                line['player_id'],
                line['sportsbook'],
                line['line_value'],
                line['odds'],
                line['side'],
                line['is_current'],
                line['fetched_at']
            )
        
        print("Sample line data populated successfully")
        
        # Get line statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_lines,
                COUNT(DISTINCT game_id) as unique_games,
                COUNT(DISTINCT market_id) as unique_markets,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT sportsbook) as unique_sportsbooks,
                COUNT(CASE WHEN is_current = TRUE THEN 1 END) as current_lines,
                COUNT(CASE WHEN is_current = FALSE THEN 1 END) as historical_lines,
                AVG(line_value) as avg_line_value,
                AVG(odds) as avg_odds
            FROM lines
        """)
        
        print(f"\nLine Statistics:")
        print(f"  Total Lines: {stats['total_lines']}")
        print(f"  Unique Games: {stats['unique_games']}")
        print(f"  Unique Markets: {stats['unique_markets']}")
        print(f"  Unique Players: {stats['unique_players']}")
        print(f"  Unique Sportsbooks: {stats['unique_sportsbooks']}")
        print(f"  Current Lines: {stats['current_lines']}")
        print(f"  Historical Lines: {stats['historical_lines']}")
        print(f"  Avg Line Value: {stats['avg_line_value']:.2f}")
        print(f"  Avg Odds: {stats['avg_odds']:.0f}")
        
        # Get lines by sportsbook
        by_sportsbook = await conn.fetch("""
            SELECT 
                sportsbook,
                COUNT(*) as total_lines,
                COUNT(CASE WHEN is_current = TRUE THEN 1 END) as current_lines,
                COUNT(DISTINCT game_id) as unique_games,
                COUNT(DISTINCT player_id) as unique_players,
                AVG(line_value) as avg_line_value,
                AVG(odds) as avg_odds
            FROM lines
            GROUP BY sportsbook
            ORDER BY total_lines DESC
        """)
        
        print(f"\nLines by Sportsbook:")
        for sportsbook in by_sportsbook:
            print(f"  {sportsbook}:")
            print(f"    Total Lines: {sportsbook['total_lines']}")
            print(f"    Current Lines: {sportsbook['current_lines']}")
            print(f"    Unique Games: {sportsbook['unique_games']}")
            print(f"    Unique Players: {sportsbook['unique_players']}")
            print(f"    Avg Line Value: {sportsbook['avg_line_value']:.2f}")
            print(f"    Avg Odds: {sportsbook['avg_odds']:.0f}")
        
        # Get current lines
        current = await conn.fetch("""
            SELECT * FROM lines 
            WHERE is_current = TRUE 
            ORDER BY fetched_at DESC 
            LIMIT 5
        """)
        
        print(f"\nCurrent Lines:")
        for line in current:
            print(f"  - Game {line['game_id']}, Player {line['player_id']}")
            print(f"    {line['sportsbook']}: {line['line_value']} {line['side']} ({line['odds']})")
            print(f"    Market {line['market_id']}, Fetched: {line['fetched_at']}")
        
        # Get line movements for a specific player
        movements = await conn.fetch("""
            SELECT * FROM lines 
            WHERE game_id = 662 AND player_id = 91 
            ORDER BY fetched_at ASC
        """)
        
        print(f"\nLine Movements for Player 91 (LeBron James):")
        for movement in movements:
            print(f"  - {movement['fetched_at']}: {movement['line_value']} {movement['side']} ({movement['odds']})")
            print(f"    {movement['sportsbook']}, Current: {movement['is_current']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_lines())
