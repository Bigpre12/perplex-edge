#!/usr/bin/env python3
"""
POPULATE PICKS - Initialize and populate the picks table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_picks():
    """Populate picks table with initial data"""
    
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
                WHERE table_name = 'picks'
            )
        """)
        
        if not table_check:
            print("Creating picks table...")
            await conn.execute("""
                CREATE TABLE picks (
                    id SERIAL PRIMARY KEY,
                    game_id INTEGER NOT NULL,
                    pick_type VARCHAR(50) NOT NULL,
                    player_name VARCHAR(100) NOT NULL,
                    stat_type VARCHAR(50) NOT NULL,
                    line DECIMAL(10, 2) NOT NULL,
                    odds INTEGER NOT NULL,
                    model_probability DECIMAL(5, 4) NOT NULL,
                    implied_probability DECIMAL(5, 4) NOT NULL,
                    ev_percentage DECIMAL(5, 2),
                    confidence DECIMAL(5, 2),
                    hit_rate DECIMAL(5, 2),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    closing_odds DECIMAL(10, 4),
                    clv_percentage DECIMAL(10, 4),
                    roi_percentage DECIMAL(10, 4),
                    opening_odds DECIMAL(10, 4),
                    line_movement DECIMAL(10, 4),
                    sharp_money_indicator DECIMAL(10, 4),
                    best_book_odds DECIMAL(10, 4),
                    best_book_name VARCHAR(50),
                    ev_improvement DECIMAL(10, 4)
                )
            """)
            print("Table created")
        else:
             # Add columns if they don't exist (migrations)
            print("Checking for new columns...")
            columns = [
                ("closing_odds", "DECIMAL(10, 4)"),
                ("clv_percentage", "DECIMAL(10, 4)"),
                ("roi_percentage", "DECIMAL(10, 4)"),
                ("opening_odds", "DECIMAL(10, 4)"),
                ("line_movement", "DECIMAL(10, 4)"),
                ("sharp_money_indicator", "DECIMAL(10, 4)"),
                ("best_book_odds", "DECIMAL(10, 4)"),
                ("best_book_name", "VARCHAR(50)"),
                ("ev_improvement", "DECIMAL(10, 4)")
            ]
            for col_name, col_type in columns:
                 await conn.execute(f"ALTER TABLE picks ADD COLUMN IF NOT EXISTS {col_name} {col_type}")

        
        # Generate sample picks data
        print("Generating sample picks data...")
        
        picks = [
            # NBA Picks - High Confidence
            {
                'game_id': 662,
                'pick_type': 'player_prop',
                'player_name': 'LeBron James',
                'stat_type': 'points',
                'line': 24.5,
                'odds': -110,
                'model_probability': 0.5800,
                'implied_probability': 0.5238,
                'ev_percentage': 10.75,
                'confidence': 85.0,
                'hit_rate': 62.4,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'closing_odds': -125,
                'clv_percentage': 5.2,
                'roi_percentage': 15.5,
                'opening_odds': -105,
                'line_movement': -20,
                'sharp_money_indicator': 0.8,
                'best_book_odds': -108,
                'best_book_name': 'DraftKings',
                'ev_improvement': 2.5
            },
            {
                'game_id': 662,
                'pick_type': 'player_prop',
                'player_name': 'LeBron James',
                'stat_type': 'rebounds',
                'line': 7.5,
                'odds': -105,
                'model_probability': 0.5600,
                'implied_probability': 0.5122,
                'ev_percentage': 9.34,
                'confidence': 82.0,
                'hit_rate': 61.1,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'closing_odds': -115,
                'clv_percentage': 3.1,
                'roi_percentage': 8.2,
                'opening_odds': -100,
                'line_movement': -15,
                'sharp_money_indicator': 0.6,
                'best_book_odds': -102,
                'best_book_name': 'FanDuel',
                'ev_improvement': 1.8
            },
            {
                'game_id': 662,
                'pick_type': 'player_prop',
                'player_name': 'Stephen Curry',
                'stat_type': 'points',
                'line': 28.5,
                'odds': -115,
                'model_probability': 0.6200,
                'implied_probability': 0.5349,
                'ev_percentage': 15.92,
                'confidence': 88.0,
                'hit_rate': 64.0,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'closing_odds': -130,
                'clv_percentage': 6.5,
                'roi_percentage': 18.2,
                'opening_odds': -110,
                'line_movement': -20,
                'sharp_money_indicator': 0.9,
                'best_book_odds': -112,
                'best_book_name': 'BetMGM',
                'ev_improvement': 3.2
            },
            # Add more with Nones or defaults if needed, but for now just updating schema
        ]
        
        # Insert picks data
        for pick in picks:
             # Default CLV values if missing
            closing_odds = pick.get('closing_odds', None)
            clv_percentage = pick.get('clv_percentage', None)
            roi_percentage = pick.get('roi_percentage', None)
            opening_odds = pick.get('opening_odds', None)
            line_movement = pick.get('line_movement', None)
            sharp_money_indicator = pick.get('sharp_money_indicator', None)
            best_book_odds = pick.get('best_book_odds', None)
            best_book_name = pick.get('best_book_name', None)
            ev_improvement = pick.get('ev_improvement', None)

            await conn.execute("""
                INSERT INTO picks (
                    game_id, pick_type, player_name, stat_type, line, odds, model_probability,
                    implied_probability, ev_percentage, confidence, hit_rate, created_at, updated_at,
                    closing_odds, clv_percentage, roi_percentage, opening_odds, line_movement,
                    sharp_money_indicator, best_book_odds, best_book_name, ev_improvement
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22)
            """, 
                pick['game_id'],
                pick['pick_type'],
                pick['player_name'],
                pick['stat_type'],
                pick['line'],
                pick['odds'],
                pick['model_probability'],
                pick['implied_probability'],
                pick['ev_percentage'],
                pick['confidence'],
                pick['hit_rate'],
                pick['created_at'],
                pick['updated_at'],
                closing_odds, clv_percentage, roi_percentage, opening_odds, line_movement,
                sharp_money_indicator, best_book_odds, best_book_name, ev_improvement
            )
        
        print("Sample picks data populated successfully")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_picks())
