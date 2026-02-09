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
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
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
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2)
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
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2)
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
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'game_id': 662,
                'pick_type': 'player_prop',
                'player_name': 'Stephen Curry',
                'stat_type': 'three_pointers',
                'line': 4.5,
                'odds': -110,
                'model_probability': 0.5700,
                'implied_probability': 0.5238,
                'ev_percentage': 8.84,
                'confidence': 80.0,
                'hit_rate': 61.7,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'game_id': 662,
                'pick_type': 'player_prop',
                'player_name': 'Kevin Durant',
                'stat_type': 'points',
                'line': 26.5,
                'odds': -108,
                'model_probability': 0.5900,
                'implied_probability': 0.5195,
                'ev_percentage': 13.58,
                'confidence': 86.0,
                'hit_rate': 63.2,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            # NFL Picks - Medium Confidence
            {
                'game_id': 664,
                'pick_type': 'player_prop',
                'player_name': 'Patrick Mahomes',
                'stat_type': 'passing_yards',
                'line': 285.5,
                'odds': -110,
                'model_probability': 0.5800,
                'implied_probability': 0.5238,
                'ev_percentage': 10.75,
                'confidence': 84.0,
                'hit_rate': 63.2,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=3)
            },
            {
                'game_id': 664,
                'pick_type': 'player_prop',
                'player_name': 'Patrick Mahomes',
                'stat_type': 'passing_touchdowns',
                'line': 2.5,
                'odds': -105,
                'model_probability': 0.6100,
                'implied_probability': 0.5122,
                'ev_percentage': 19.09,
                'confidence': 87.0,
                'hit_rate': 65.5,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=3)
            },
            {
                'game_id': 664,
                'pick_type': 'player_prop',
                'player_name': 'Josh Allen',
                'stat_type': 'passing_yards',
                'line': 265.5,
                'odds': -115,
                'model_probability': 0.5500,
                'implied_probability': 0.5349,
                'ev_percentage': 2.78,
                'confidence': 75.0,
                'hit_rate': 58.9,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=3)
            },
            {
                'game_id': 664,
                'pick_type': 'player_prop',
                'player_name': 'Josh Allen',
                'stat_type': 'rushing_yards',
                'line': 35.5,
                'odds': -120,
                'model_probability': 0.5700,
                'implied_probability': 0.5455,
                'ev_percentage': 4.48,
                'confidence': 78.0,
                'hit_rate': 60.3,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=3)
            },
            {
                'game_id': 664,
                'pick_type': 'player_prop',
                'player_name': 'Justin Herbert',
                'stat_type': 'passing_yards',
                'line': 275.5,
                'odds': -110,
                'model_probability': 0.5400,
                'implied_probability': 0.5238,
                'ev_percentage': 3.12,
                'confidence': 76.0,
                'hit_rate': 57.8,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=3)
            },
            # MLB Picks - High Confidence
            {
                'game_id': 666,
                'pick_type': 'player_prop',
                'player_name': 'Aaron Judge',
                'stat_type': 'home_runs',
                'line': 1.5,
                'odds': -110,
                'model_probability': 0.5900,
                'implied_probability': 0.5238,
                'ev_percentage': 12.61,
                'confidence': 85.0,
                'hit_rate': 62.9,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=4)
            },
            {
                'game_id': 666,
                'pick_type': 'player_prop',
                'player_name': 'Aaron Judge',
                'stat_type': 'rbis',
                'line': 2.5,
                'odds': -105,
                'model_probability': 0.5800,
                'implied_probability': 0.5122,
                'ev_percentage': 13.18,
                'confidence': 83.0,
                'hit_rate': 61.5,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=4)
            },
            {
                'game_id': 666,
                'pick_type': 'player_prop',
                'player_name': 'Mike Trout',
                'stat_type': 'hits',
                'line': 1.5,
                'odds': -115,
                'model_probability': 0.6200,
                'implied_probability': 0.5349,
                'ev_percentage': 15.92,
                'confidence': 88.0,
                'hit_rate': 64.2,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=4)
            },
            {
                'game_id': 666,
                'pick_type': 'player_prop',
                'player_name': 'Shohei Ohtani',
                'stat_type': 'strikeouts',
                'line': 7.5,
                'odds': -110,
                'model_probability': 0.5700,
                'implied_probability': 0.5238,
                'ev_percentage': 8.84,
                'confidence': 81.0,
                'hit_rate': 62.0,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=4)
            },
            {
                'game_id': 666,
                'pick_type': 'player_prop',
                'player_name': 'Shohei Ohtani',
                'stat_type': 'hits',
                'line': 1.5,
                'odds': -108,
                'model_probability': 0.5600,
                'implied_probability': 0.5195,
                'ev_percentage': 7.70,
                'confidence': 79.0,
                'hit_rate': 60.8,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=4)
            },
            # NHL Picks - Medium Confidence
            {
                'game_id': 668,
                'pick_type': 'player_prop',
                'player_name': 'Connor McDavid',
                'stat_type': 'points',
                'line': 1.5,
                'odds': -110,
                'model_probability': 0.5800,
                'implied_probability': 0.5238,
                'ev_percentage': 10.75,
                'confidence': 83.0,
                'hit_rate': 62.2,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=5)
            },
            {
                'game_id': 668,
                'pick_type': 'player_prop',
                'player_name': 'Connor McDavid',
                'stat_type': 'assists',
                'line': 1.5,
                'odds': -115,
                'model_probability': 0.5600,
                'implied_probability': 0.5349,
                'ev_percentage': 4.68,
                'confidence': 77.0,
                'hit_rate': 60.1,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=5)
            },
            {
                'game_id': 668,
                'pick_type': 'player_prop',
                'player_name': 'Nathan MacKinnon',
                'stat_type': 'points',
                'line': 1.5,
                'odds': -105,
                'model_probability': 0.5700,
                'implied_probability': 0.5122,
                'ev_percentage': 11.18,
                'confidence': 82.0,
                'hit_rate': 61.8,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=5)
            },
            # Recent Picks - High EV
            {
                'game_id': 662,
                'pick_type': 'player_prop',
                'player_name': 'LeBron James',
                'stat_type': 'points',
                'line': 25.0,
                'odds': -108,
                'model_probability': 0.6100,
                'implied_probability': 0.5195,
                'ev_percentage': 17.40,
                'confidence': 89.0,
                'hit_rate': 64.1,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 662,
                'pick_type': 'player_prop',
                'player_name': 'Stephen Curry',
                'stat_type': 'points',
                'line': 29.0,
                'odds': -112,
                'model_probability': 0.6300,
                'implied_probability': 0.5283,
                'ev_percentage': 19.28,
                'confidence': 90.0,
                'hit_rate': 65.2,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=30)
            },
            {
                'game_id': 664,
                'pick_type': 'player_prop',
                'player_name': 'Patrick Mahomes',
                'stat_type': 'passing_touchdowns',
                'line': 2.5,
                'odds': -108,
                'model_probability': 0.6300,
                'implied_probability': 0.5195,
                'ev_percentage': 21.28,
                'confidence': 91.0,
                'hit_rate': 66.8,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=15)
            },
            {
                'game_id': 666,
                'pick_type': 'player_prop',
                'player_name': 'Aaron Judge',
                'stat_type': 'home_runs',
                'line': 1.5,
                'odds': -105,
                'model_probability': 0.6100,
                'implied_probability': 0.5122,
                'ev_percentage': 19.09,
                'confidence': 87.0,
                'hit_rate': 63.5,
                'created_at': datetime.now(timezone.utc) - timedelta(minutes=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=10)
            },
            {
                'game_id': 668,
                'pick_type': 'player_prop',
                'player_name': 'Connor McDavid',
                'stat_type': 'points',
                'line': 1.5,
                'odds': -108,
                'model_probability': 0.6000,
                'implied_probability': 0.5195,
                'ev_percentage': 15.40,
                'confidence': 85.0,
                'hit_rate': 62.8,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
        ]
        
        # Insert picks data
        for pick in picks:
            await conn.execute("""
                INSERT INTO picks (
                    game_id, pick_type, player_name, stat_type, line, odds, model_probability,
                    implied_probability, ev_percentage, confidence, hit_rate, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
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
                pick['updated_at']
            )
        
        print("Sample picks data populated successfully")
        
        # Get picks statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_picks,
                COUNT(DISTINCT game_id) as unique_games,
                COUNT(DISTINCT player_name) as unique_players,
                COUNT(DISTINCT stat_type) as unique_stat_types,
                COUNT(DISTINCT pick_type) as unique_pick_types,
                AVG(line) as avg_line,
                AVG(odds) as avg_odds,
                AVG(model_probability) as avg_model_prob,
                AVG(implied_probability) as avg_implied_prob,
                AVG(ev_percentage) as avg_ev,
                AVG(confidence) as avg_confidence,
                AVG(hit_rate) as avg_hit_rate,
                COUNT(CASE WHEN ev_percentage > 5.0 THEN 1 END) as high_ev_picks,
                COUNT(CASE WHEN confidence >= 80.0 THEN 1 END) as high_confidence_picks,
                COUNT(CASE WHEN hit_rate >= 60.0 THEN 1 END) as high_hit_rate_picks
            FROM picks
        """)
        
        print(f"\nPicks Statistics:")
        print(f"  Total Picks: {stats['total_picks']}")
        print(f"  Unique Games: {stats['unique_games']}")
        print(f"  Unique Players: {stats['unique_players']}")
        print(f"  Unique Stat Types: {stats['unique_stat_types']}")
        print(f"  Unique Pick Types: {stats['unique_pick_types']}")
        print(f"  Avg Line: {stats['avg_line']:.2f}")
        print(f"  Avg Odds: {stats['avg_odds']:.0f}")
        print(f"  Avg Model Probability: {stats['avg_model_prob']:.4f}")
        print(f"  Avg Implied Probability: {stats['avg_implied_prob']:.4f}")
        print(f"  Avg EV: {stats['avg_ev']:.2f}%")
        print(f"  Avg Confidence: {stats['avg_confidence']:.1f}%")
        print(f"  Avg Hit Rate: {stats['avg_hit_rate']:.1f}%")
        print(f"  High EV Picks: {stats['high_ev_picks']}")
        print(f"  High Confidence Picks: {stats['high_confidence_picks']}")
        print(f"  High Hit Rate Picks: {stats['high_hit_rate_picks']}")
        
        # Get picks by player
        by_player = await conn.fetch("""
            SELECT 
                player_name,
                COUNT(*) as total_picks,
                AVG(ev_percentage) as avg_ev,
                AVG(confidence) as avg_confidence,
                AVG(hit_rate) as avg_hit_rate,
                AVG(model_probability) as avg_model_prob,
                AVG(implied_probability) as avg_implied_prob,
                COUNT(CASE WHEN ev_percentage > 5.0 THEN 1 END) as high_ev_picks,
                COUNT(CASE WHEN confidence >= 80.0 THEN 1 END) as high_confidence_picks
            FROM picks
            GROUP BY player_name
            ORDER BY avg_ev DESC
            LIMIT 10
        """)
        
        print(f"\nTop 10 Players by EV:")
        for player in by_player:
            print(f"  {player}:")
            print(f"    Total Picks: {player['total_picks']}")
            print(f"    Avg EV: {player['avg_ev']:.2f}%")
            print(f"    Avg Confidence: {player['avg_confidence']:.1f}%")
            print(f"    Avg Hit Rate: {player['avg_hit_rate']:.1f}%")
            print(f"    High EV Picks: {player['high_ev_picks']}")
            print(f"    High Confidence Picks: {player['high_confidence_picks']}")
        
        # Get picks by stat type
        by_stat_type = await conn.fetch("""
            SELECT 
                stat_type,
                COUNT(*) as total_picks,
                AVG(ev_percentage) as avg_ev,
                AVG(confidence) as avg_confidence,
                AVG(hit_rate) as avg_hit_rate,
                AVG(model_probability) as avg_model_prob,
                AVG(implied_probability) as avg_implied_prob,
                COUNT(CASE WHEN ev_percentage > 5.0 THEN 1 END) as high_ev_picks
            FROM picks
            GROUP BY stat_type
            ORDER BY avg_ev DESC
        """)
        
        print(f"\nPicks by Stat Type:")
        for stat in by_stat_type:
            print(f"  {stat}:")
            print(f"    Total Picks: {stat['total_picks']}")
            print(f"    Avg EV: {stat['avg_ev']:.2f}%")
            print(f"    Avg Confidence: {stat['avg_confidence']:.1f}%")
            print(f"    Avg Hit Rate: {stat['avg_hit_rate']:.1f}%")
            print(f"    High EV Picks: {stat['high_ev_picks']}")
        
        # Get high EV picks
        high_ev = await conn.fetch("""
            SELECT * FROM picks 
            WHERE ev_percentage > 10.0
            ORDER BY ev_percentage DESC
            LIMIT 10
        """)
        
        print(f"\nTop 10 High EV Picks:")
        for pick in high_ev:
            print(f"  - {pick['player_name']}: {pick['stat_type']} {pick['line']}")
            print(f"    EV: {pick['ev_percentage']:.2f}%, Confidence: {pick['confidence']:.1f}%")
            print(f"    Model: {pick['model_probability']:.4f}, Implied: {pick['implied_probability']:.4f}")
            print(f"    Odds: {pick['odds']}, Hit Rate: {pick['hit_rate']:.1f}%")
            print(f"    Created: {pick['created_at']}")
        
        # Get recent picks
        recent = await conn.fetch("""
            SELECT * FROM picks 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent Picks:")
        for pick in recent:
            print(f"  - {pick['player_name']}: {pick['stat_type']} {pick['line']}")
            print(f"    EV: {pick['ev_percentage']:.2f}%, Confidence: {pick['confidence']:.1f}%")
            print(f"    Model: {pick['model_probability']:.4f}, Implied: {pick['implied_probability']:.4f}")
            print(f"    Odds: {pick['odds']}, Hit Rate: {pick['hit_rate']:.1f}%")
            print(f"    Created: {pick['created_at']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_picks())
