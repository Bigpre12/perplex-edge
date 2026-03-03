#!/usr/bin/env python3
"""
POPULATE USER BETS - Initialize and populate the user_bets table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_user_bets():
    """Populate user_bets table with initial data"""
    
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
                WHERE table_name = 'user_bets'
            )
        """)
        
        if not table_check:
            print("Creating user_bets table...")
            await conn.execute("""
                CREATE TABLE user_bets (
                    id SERIAL PRIMARY KEY,
                    sport_id INTEGER NOT NULL,
                    game_id INTEGER NOT NULL,
                    player_id INTEGER,
                    market_type VARCHAR(50) NOT NULL,
                    side VARCHAR(10) NOT NULL,
                    line_value DECIMAL(10, 2),
                    sportsbook VARCHAR(50) NOT NULL,
                    opening_odds DECIMAL(10, 2),
                    stake DECIMAL(10, 2) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    actual_value DECIMAL(10, 2),
                    closing_odds DECIMAL(10, 2),
                    closing_line DECIMAL(10, 2),
                    clv_cents DECIMAL(10, 2),
                    profit_loss DECIMAL(10, 2),
                    placed_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    settled_at TIMESTAMP WITH TIME ZONE,
                    notes TEXT,
                    model_pick_id INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample user bets data
        print("Generating sample user bets data...")
        
        user_bets = [
            # NBA Player Props Bets
            {
                'sport_id': 30,
                'game_id': 662,
                'player_id': 91,
                'market_type': 'points',
                'side': 'over',
                'line_value': 24.5,
                'sportsbook': 'DraftKings',
                'opening_odds': -110,
                'stake': 110.00,
                'status': 'won',
                'actual_value': 28.0,
                'closing_odds': -105,
                'closing_line': 24.5,
                'clv_cents': 5.0,
                'profit_loss': 100.00,
                'placed_at': datetime.now(timezone.utc) - timedelta(days=1, hours=19),
                'settled_at': datetime.now(timezone.utc) - timedelta(days=1, hours=22),
                'notes': 'LeBron James over 24.5 points - strong matchup vs Warriors',
                'model_pick_id': 1,
                'created_at': datetime.now(timezone.utc) - timedelta(days=1, hours=19),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1, hours=22)
            },
            {
                'sport_id': 30,
                'game_id': 662,
                'player_id': 92,
                'market_type': 'points',
                'side': 'over',
                'line_value': 28.5,
                'sportsbook': 'FanDuel',
                'opening_odds': -110,
                'stake': 55.00,
                'status': 'lost',
                'actual_value': 26.0,
                'closing_odds': -115,
                'closing_line': 28.5,
                'clv_cents': -5.0,
                'profit_loss': -55.00,
                'placed_at': datetime.now(timezone.utc) - timedelta(days=1, hours=18),
                'settled_at': datetime.now(timezone.utc) - timedelta(days=1, hours=22),
                'notes': 'Steph Curry over 28.5 points - tough defense from Lakers',
                'model_pick_id': 2,
                'created_at': datetime.now(timezone.utc) - timedelta(days=1, hours=18),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1, hours=22)
            },
            {
                'sport_id': 30,
                'game_id': 663,
                'player_id': 101,
                'market_type': 'rebounds',
                'side': 'over',
                'line_value': 8.5,
                'sportsbook': 'BetMGM',
                'opening_odds': -110,
                'stake': 110.00,
                'status': 'won',
                'actual_value': 12.0,
                'closing_odds': -108,
                'closing_line': 8.5,
                'clv_cents': 2.0,
                'profit_loss': 100.00,
                'placed_at': datetime.now(timezone.utc) - timedelta(days=2, hours=20),
                'settled_at': datetime.now(timezone.utc) - timedelta(days=2, hours=23),
                'notes': 'Kevin Durant over 8.5 rebounds - facing smaller forwards',
                'model_pick_id': 3,
                'created_at': datetime.now(timezone.utc) - timedelta(days=2, hours=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=2, hours=23)
            },
            {
                'sport_id': 30,
                'game_id': 663,
                'player_id': 102,
                'market_type': 'assists',
                'side': 'over',
                'line_value': 6.5,
                'sportsbook': 'Caesars',
                'opening_odds': -110,
                'stake': 220.00,
                'status': 'won',
                'actual_value': 8.0,
                'closing_odds': -112,
                'closing_line': 6.5,
                'clv_cents': -2.0,
                'profit_loss': 200.00,
                'placed_at': datetime.now(timezone.utc) - timedelta(days=2, hours=19),
                'settled_at': datetime.now(timezone.utc) - timedelta(days=2, hours=23),
                'notes': 'Devin Booker over 6.5 assists - playmaking role vs Nuggets',
                'model_pick_id': 4,
                'created_at': datetime.now(timezone.utc) - timedelta(days=2, hours=19),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=2, hours=23)
            },
            # NFL Player Props Bets
            {
                'sport_id': 1,
                'game_id': 664,
                'player_id': 111,
                'market_type': 'passing_yards',
                'side': 'over',
                'line_value': 285.5,
                'sportsbook': 'PointsBet',
                'opening_odds': -110,
                'stake': 110.00,
                'status': 'won',
                'actual_value': 312.0,
                'closing_odds': -105,
                'closing_line': 285.5,
                'clv_cents': 5.0,
                'profit_loss': 100.00,
                'placed_at': datetime.now(timezone.utc) - timedelta(days=3, hours=17),
                'settled_at': datetime.now(timezone.utc) - timedelta(days=3, hours=21),
                'notes': 'Patrick Mahomes over 285.5 yards - great matchup vs Bills',
                'model_pick_id': 5,
                'created_at': datetime.now(timezone.utc) - timedelta(days=3, hours=17),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=3, hours=21)
            },
            {
                'sport_id': 1,
                'game_id': 664,
                'player_id': 112,
                'market_type': 'rushing_yards',
                'side': 'over',
                'line_value': 85.5,
                'sportsbook': 'Bet365',
                'opening_odds': -110,
                'stake': 55.00,
                'status': 'lost',
                'actual_value': 78.0,
                'closing_odds': -115,
                'closing_line': 85.5,
                'clv_cents': -5.0,
                'profit_loss': -55.00,
                'placed_at': datetime.now(timezone.utc) - timedelta(days=3, hours=16),
                'settled_at': datetime.now(timezone.utc) - timedelta(days=3, hours=21),
                'notes': 'Josh Allen over 85.5 yards - tough Chiefs defense',
                'model_pick_id': 6,
                'created_at': datetime.now(timezone.utc) - timedelta(days=3, hours=16),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=3, hours=21)
            },
            {
                'sport_id': 1,
                'game_id': 665,
                'player_id': 113,
                'market_type': 'receiving_yards',
                'side': 'over',
                'line_value': 75.5,
                'sportsbook': 'DraftKings',
                'opening_odds': -110,
                'stake': 110.00,
                'status': 'won',
                'actual_value': 89.0,
                'closing_odds': -108,
                'closing_line': 75.5,
                'clv_cents': 2.0,
                'profit_loss': 100.00,
                'placed_at': datetime.now(timezone.utc) - timedelta(days=4, hours=18),
                'settled_at': datetime.now(timezone.utc) - timedelta(days=4, hours=22),
                'notes': 'Travis Kelce over 75.5 yards - Mahomes favorite target',
                'model_pick_id': 7,
                'created_at': datetime.now(timezone.utc) - timedelta(days=4, hours=18),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=4, hours=22)
            },
            {
                'sport_id': 1,
                'game_id': 665,
                'player_id': 114,
                'market_type': 'interceptions',
                'side': 'over',
                'line_value': 0.5,
                'sportsbook': 'FanDuel',
                'opening_odds': +140,
                'stake': 50.00,
                'status': 'lost',
                'actual_value': 0.0,
                'closing_odds': +150,
                'closing_line': 0.5,
                'clv_cents': -10.0,
                'profit_loss': -50.00,
                'placed_at': datetime.now(timezone.utc) - timedelta(days=4, hours=17),
                'settled_at': datetime.now(timezone.utc) - timedelta(days=4, hours=22),
                'notes': 'Micah Parsons over 0.5 interceptions - long shot bet',
                'model_pick_id': 8,
                'created_at': datetime.now(timezone.utc) - timedelta(days=4, hours=17),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=4, hours=22)
            },
            # MLB Player Props Bets
            {
                'sport_id': 2,
                'game_id': 666,
                'player_id': 201,
                'market_type': 'home_runs',
                'side': 'over',
                'line_value': 1.5,
                'sportsbook': 'BetMGM',
                'opening_odds': -110,
                'stake': 110.00,
                'status': 'won',
                'actual_value': 2.0,
                'closing_odds': -105,
                'closing_line': 1.5,
                'clv_cents': 5.0,
                'profit_loss': 100.00,
                'placed_at': datetime.now(timezone.utc) - timedelta(days=5, hours=19),
                'settled_at': datetime.now(timezone.utc) - timedelta(days=5, hours=23),
                'notes': 'Aaron Judge over 1.5 HRs - facing struggling pitcher',
                'model_pick_id': 9,
                'created_at': datetime.now(timezone.utc) - timedelta(days=5, hours=19),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=5, hours=23)
            },
            {
                'sport_id': 2,
                'game_id': 666,
                'player_id': 202,
                'market_type': 'strikeouts',
                'side': 'over',
                'line_value': 7.5,
                'sportsbook': 'Caesars',
                'opening_odds': -110,
                'stake': 110.00,
                'status': 'won',
                'actual_value': 9.0,
                'closing_odds': -108,
                'closing_line': 7.5,
                'clv_cents': 2.0,
                'profit_loss': 100.00,
                'placed_at': datetime.now(timezone.utc) - timedelta(days=5, hours=18),
                'settled_at': datetime.now(timezone.utc) - timedelta(days=5, hours=23),
                'notes': 'Gerrit Cole over 7.5 strikeouts - dominant form',
                'model_pick_id': 10,
                'created_at': datetime.now(timezone.utc) - timedelta(days=5, hours=18),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=5, hours=23)
            },
            {
                'sport_id': 2,
                'game_id': 667,
                'player_id': 203,
                'market_type': 'hits',
                'side': 'over',
                'line_value': 1.5,
                'sportsbook': 'PointsBet',
                'opening_odds': -110,
                'stake': 55.00,
                'status': 'lost',
                'actual_value': 1.0,
                'closing_odds': -115,
                'closing_line': 1.5,
                'clv_cents': -5.0,
                'profit_loss': -55.00,
                'placed_at': datetime.now(timezone.utc) - timedelta(days=6, hours=20),
                'settled_at': datetime.now(timezone.utc) - timedelta(days=6, hours=0),
                'notes': 'Mike Trout over 1.5 hits - off day at the plate',
                'model_pick_id': 11,
                'created_at': datetime.now(timezone.utc) - timedelta(days=6, hours=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=6, hours=0)
            },
            # NHL Player Props Bets
            {
                'sport_id': 53,
                'game_id': 668,
                'player_id': 301,
                'market_type': 'points',
                'side': 'over',
                'line_value': 1.5,
                'sportsbook': 'Bet365',
                'opening_odds': -110,
                'stake': 110.00,
                'status': 'won',
                'actual_value': 2.0,
                'closing_odds': -105,
                'closing_line': 1.5,
                'clv_cents': 5.0,
                'profit_loss': 100.00,
                'placed_at': datetime.now(timezone.utc) - timedelta(days=7, hours=19),
                'settled_at': datetime.now(timezone.utc) - timedelta(days=7, hours=23),
                'notes': 'Connor McDavid over 1.5 points - always dangerous',
                'model_pick_id': 12,
                'created_at': datetime.now(timezone.utc) - timedelta(days=7, hours=19),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7, hours=23)
            },
            {
                'sport_id': 53,
                'game_id': 668,
                'player_id': 302,
                'market_type': 'goals',
                'side': 'over',
                'line_value': 0.5,
                'sportsbook': 'DraftKings',
                'opening_odds': -110,
                'stake': 110.00,
                'status': 'lost',
                'actual_value': 0.0,
                'closing_odds': -115,
                'closing_line': 0.5,
                'clv_cents': -5.0,
                'profit_loss': -110.00,
                'placed_at': datetime.now(timezone.utc) - timedelta(days=7, hours=18),
                'settled_at': datetime.now(timezone.utc) - timedelta(days=7, hours=23),
                'notes': 'Nathan MacKinnon over 0.5 goals - held scoreless',
                'model_pick_id': 13,
                'created_at': datetime.now(timezone.utc) - timedelta(days=7, hours=18),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7, hours=23)
            },
            # Pending Bets
            {
                'sport_id': 30,
                'game_id': 669,
                'player_id': 105,
                'market_type': 'points',
                'side': 'over',
                'line_value': 22.5,
                'sportsbook': 'FanDuel',
                'opening_odds': -110,
                'stake': 220.00,
                'status': 'pending',
                'actual_value': None,
                'closing_odds': None,
                'closing_line': None,
                'clv_cents': None,
                'profit_loss': None,
                'placed_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'settled_at': None,
                'notes': 'Jayson Tatum over 22.5 points - game in progress',
                'model_pick_id': 14,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'sport_id': 1,
                'game_id': 670,
                'player_id': 115,
                'market_type': 'passing_touchdowns',
                'side': 'over',
                'line_value': 1.5,
                'sportsbook': 'BetMGM',
                'opening_odds': -110,
                'stake': 110.00,
                'status': 'pending',
                'actual_value': None,
                'closing_odds': None,
                'closing_line': None,
                'clv_cents': None,
                'profit_loss': None,
                'placed_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'settled_at': None,
                'notes': 'Joe Burrow over 1.5 TDs - primetime game',
                'model_pick_id': 15,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=1)
            },
            {
                'sport_id': 2,
                'game_id': 671,
                'player_id': 204,
                'market_type': 'batting_average',
                'side': 'over',
                'line_value': 0.275,
                'sportsbook': 'Caesars',
                'opening_odds': -110,
                'stake': 55.00,
                'status': 'pending',
                'actual_value': None,
                'closing_odds': None,
                'closing_line': None,
                'clv_cents': None,
                'profit_loss': None,
                'placed_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'settled_at': None,
                'notes': 'Shohei Ohtani over 0.275 BA - multi-threat player',
                'model_pick_id': 16,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=3)
            }
        ]
        
        # Insert user bets data
        for bet in user_bets:
            await conn.execute("""
                INSERT INTO user_bets (
                    sport_id, game_id, player_id, market_type, side, line_value, sportsbook,
                    opening_odds, stake, status, actual_value, closing_odds, closing_line,
                    clv_cents, profit_loss, placed_at, settled_at, notes, model_pick_id,
                    created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21)
            """, 
                bet['sport_id'],
                bet['game_id'],
                bet['player_id'],
                bet['market_type'],
                bet['side'],
                bet['line_value'],
                bet['sportsbook'],
                bet['opening_odds'],
                bet['stake'],
                bet['status'],
                bet['actual_value'],
                bet['closing_odds'],
                bet['closing_line'],
                bet['clv_cents'],
                bet['profit_loss'],
                bet['placed_at'],
                bet['settled_at'],
                bet['notes'],
                bet['model_pick_id'],
                bet['created_at'],
                bet['updated_at']
            )
        
        print("Sample user bets data populated successfully")
        
        # Get user bets statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_bets,
                COUNT(DISTINCT sport_id) as unique_sports,
                COUNT(DISTINCT game_id) as unique_games,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(DISTINCT sportsbook) as unique_sportsbooks,
                COUNT(DISTINCT market_type) as unique_market_types,
                COUNT(CASE WHEN status = 'won' THEN 1 END) as won_bets,
                COUNT(CASE WHEN status = 'lost' THEN 1 END) as lost_bets,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_bets,
                SUM(stake) as total_stake,
                SUM(profit_loss) as total_profit_loss,
                AVG(stake) as avg_stake,
                AVG(profit_loss) as avg_profit_loss,
                ROUND(COUNT(CASE WHEN status = 'won' THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN status IN ('won', 'lost') THEN 1 END), 0), 2) as win_rate_percentage,
                SUM(clv_cents) as total_clv_cents,
                AVG(clv_cents) as avg_clv_cents
            FROM user_bets
        """)
        
        print(f"\nUser Bets Statistics:")
        print(f"  Total Bets: {stats['total_bets']}")
        print(f"  Unique Sports: {stats['unique_sports']}")
        print(f"  Unique Games: {stats['unique_games']}")
        print(f"  Unique Players: {stats['unique_players']}")
        print(f"  Unique Sportsbooks: {stats['unique_sportsbooks']}")
        print(f"  Unique Market Types: {stats['unique_market_types']}")
        print(f"  Won Bets: {stats['won_bets']}")
        print(f"  Lost Bets: {stats['lost_bets']}")
        print(f"  Pending Bets: {stats['pending_bets']}")
        print(f"  Total Stake: ${stats['total_stake']:.2f}")
        print(f"  Total Profit/Loss: ${stats['total_profit_loss']:.2f}")
        print(f"  Avg Stake: ${stats['avg_stake']:.2f}")
        print(f"  Avg Profit/Loss: ${stats['avg_profit_loss']:.2f}")
        print(f"  Win Rate: {stats['win_rate_percentage']:.2f}%")
        print(f"  Total CLV Cents: {stats['total_clv_cents']:.2f}")
        print(f"  Avg CLV Cents: {stats['avg_clv_cents']:.2f}")
        
        # Get bets by sport
        by_sport = await conn.fetch("""
            SELECT 
                sport_id,
                COUNT(*) as total_bets,
                COUNT(CASE WHEN status = 'won' THEN 1 END) as won_bets,
                COUNT(CASE WHEN status = 'lost' THEN 1 END) as lost_bets,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_bets,
                SUM(stake) as total_stake,
                SUM(profit_loss) as total_profit_loss,
                ROUND(COUNT(CASE WHEN status = 'won' THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN status IN ('won', 'lost') THEN 1 END), 0), 2) as win_rate_percentage,
                AVG(clv_cents) as avg_clv_cents
            FROM user_bets
            GROUP BY sport_id
            ORDER BY total_bets DESC
        """)
        
        print(f"\nBets by Sport:")
        sport_mapping = {
            1: "NFL",
            2: "MLB",
            30: "NBA",
            53: "NHL"
        }
        
        for sport in by_sport:
            sport_name = sport_mapping.get(sport['sport_id'], f"Sport {sport['sport_id']}")
            print(f"  {sport_name}:")
            print(f"    Total Bets: {sport['total_bets']}")
            print(f"    Won: {sport['won_bets']}, Lost: {sport['lost_bets']}, Pending: {sport['pending_bets']}")
            print(f"    Total Stake: ${sport['total_stake']:.2f}")
            print(f"    Total P/L: ${sport['total_profit_loss']:.2f}")
            print(f"    Win Rate: {sport['win_rate_percentage']:.2f}%")
            print(f"    Avg CLV: {sport['avg_clv_cents']:.2f}")
        
        # Get bets by sportsbook
        by_sportsbook = await conn.fetch("""
            SELECT 
                sportsbook,
                COUNT(*) as total_bets,
                COUNT(CASE WHEN status = 'won' THEN 1 END) as won_bets,
                COUNT(CASE WHEN status = 'lost' THEN 1 END) as lost_bets,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_bets,
                SUM(stake) as total_stake,
                SUM(profit_loss) as total_profit_loss,
                ROUND(COUNT(CASE WHEN status = 'won' THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN status IN ('won', 'lost') THEN 1 END), 0), 2) as win_rate_percentage,
                AVG(clv_cents) as avg_clv_cents
            FROM user_bets
            GROUP BY sportsbook
            ORDER BY total_bets DESC
        """)
        
        print(f"\nBets by Sportsbook:")
        for sportsbook in by_sportsbook:
            print(f"  {sportsbook['sportsbook']}:")
            print(f"    Total Bets: {sportsbook['total_bets']}")
            print(f"    Won: {sportsbook['won_bets']}, Lost: {sportsbook['lost_bets']}, Pending: {sportsbook['pending_bets']}")
            print(f"    Total Stake: ${sportsbook['total_stake']:.2f}")
            print(f"    Total P/L: ${sportsbook['total_profit_loss']:.2f}")
            print(f"    Win Rate: {sportsbook['win_rate_percentage']:.2f}%")
            print(f"    Avg CLV: {sportsbook['avg_clv_cents']:.2f}")
        
        # Get bets by market type
        by_market_type = await conn.fetch("""
            SELECT 
                market_type,
                COUNT(*) as total_bets,
                COUNT(CASE WHEN status = 'won' THEN 1 END) as won_bets,
                COUNT(CASE WHEN status = 'lost' THEN 1 END) as lost_bets,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_bets,
                SUM(stake) as total_stake,
                SUM(profit_loss) as total_profit_loss,
                ROUND(COUNT(CASE WHEN status = 'won' THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN status IN ('won', 'lost') THEN 1 END), 0), 2) as win_rate_percentage,
                AVG(clv_cents) as avg_clv_cents
            FROM user_bets
            GROUP BY market_type
            ORDER BY total_bets DESC
        """)
        
        print(f"\nBets by Market Type:")
        for market in by_market_type:
            print(f"  {market['market_type']}:")
            print(f"    Total Bets: {market['total_bets']}")
            print(f"    Won: {market['won_bets']}, Lost: {market['lost_bets']}, Pending: {market['pending_bets']}")
            print(f"    Total Stake: ${market['total_stake']:.2f}")
            print(f"    Total P/L: ${market['total_profit_loss']:.2f}")
            print(f"    Win Rate: {market['win_rate_percentage']:.2f}%")
            print(f"    Avg CLV: {market['avg_clv_cents']:.2f}")
        
        # Recent bets
        recent = await conn.fetch("""
            SELECT * FROM user_bets 
            ORDER BY placed_at DESC, created_at DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent User Bets:")
        for bet in recent:
            sport_name = sport_mapping.get(bet['sport_id'], f"Sport {bet['sport_id']}")
            print(f"  - {bet['player_id']} {bet['market_type']} {bet['side']} {bet['line_value']}")
            print(f"    Sport: {sport_name}, Sportsbook: {bet['sportsbook']}")
            print(f"    Stake: ${bet['stake']:.2f}, Odds: {bet['opening_odds']}")
            print(f"    Status: {bet['status']}")
            if bet['status'] in ['won', 'lost']:
                print(f"    P/L: ${bet['profit_loss']:.2f}, CLV: {bet['clv_cents']:.2f}")
            print(f"    Placed: {bet['placed_at']}")
            if bet['settled_at']:
                print(f"    Settled: {bet['settled_at']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_user_bets())
