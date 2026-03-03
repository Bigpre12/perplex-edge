#!/usr/bin/env python3
"""
POPULATE ODDS SNAPSHOTS - Initialize and populate the odds_snapshots table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_odds_snapshots():
    """Populate odds_snapshots table with initial data"""
    
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
                WHERE table_name = 'odds_snapshots'
            )
        """)
        
        if not table_check:
            print("Creating odds_snapshots table...")
            await conn.execute("""
                CREATE TABLE odds_snapshots (
                    id SERIAL PRIMARY KEY,
                    game_id INTEGER NOT NULL,
                    market_id INTEGER NOT NULL,
                    player_id INTEGER,
                    external_fixture_id VARCHAR(100),
                    external_market_id VARCHAR(100),
                    external_outcome_id VARCHAR(100),
                    bookmaker VARCHAR(50) NOT NULL,
                    line_value DECIMAL(10, 2),
                    price DECIMAL(10, 4),
                    american_odds INTEGER,
                    side VARCHAR(10),
                    is_active BOOLEAN DEFAULT TRUE,
                    snapshot_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample odds snapshot data
        print("Generating sample odds snapshot data...")
        
        snapshots = [
            # NBA Game 662 - LeBron James Points Market
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_91',
                'external_outcome_id': 'over_13.5',
                'bookmaker': 'DraftKings',
                'line_value': 13.5,
                'price': 1.9091,  # -110 American odds
                'american_odds': -110,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=6),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=6),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=6)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_91',
                'external_outcome_id': 'under_13.5',
                'bookmaker': 'DraftKings',
                'line_value': 13.5,
                'price': 1.9091,  # -110 American odds
                'american_odds': -110,
                'side': 'under',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=6),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=6),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=6)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_91',
                'external_outcome_id': 'over_14.0',
                'bookmaker': 'DraftKings',
                'line_value': 14.0,
                'price': 1.9524,  # -105 American odds
                'american_odds': -105,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=4)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_91',
                'external_outcome_id': 'under_14.0',
                'bookmaker': 'DraftKings',
                'line_value': 14.0,
                'price': 1.9524,  # -105 American odds
                'american_odds': -105,
                'side': 'under',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=4)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_91',
                'external_outcome_id': 'over_13.5',
                'bookmaker': 'FanDuel',
                'line_value': 13.5,
                'price': 1.9231,  # -108 American odds
                'american_odds': -108,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=4)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_91',
                'external_outcome_id': 'under_13.5',
                'bookmaker': 'FanDuel',
                'line_value': 13.5,
                'price': 1.9231,  # -108 American odds
                'american_odds': -108,
                'side': 'under',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=4)
            },
            # NBA Game 662 - Stephen Curry Points Market
            {
                'game_id': 662,
                'market_id': 92,
                'player_id': 92,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_92',
                'external_outcome_id': 'over_28.5',
                'bookmaker': 'DraftKings',
                'line_value': 28.5,
                'price': 1.9091,  # -110 American odds
                'american_odds': -110,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=3)
            },
            {
                'game_id': 662,
                'market_id': 92,
                'player_id': 92,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_92',
                'external_outcome_id': 'under_28.5',
                'bookmaker': 'DraftKings',
                'line_value': 28.5,
                'price': 1.9091,  # -110 American odds
                'american_odds': -110,
                'side': 'under',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=3)
            },
            {
                'game_id': 662,
                'market_id': 92,
                'player_id': 92,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_92',
                'external_outcome_id': 'over_29.0',
                'bookmaker': 'FanDuel',
                'line_value': 29.0,
                'price': 1.9259,  # -108 American odds
                'american_odds': -108,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=3)
            },
            # NFL Game 664 - Patrick Mahomes Passing Yards
            {
                'game_id': 664,
                'market_id': 101,
                'player_id': 101,
                'external_fixture_id': 'nfl_2026_664',
                'external_market_id': 'player_pass_yards_101',
                'external_outcome_id': 'over_285.5',
                'bookmaker': 'DraftKings',
                'line_value': 285.5,
                'price': 1.9091,  # -110 American odds
                'american_odds': -110,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'game_id': 664,
                'market_id': 101,
                'player_id': 101,
                'external_fixture_id': 'nfl_2026_664',
                'external_market_id': 'player_pass_yards_101',
                'external_outcome_id': 'under_285.5',
                'bookmaker': 'DraftKings',
                'line_value': 285.5,
                'price': 1.9091,  # -110 American odds
                'american_odds': -110,
                'side': 'under',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'game_id': 664,
                'market_id': 102,
                'player_id': 101,
                'external_fixture_id': 'nfl_2026_664',
                'external_market_id': 'player_pass_tds_101',
                'external_outcome_id': 'over_2.5',
                'bookmaker': 'DraftKings',
                'line_value': 2.5,
                'price': 1.9091,  # -110 American odds
                'american_odds': -110,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'game_id': 664,
                'market_id': 102,
                'player_id': 101,
                'external_fixture_id': 'nfl_2026_664',
                'external_market_id': 'player_pass_tds_101',
                'external_outcome_id': 'under_2.5',
                'bookmaker': 'DraftKings',
                'line_value': 2.5,
                'price': 1.9091,  # -110 American odds
                'american_odds': -110,
                'side': 'under',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            # MLB Game 666 - Aaron Judge Home Runs
            {
                'game_id': 666,
                'market_id': 201,
                'player_id': 201,
                'external_fixture_id': 'mlb_2026_666',
                'external_market_id': 'player_hr_201',
                'external_outcome_id': 'over_1.5',
                'bookmaker': 'DraftKings',
                'line_value': 1.5,
                'price': 1.9091,  # -110 American odds
                'american_odds': -110,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=1)
            },
            {
                'game_id': 666,
                'market_id': 201,
                'player_id': 201,
                'external_fixture_id': 'mlb_2026_666',
                'external_market_id': 'player_hr_201',
                'external_outcome_id': 'under_1.5',
                'bookmaker': 'DraftKings',
                'line_value': 1.5,
                'price': 1.9091,  # -110 American odds
                'american_odds': -110,
                'side': 'under',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=1)
            },
            {
                'game_id': 666,
                'market_id': 202,
                'player_id': 201,
                'external_fixture_id': 'mlb_2026_666',
                'external_market_id': 'player_avg_201',
                'external_outcome_id': 'over_0.275',
                'bookmaker': 'DraftKings',
                'line_value': 0.275,
                'price': 1.9091,  # -110 American odds
                'american_odds': -110,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'created_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=1)
            },
            # NHL Game 668 - Connor McDavid Points
            {
                'game_id': 668,
                'market_id': 301,
                'player_id': 301,
                'external_fixture_id': 'nhl_2026_668',
                'external_market_id': 'player_points_301',
                'external_outcome_id': 'over_1.5',
                'bookmaker': 'DraftKings',
                'line_value': 1.5,
                'price': 1.9091,  # -110 American odds
                'american_odds': -110,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 668,
                'market_id': 301,
                'player_id': 301,
                'external_fixture_id': 'nhl_2026_668',
                'external_market_id': 'player_points_301',
                'external_outcome_id': 'under_1.5',
                'bookmaker': 'DraftKings',
                'line_value': 1.5,
                'price': 1.9091,  # -110 American odds
                'american_odds': -110,
                'side': 'under',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            # Recent snapshots showing line movements
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_91',
                'external_outcome_id': 'over_14.0',
                'bookmaker': 'DraftKings',
                'line_value': 14.0,
                'price': 1.9524,  # -105 American odds
                'american_odds': -105,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(minutes=15),
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=15)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_91',
                'external_outcome_id': 'over_14.0',
                'bookmaker': 'DraftKings',
                'line_value': 14.0,
                'price': 1.9412,  # -108 American odds
                'american_odds': -108,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(minutes=10),
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=10)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_91',
                'external_outcome_id': 'over_14.0',
                'bookmaker': 'DraftKings',
                'line_value': 14.0,
                'price': 1.9615,  # -103 American odds
                'american_odds': -103,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(minutes=5),
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=5)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_91',
                'external_outcome_id': 'over_14.0',
                'bookmaker': 'DraftKings',
                'line_value': 14.0,
                'price': 1.9706,  # -102 American odds
                'american_odds': -102,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc),
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            },
            # FanDuel snapshots for comparison
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_91',
                'external_outcome_id': 'over_13.5',
                'bookmaker': 'FanDuel',
                'line_value': 13.5,
                'price': 1.9231,  # -108 American odds
                'american_odds': -108,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(minutes=5),
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=5)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_91',
                'external_outcome_id': 'over_13.5',
                'bookmaker': 'FanDuel',
                'line_value': 13.5,
                'price': 1.9346,  # -106 American odds
                'american_odds': -106,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc),
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            },
            # BetMGM snapshots
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_91',
                'external_outcome_id': 'over_14.5',
                'bookmaker': 'BetMGM',
                'line_value': 14.5,
                'price': 1.9091,  # -110 American odds
                'american_odds': -110,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc) - timedelta(minutes=10),
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=10)
            },
            {
                'game_id': 662,
                'market_id': 91,
                'player_id': 91,
                'external_fixture_id': 'nba_2026_662',
                'external_market_id': 'player_points_91',
                'external_outcome_id': 'over_14.5',
                'bookmaker': 'BetMGM',
                'line_value': 14.5,
                'price': 1.9231,  # -108 American odds
                'american_odds': -108,
                'side': 'over',
                'is_active': True,
                'snapshot_at': datetime.now(timezone.utc),
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
        ]
        
        # Insert odds snapshot data
        for snapshot in snapshots:
            await conn.execute("""
                INSERT INTO odds_snapshots (
                    game_id, market_id, player_id, external_fixture_id, external_market_id,
                    external_outcome_id, bookmaker, line_value, price, american_odds, side,
                    is_active, snapshot_at, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            """, 
                snapshot['game_id'],
                snapshot['market_id'],
                snapshot['player_id'],
                snapshot['external_fixture_id'],
                snapshot['external_market_id'],
                snapshot['external_outcome_id'],
                snapshot['bookmaker'],
                snapshot['line_value'],
                snapshot['price'],
                snapshot['american_odds'],
                snapshot['side'],
                snapshot['is_active'],
                snapshot['snapshot_at'],
                snapshot['created_at'],
                snapshot['updated_at']
            )
        
        print("Sample odds snapshot data populated successfully")
        
        # Get odds snapshot statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_snapshots,
                COUNT(DISTINCT game_id) as unique_games,
                COUNT(DISTINCT market_id) as unique_markets,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT bookmaker) as unique_bookmakers,
                COUNT(DISTINCT external_fixture_id) as unique_fixtures,
                COUNT(DISTINCT external_market_id) as unique_external_markets,
                COUNT(DISTINCT external_outcome_id) as unique_external_outcomes,
                AVG(line_value) as avg_line_value,
                AVG(price) as avg_price,
                AVG(american_odds) as avg_american_odds,
                COUNT(CASE WHEN side = 'over' THEN 1 END) as over_snapshots,
                COUNT(CASE WHEN side = 'under' THEN 1 END) as under_snapshots,
                COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_snapshots
            FROM odds_snapshots
        """)
        
        print(f"\nOdds Snapshot Statistics:")
        print(f"  Total Snapshots: {stats['total_snapshots']}")
        print(f"  Unique Games: {stats['unique_games']}")
        print(f"  Unique Markets: {stats['unique_markets']}")
        print(f"  Unique Players: {stats['unique_players']}")
        print(f"  Unique Bookmakers: {stats['unique_bookmakers']}")
        print(f"  Unique Fixtures: {stats['unique_fixtures']}")
        print(f"  Unique External Markets: {stats['unique_external_markets']}")
        print(f"  Unique External Outcomes: {stats['unique_external_outcomes']}")
        print(f"  Avg Line Value: {stats['avg_line_value']:.2f}")
        print(f"  Avg Price: {stats['avg_price']:.4f}")
        print(f"  Avg American Odds: {stats['avg_american_odds']:.0f}")
        print(f"  Over Snapshots: {stats['over_snapshots']}")
        print(f"  Under Snapshots: {stats['under_snapshots']}")
        print(f"  Active Snapshots: {stats['active_snapshots']}")
        
        # Get snapshots by bookmaker
        by_bookmaker = await conn.fetch("""
            SELECT 
                bookmaker,
                COUNT(*) as total_snapshots,
                COUNT(DISTINCT game_id) as unique_games,
                COUNT(DISTINCT market_id) as unique_markets,
                AVG(line_value) as avg_line_value,
                AVG(price) as avg_price,
                AVG(american_odds) as avg_american_odds,
                COUNT(CASE WHEN side = 'over' THEN 1 END) as over_snapshots,
                COUNT(CASE WHEN side = 'under' THEN 1 END) as under_snapshots
            FROM odds_snapshots
            GROUP BY bookmaker
            ORDER BY total_snapshots DESC
        """)
        
        print(f"\nSnapshots by Bookmaker:")
        for bookmaker in by_bookmaker:
            print(f"  {bookmaker}:")
            print(f"    Total Snapshots: {bookmaker['total_snapshots']}")
            print(f"    Unique Games: {bookmaker['unique_games']}")
            print(f"    Unique Markets: {bookmaker['unique_markets']}")
            print(f"    Avg Line Value: {bookmaker['avg_line_value']:.2f}")
            print(f"    Avg Price: {bookmaker['avg_price']:.4f}")
            print(f"    Avg American Odds: {bookmaker['avg_american_odds']:.0f}")
            print(f"    Over/Under: {bookmaker['over_snapshots']}/{bookmaker['under_snapshots']}")
        
        # Get snapshots by game
        by_game = await conn.fetch("""
            SELECT 
                game_id,
                COUNT(*) as total_snapshots,
                COUNT(DISTINCT market_id) as unique_markets,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT bookmaker) as unique_bookmakers,
                MIN(snapshot_at) as first_snapshot,
                MAX(snapshot_at) as last_snapshot
            FROM odds_snapshots
            GROUP BY game_id
            ORDER BY total_snapshots DESC
            LIMIT 5
        """)
        
        print(f"\nTop 5 Games by Snapshot Count:")
        for game in by_game:
            print(f"  Game {game['game_id']}:")
            print(f"    Total Snapshots: {game['total_snapshots']}")
            print(f"    Unique Markets: {game['unique_markets']}")
            print(f"    Unique Players: {game['unique_players']}")
            print(f"    Unique Bookmakers: {game['unique_bookmakers']}")
            print(f"    Period: {game['first_snapshot']} to {game['last_snapshot']}")
        
        # Get recent snapshots
        recent = await conn.fetch("""
            SELECT * FROM odds_snapshots 
            ORDER BY snapshot_at DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent Snapshots:")
        for snapshot in recent:
            print(f"  - Game {snapshot['game_id']}, Market {snapshot['market_id']}")
            print(f"    {snapshot['bookmaker']}: {snapshot['line_value']} {snapshot['side']} ({snapshot['american_odds']})")
            print(f"    Price: {snapshot['price']:.4f}, Player {snapshot['player_id']}")
            print(f"    Snapshot: {snapshot['snapshot_at']}")
        
        # Get line movements for a specific game/market/player
        movements = await conn.fetch("""
            SELECT 
                bookmaker,
                line_value,
                price,
                american_odds,
                side,
                snapshot_at,
                LAG(line_value) OVER (PARTITION BY bookmaker ORDER BY snapshot_at) as prev_line_value,
                LAG(price) OVER (PARTITION BY bookmaker ORDER BY snapshot_at) as prev_price,
                LAG(american_odds) OVER (PARTITION BY bookmaker ORDER BY snapshot_at) as prev_american_odds
            FROM odds_snapshots 
            WHERE game_id = 662 AND market_id = 91 AND player_id = 91
            ORDER BY bookmaker, snapshot_at ASC
        """)
        
        print(f"\nLine Movements for LeBron James Points (Game 662):")
        for movement in movements:
            line_movement = movement['line_value'] - movement['prev_line_value'] if movement['prev_line_value'] else 0
            price_movement = movement['price'] - movement['prev_price'] if movement['prev_price'] else 0
            odds_movement = movement['american_odds'] - movement['prev_american_odds'] if movement['prev_american_odds'] else 0
            
            print(f"  - {movement['bookmaker']}: {movement['line_value']} {movement['side']} ({movement['american_odds']})")
            print(f"    Price: {movement['price']:.4f}, Snapshot: {movement['snapshot_at']}")
            if movement['prev_line_value']:
                print(f"    Movement: Line {line_movement:+.1f}, Price {price_movement:+.4f}, Odds {odds_movement:+d}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_odds_snapshots())
