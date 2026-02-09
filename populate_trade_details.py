#!/usr/bin/env python3
"""
POPULATE TRADE DETAILS - Initialize and populate the trade_details table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_trade_details():
    """Populate trade_details table with initial data"""
    
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
                WHERE table_name = 'trade_details'
            )
        """)
        
        if not table_check:
            print("Creating trade_details table...")
            await conn.execute("""
                CREATE TABLE trade_details (
                    id SERIAL PRIMARY KEY,
                    trade_id VARCHAR(50) NOT NULL,
                    player_id INTEGER NOT NULL,
                    from_team_id INTEGER,
                    to_team_id INTEGER,
                    asset_type VARCHAR(50) NOT NULL,
                    asset_description TEXT,
                    player_name VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample trade details data
        print("Generating sample trade details data...")
        
        trade_details = [
            # NBA Trades
            {
                'trade_id': 'NBA_2024_001',
                'player_id': 1,
                'from_team_id': 5,
                'to_team_id': 3,
                'asset_type': 'player',
                'asset_description': 'Star forward with championship experience',
                'player_name': 'Kevin Durant',
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'trade_id': 'NBA_2024_001',
                'player_id': 2,
                'from_team_id': 3,
                'to_team_id': 5,
                'asset_type': 'player',
                'asset_description': 'All-star guard with scoring ability',
                'player_name': 'Devin Booker',
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'trade_id': 'NBA_2024_002',
                'player_id': 3,
                'from_team_id': 4,
                'to_team_id': 7,
                'asset_type': 'player',
                'asset_description': 'Elite point guard with playmaking skills',
                'player_name': 'Kyle Lowry',
                'created_at': datetime.now(timezone.utc) - timedelta(days=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=25)
            },
            {
                'trade_id': 'NBA_2024_002',
                'player_id': 4,
                'from_team_id': 7,
                'to_team_id': 4,
                'asset_type': 'player',
                'asset_description': 'Veteran center with defensive presence',
                'player_name': 'Nikola Jokic',
                'created_at': datetime.now(timezone.utc) - timedelta(days=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=25)
            },
            {
                'trade_id': 'NBA_2024_003',
                'player_id': 5,
                'from_team_id': 6,
                'to_team_id': 8,
                'asset_type': 'player',
                'asset_description': 'Rising star with high potential',
                'player_name': 'Tyrese Haliburton',
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'trade_id': 'NBA_2024_003',
                'player_id': 6,
                'from_team_id': 8,
                'to_team_id': 6,
                'asset_type': 'player',
                'asset_description': 'Veteran scorer with clutch performance',
                'player_name': 'Damian Lillard',
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'trade_id': 'NBA_2024_004',
                'player_id': 7,
                'from_team_id': 9,
                'to_team_id': 10,
                'asset_type': 'player',
                'asset_description': 'Defensive specialist with three-point shooting',
                'player_name': 'Matisse Thybulle',
                'created_at': datetime.now(timezone.utc) - timedelta(days=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=15)
            },
            {
                'trade_id': 'NBA_2024_004',
                'player_id': 8,
                'from_team_id': 10,
                'to_team_id': 9,
                'asset_type': 'player',
                'asset_description': 'Young forward with scoring potential',
                'player_name': 'Patrick Williams',
                'created_at': datetime.now(timezone.utc) - timedelta(days=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=15)
            },
            # NFL Trades
            {
                'trade_id': 'NFL_2024_001',
                'player_id': 101,
                'from_team_id': 101,
                'to_team_id': 102,
                'asset_type': 'player',
                'asset_description': 'Elite quarterback with Super Bowl experience',
                'player_name': 'Aaron Rodgers',
                'created_at': datetime.now(timezone.utc) - timedelta(days=35),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=35)
            },
            {
                'trade_id': 'NFL_2024_001',
                'player_id': 102,
                'from_team_id': 102,
                'to_team_id': 101,
                'asset_type': 'player',
                'asset_description': 'Pro Bowl wide receiver with speed',
                'player_name': 'Davante Adams',
                'created_at': datetime.now(timezone.utc) - timedelta(days=35),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=35)
            },
            {
                'trade_id': 'NFL_2024_002',
                'player_id': 103,
                'from_team_id': 103,
                'to_team_id': 104,
                'asset_type': 'player',
                'asset_description': 'Star running back with versatility',
                'player_name': 'Christian McCaffrey',
                'created_at': datetime.now(timezone.utc) - timedelta(days=28),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=28)
            },
            {
                'trade_id': 'NFL_2024_002',
                'player_id': 104,
                'from_team_id': 104,
                'to_team_id': 103,
                'asset_type': 'player',
                'asset_description': 'Veteran linebacker with leadership',
                'player_name': 'Bobby Wagner',
                'created_at': datetime.now(timezone.utc) - timedelta(days=28),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=28)
            },
            {
                'trade_id': 'NFL_2024_003',
                'player_id': 105,
                'from_team_id': 105,
                'to_team_id': 106,
                'asset_type': 'player',
                'asset_description': 'Elite edge rusher with sack ability',
                'player_name': 'Myles Garrett',
                'created_at': datetime.now(timezone.utc) - timedelta(days=21),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=21)
            },
            {
                'trade_id': 'NFL_2024_003',
                'player_id': 106,
                'from_team_id': 106,
                'to_team_id': 105,
                'asset_type': 'player',
                'asset_description': 'Pro Bowl cornerback with coverage skills',
                'player_name': 'Jaire Alexander',
                'created_at': datetime.now(timezone.utc) - timedelta(days=21),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=21)
            },
            # MLB Trades
            {
                'trade_id': 'MLB_2024_001',
                'player_id': 201,
                'from_team_id': 201,
                'to_team_id': 202,
                'asset_type': 'player',
                'asset_description': 'Power-hitting first baseman with MVP potential',
                'player_name': 'Pete Alonso',
                'created_at': datetime.now(timezone.utc) - timedelta(days=40),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=40)
            },
            {
                'trade_id': 'MLB_2024_001',
                'player_id': 202,
                'from_team_id': 202,
                'to_team_id': 201,
                'asset_type': 'player',
                'asset_description': 'Ace pitcher with strikeout ability',
                'player_name': 'Jacob deGrom',
                'created_at': datetime.now(timezone.utc) - timedelta(days=40),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=40)
            },
            {
                'trade_id': 'MLB_2024_002',
                'player_id': 203,
                'from_team_id': 203,
                'to_team_id': 204,
                'asset_type': 'player',
                'asset_description': 'Gold glove outfielder with speed',
                'player_name': 'Mike Trout',
                'created_at': datetime.now(timezone.utc) - timedelta(days=32),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=32)
            },
            {
                'trade_id': 'MLB_2024_002',
                'player_id': 204,
                'from_team_id': 204,
                'to_team_id': 203,
                'asset_type': 'player',
                'asset_description': 'All-star third baseman with power',
                'player_name': 'Manny Machado',
                'created_at': datetime.now(timezone.utc) - timedelta(days=32),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=32)
            },
            {
                'trade_id': 'MLB_2024_003',
                'player_id': 205,
                'from_team_id': 205,
                'to_team_id': 206,
                'asset_type': 'player',
                'asset_description': 'Cy Young winner with elite stuff',
                'player_name': 'Gerrit Cole',
                'created_at': datetime.now(timezone.utc) - timedelta(days=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=25)
            },
            {
                'trade_id': 'MLB_2024_003',
                'player_id': 206,
                'from_team_id': 206,
                'to_team_id': 205,
                'asset_type': 'player',
                'asset_description': 'Hall of fame closer with save ability',
                'player_name': 'Craig Kimbrel',
                'created_at': datetime.now(timezone.utc) - timedelta(days=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=25)
            },
            # NHL Trades
            {
                'trade_id': 'NHL_2024_001',
                'player_id': 301,
                'from_team_id': 301,
                'to_team_id': 302,
                'asset_type': 'player',
                'asset_description': 'Elite center with scoring ability',
                'player_name': 'Connor McDavid',
                'created_at': datetime.now(timezone.utc) - timedelta(days=38),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=38)
            },
            {
                'trade_id': 'NHL_2024_001',
                'player_id': 302,
                'from_team_id': 302,
                'to_team_id': 301,
                'asset_type': 'player',
                'asset_description': 'Power forward with physical presence',
                'player_name': 'Nathan MacKinnon',
                'created_at': datetime.now(timezone.utc) - timedelta(days=38),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=38)
            },
            {
                'trade_id': 'NHL_2024_002',
                'player_id': 303,
                'from_team_id': 303,
                'to_team_id': 304,
                'asset_type': 'player',
                'asset_description': 'Elite goaltender with Vezina potential',
                'player_name': 'Andrei Vasilevskiy',
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'trade_id': 'NHL_2024_002',
                'player_id': 304,
                'from_team_id': 304,
                'to_team_id': 303,
                'asset_type': 'player',
                'asset_description': 'Offensive defenseman with power play skills',
                'player_name': 'Victor Hedman',
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'trade_id': 'NHL_2024_003',
                'player_id': 305,
                'from_team_id': 305,
                'to_team_id': 306,
                'asset_type': 'player',
                'asset_description': 'Goal-scoring winger with speed',
                'player_name': 'Auston Matthews',
                'created_at': datetime.now(timezone.utc) - timedelta(days=22),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=22)
            },
            {
                'trade_id': 'NHL_2024_003',
                'player_id': 306,
                'from_team_id': 306,
                'to_team_id': 305,
                'asset_type': 'player',
                'asset_description': 'Two-way defenseman with leadership',
                'player_name': 'Roman Josi',
                'created_at': datetime.now(timezone.utc) - timedelta(days=22),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=22)
            },
            # Multi-asset trades
            {
                'trade_id': 'NBA_2024_005',
                'player_id': 9,
                'from_team_id': 11,
                'to_team_id': 12,
                'asset_type': 'draft_pick',
                'asset_description': '2025 first round draft pick (lottery protected)',
                'player_name': '2025 1st Round Pick',
                'created_at': datetime.now(timezone.utc) - timedelta(days=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=10)
            },
            {
                'trade_id': 'NBA_2024_005',
                'player_id': 10,
                'from_team_id': 12,
                'to_team_id': 11,
                'asset_type': 'player',
                'asset_description': 'Young center with defensive potential',
                'player_name': 'Walker Kessler',
                'created_at': datetime.now(timezone.utc) - timedelta(days=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=10)
            },
            {
                'trade_id': 'NFL_2024_004',
                'player_id': 107,
                'from_team_id': 107,
                'to_team_id': 108,
                'asset_type': 'draft_pick',
                'asset_description': '2025 second round draft pick',
                'player_name': '2025 2nd Round Pick',
                'created_at': datetime.now(timezone.utc) - timedelta(days=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=15)
            },
            {
                'trade_id': 'NFL_2024_004',
                'player_id': 108,
                'from_team_id': 108,
                'to_team_id': 107,
                'asset_type': 'player',
                'asset_description': 'Veteran safety with ball skills',
                'player_name': 'Kevin Byard',
                'created_at': datetime.now(timezone.utc) - timedelta(days=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=15)
            }
        ]
        
        # Insert trade details data
        for trade in trade_details:
            await conn.execute("""
                INSERT INTO trade_details (
                    trade_id, player_id, from_team_id, to_team_id, asset_type, asset_description,
                    player_name, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
                trade['trade_id'],
                trade['player_id'],
                trade['from_team_id'],
                trade['to_team_id'],
                trade['asset_type'],
                trade['asset_description'],
                trade['player_name'],
                trade['created_at'],
                trade['updated_at']
            )
        
        print("Sample trade details data populated successfully")
        
        # Get trade details statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_trades,
                COUNT(DISTINCT trade_id) as unique_trades,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT from_team_id) as unique_from_teams,
                COUNT(DISTINCT to_team_id) as unique_to_teams,
                COUNT(DISTINCT asset_type) as unique_asset_types,
                COUNT(CASE WHEN asset_type = 'player' THEN 1 END) as player_trades,
                COUNT(CASE WHEN asset_type = 'draft_pick' THEN 1 END) as draft_pick_trades,
                COUNT(CASE WHEN from_team_id = to_team_id THEN 1 END) as same_team_trades,
                COUNT(CASE WHEN from_team_id != to_team_id THEN 1 END) as different_team_trades
            FROM trade_details
        """)
        
        print(f"\nTrade Details Statistics:")
        print(f"  Total Trade Records: {stats['total_trades']}")
        print(f"  Unique Trades: {stats['unique_trades']}")
        print(f"  Unique Players: {stats['unique_players']}")
        print(f"  Unique From Teams: {stats['unique_from_teams']}")
        print(f"  Unique To Teams: {stats['unique_to_teams']}")
        print(f"  Unique Asset Types: {stats['unique_asset_types']}")
        print(f"  Player Trades: {stats['player_trades']}")
        print(f"  Draft Pick Trades: {stats['draft_pick_trades']}")
        print(f"  Same Team Trades: {stats['same_team_trades']}")
        print(f"  Different Team Trades: {stats['different_team_trades']}")
        
        # Get trades by trade ID
        by_trade_id = await conn.fetch("""
            SELECT 
                trade_id,
                COUNT(*) as total_assets,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT from_team_id) as unique_from_teams,
                COUNT(DISTINCT to_team_id) as unique_to_teams,
                COUNT(CASE WHEN asset_type = 'player' THEN 1 END) as player_assets,
                COUNT(CASE WHEN asset_type = 'draft_pick' THEN 1 END) as draft_pick_assets,
                MIN(created_at) as first_trade,
                MAX(created_at) as last_trade
            FROM trade_details
            GROUP BY trade_id
            ORDER BY total_assets DESC
            LIMIT 10
        """)
        
        print(f"\nTrades by Trade ID:")
        for trade in by_trade_id:
            print(f"  {trade['trade_id']}:")
            print(f"    Total Assets: {trade['total_assets']}")
            print(f"    Unique Players: {trade['unique_players']}")
            print(f"    From Teams: {trade['unique_from_teams']}")
            print(f"    To Teams: {trade['unique_to_teams']}")
            print(f"    Player Assets: {trade['player_assets']}")
            print(f"    Draft Pick Assets: {trade['draft_pick_assets']}")
            print(f"    Period: {trade['first_trade']} to {trade['last_trade']}")
        
        # Get trades by asset type
        by_asset_type = await conn.fetch("""
            SELECT 
                asset_type,
                COUNT(*) as total_trades,
                COUNT(DISTINCT trade_id) as unique_trades,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT from_team_id) as unique_from_teams,
                COUNT(DISTINCT to_team_id) as unique_to_teams,
                MIN(created_at) as first_trade,
                MAX(created_at) as last_trade
            FROM trade_details
            GROUP BY asset_type
            ORDER BY total_trades DESC
        """)
        
        print(f"\nTrades by Asset Type:")
        for asset in by_asset_type:
            print(f"  {asset['asset_type']}:")
            print(f"    Total Trades: {asset['total_trades']}")
            print(f"    Unique Trade IDs: {asset['unique_trades']}")
            print(f"    Unique Players: {asset['unique_players']}")
            print(f"    From Teams: {asset['unique_from_teams']}")
            print(f"    To Teams: {asset['unique_to_teams']}")
            print(f"    Period: {asset['first_trade']} to {asset['last_trade']}")
        
        # Get trades by team (from perspective)
        by_from_team = await conn.fetch("""
            SELECT 
                from_team_id,
                COUNT(*) as total_trades,
                COUNT(DISTINCT trade_id) as unique_trades,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT to_team_id) as unique_to_teams,
                COUNT(CASE WHEN asset_type = 'player' THEN 1 END) as player_assets,
                COUNT(CASE WHEN asset_type = 'draft_pick' THEN 1 END) as draft_pick_assets,
                MIN(created_at) as first_trade,
                MAX(created_at) as last_trade
            FROM trade_details
            WHERE from_team_id IS NOT NULL
            GROUP BY from_team_id
            ORDER BY total_trades DESC
            LIMIT 10
        """)
        
        print(f"\nTrades by From Team:")
        for team in by_from_team:
            print(f"  Team {team['from_team_id']}:")
            print(f"    Total Trades: {team['total_trades']}")
            print(f"    Unique Trade IDs: {team['unique_trades']}")
            print(f"    Unique Players: {team['unique_players']}")
            print(f"    To Teams: {team['unique_to_teams']}")
            print(f"    Player Assets: {team['player_assets']}")
            print(f"    Draft Pick Assets: {team['draft_pick_assets']}")
            print(f"    Period: {team['first_trade']} to {team['last_trade']}")
        
        # Get trades by team (to perspective)
        by_to_team = await conn.fetch("""
            SELECT 
                to_team_id,
                COUNT(*) as total_trades,
                COUNT(DISTINCT trade_id) as unique_trades,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT from_team_id) as unique_from_teams,
                COUNT(CASE WHEN asset_type = 'player' THEN 1 END) as player_assets,
                COUNT(CASE WHEN asset_type = 'draft_pick' THEN 1 END) as draft_pick_assets,
                MIN(created_at) as first_trade,
                MAX(created_at) as last_trade
            FROM trade_details
            WHERE to_team_id IS NOT NULL
            GROUP BY to_team_id
            ORDER BY total_trades DESC
            LIMIT 10
        """)
        
        print(f"\nTrades by To Team:")
        for team in by_to_team:
            print(f"  Team {team['to_team_id']}:")
            print(f"    Total Trades: {team['total_trades']}")
            print(f"    Unique Trade IDs: {team['unique_trades']}")
            print(f"    Unique Players: {team['unique_players']}")
            print(f"    From Teams: {team['unique_from_teams']}")
            print(f"    Player Assets: {team['player_assets']}")
            print(f"    Draft Pick Assets: {team['draft_pick_assets']}")
            print(f"    Period: {team['first_trade']} to {team['last_trade']}")
        
        # Recent trades
        recent = await conn.fetch("""
            SELECT * FROM trade_details 
            ORDER BY created_at DESC, updated_at DESC 
            LIMIT 10
        """)
        
        print(f"\nRecent Trade Details:")
        for trade in recent:
            print(f"  - {trade['player_name']} ({trade['asset_type']})")
            print(f"    Trade ID: {trade['trade_id']}")
            print(f"    From Team: {trade['from_team_id']} → To Team: {trade['to_team_id']}")
            print(f"    Asset Description: {trade['asset_description']}")
            print(f"    Created: {trade['created_at']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_trade_details())
