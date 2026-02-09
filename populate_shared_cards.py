#!/usr/bin/env python3
"""
POPULATE SHARED CARDS - Initialize and populate the shared_cards table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_shared_cards():
    """Populate shared_cards table with initial data"""
    
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
                WHERE table_name = 'shared_cards'
            )
        """)
        
        if not table_check:
            print("Creating shared_cards table...")
            await conn.execute("""
                CREATE TABLE shared_cards (
                    id SERIAL PRIMARY KEY,
                    platform VARCHAR(50) NOT NULL,
                    sport_id INTEGER NOT NULL,
                    legs JSONB NOT NULL,
                    leg_count INTEGER NOT NULL,
                    total_odds DECIMAL(10, 2) NOT NULL,
                    decimal_odds DECIMAL(10, 2) NOT NULL,
                    parlay_probability DECIMAL(10, 4) NOT NULL,
                    parlay_ev DECIMAL(10, 4) NOT NULL,
                    overall_grade VARCHAR(10) NOT NULL,
                    label VARCHAR(200) NOT NULL,
                    kelly_suggested_units DECIMAL(10, 4),
                    kelly_risk_level VARCHAR(20),
                    view_count INTEGER DEFAULT 0,
                    settled BOOLEAN DEFAULT FALSE,
                    won BOOLEAN,
                    settled_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample shared cards data
        print("Generating sample shared cards data...")
        
        shared_cards = [
            # NBA Parlay Cards
            {
                'platform': 'twitter',
                'sport_id': 30,
                'legs': [
                    {'player': 'LeBron James', 'market': 'points', 'line': 24.5, 'odds': -110},
                    {'player': 'Stephen Curry', 'market': 'points', 'line': 28.5, 'odds': -110},
                    {'player': 'Kevin Durant', 'market': 'points', 'line': 26.5, 'odds': -110}
                ],
                'leg_count': 3,
                'total_odds': 6.00,
                'decimal_odds': 7.00,
                'parlay_probability': 0.1429,
                'parlay_ev': 0.0286,
                'overall_grade': 'A',
                'label': 'NBA Stars Points Parlay - All Over',
                'kelly_suggested_units': 2.5,
                'kelly_risk_level': 'Medium',
                'view_count': 1250,
                'settled': True,
                'won': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(days=1),
                'created_at': datetime.now(timezone.utc) - timedelta(days=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                'platform': 'discord',
                'sport_id': 30,
                'legs': [
                    {'player': 'LeBron James', 'market': 'rebounds', 'line': 7.5, 'odds': -110},
                    {'player': 'Anthony Davis', 'market': 'rebounds', 'line': 10.5, 'odds': -110},
                    {'player': 'Nikola Jokic', 'market': 'rebounds', 'line': 11.5, 'odds': -110}
                ],
                'leg_count': 3,
                'total_odds': 6.00,
                'decimal_odds': 7.00,
                'parlay_probability': 0.1429,
                'parlay_ev': 0.0143,
                'overall_grade': 'B+',
                'label': 'NBA Rebounds Master Parlay',
                'kelly_suggested_units': 1.8,
                'kelly_risk_level': 'Medium',
                'view_count': 890,
                'settled': True,
                'won': False,
                'settled_at': datetime.now(timezone.utc) - timedelta(days=2),
                'created_at': datetime.now(timezone.utc) - timedelta(days=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=2)
            },
            # NFL Parlay Cards
            {
                'platform': 'twitter',
                'sport_id': 1,
                'legs': [
                    {'player': 'Patrick Mahomes', 'market': 'passing_yards', 'line': 285.5, 'odds': -110},
                    {'player': 'Josh Allen', 'market': 'passing_yards', 'line': 265.5, 'odds': -110},
                    {'player': 'Justin Herbert', 'market': 'passing_yards', 'line': 275.5, 'odds': -110}
                ],
                'leg_count': 3,
                'total_odds': 6.00,
                'decimal_odds': 7.00,
                'parlay_probability': 0.1429,
                'parlay_ev': 0.0357,
                'overall_grade': 'A-',
                'label': 'NFL QB Passing Yards Parlay',
                'kelly_suggested_units': 3.2,
                'kelly_risk_level': 'High',
                'view_count': 2100,
                'settled': True,
                'won': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(days=3),
                'created_at': datetime.now(timezone.utc) - timedelta(days=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=3)
            },
            {
                'platform': 'reddit',
                'sport_id': 1,
                'legs': [
                    {'player': 'Christian McCaffrey', 'market': 'rushing_yards', 'line': 85.5, 'odds': -110},
                    {'player': 'Derrick Henry', 'market': 'rushing_yards', 'line': 95.5, 'odds': -110},
                    {'player': 'Jonathan Taylor', 'market': 'rushing_yards', 'line': 90.5, 'odds': -110}
                ],
                'leg_count': 3,
                'total_odds': 6.00,
                'decimal_odds': 7.00,
                'parlay_probability': 0.1429,
                'parlay_ev': 0.0214,
                'overall_grade': 'B',
                'label': 'NFL RB Rushing Yards Parlay',
                'kelly_suggested_units': 2.1,
                'kelly_risk_level': 'Medium',
                'view_count': 1560,
                'settled': True,
                'won': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(days=4),
                'created_at': datetime.now(timezone.utc) - timedelta(days=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=4)
            },
            # MLB Parlay Cards
            {
                'platform': 'twitter',
                'sport_id': 2,
                'legs': [
                    {'player': 'Aaron Judge', 'market': 'home_runs', 'line': 1.5, 'odds': -110},
                    {'player': 'Mike Trout', 'market': 'hits', 'line': 1.5, 'odds': -110},
                    {'player': 'Shohei Ohtani', 'market': 'strikeouts', 'line': 7.5, 'odds': -110}
                ],
                'leg_count': 3,
                'total_odds': 6.00,
                'decimal_odds': 7.00,
                'parlay_probability': 0.1429,
                'parlay_ev': 0.0429,
                'overall_grade': 'A',
                'label': 'MLB Stars Multi-Stat Parlay',
                'kelly_suggested_units': 3.8,
                'kelly_risk_level': 'High',
                'view_count': 1890,
                'settled': True,
                'won': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(days=5),
                'created_at': datetime.now(timezone.utc) - timedelta(days=6),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=5)
            },
            {
                'platform': 'discord',
                'sport_id': 2,
                'legs': [
                    {'player': 'Aaron Judge', 'market': 'rbis', 'line': 2.5, 'odds': -110},
                    {'player': 'Juan Soto', 'market': 'hits', 'line': 1.5, 'odds': -110},
                    {'player': 'Mookie Betts', 'market': 'runs', 'line': 0.5, 'odds': -110}
                ],
                'leg_count': 3,
                'total_odds': 6.00,
                'decimal_odds': 7.00,
                'parlay_probability': 0.1429,
                'parlay_ev': 0.0179,
                'overall_grade': 'B+',
                'label': 'MLB Offensive Production Parlay',
                'kelly_suggested_units': 2.3,
                'kelly_risk_level': 'Medium',
                'view_count': 1120,
                'settled': True,
                'won': False,
                'settled_at': datetime.now(timezone.utc) - timedelta(days=6),
                'created_at': datetime.now(timezone.utc) - timedelta(days=7),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=6)
            },
            # NHL Parlay Cards
            {
                'platform': 'twitter',
                'sport_id': 53,
                'legs': [
                    {'player': 'Connor McDavid', 'market': 'points', 'line': 1.5, 'odds': -110},
                    {'player': 'Nathan MacKinnon', 'market': 'points', 'line': 1.5, 'odds': -110},
                    {'player': 'Auston Matthews', 'market': 'goals', 'line': 0.5, 'odds': -110}
                ],
                'leg_count': 3,
                'total_odds': 6.00,
                'decimal_odds': 7.00,
                'parlay_probability': 0.1429,
                'parlay_ev': 0.0286,
                'overall_grade': 'A-',
                'label': 'NHL Stars Points Parlay',
                'kelly_suggested_units': 2.6,
                'kelly_risk_level': 'Medium',
                'view_count': 980,
                'settled': True,
                'won': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(days=7),
                'created_at': datetime.now(timezone.utc) - timedelta(days=8),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=7)
            },
            # NCAA Basketball Parlay Cards
            {
                'platform': 'reddit',
                'sport_id': 32,
                'legs': [
                    {'player': 'Zion Williamson', 'market': 'points', 'line': 22.5, 'odds': -110},
                    {'player': 'Paolo Banchero', 'market': 'points', 'line': 20.5, 'odds': -110},
                    {'player': 'Chet Holmgren', 'market': 'rebounds', 'line': 8.5, 'odds': -110}
                ],
                'leg_count': 3,
                'total_odds': 6.00,
                'decimal_odds': 7.00,
                'parlay_probability': 0.1429,
                'parlay_ev': 0.0214,
                'overall_grade': 'B+',
                'label': 'NCAA Basketball Stars Parlay',
                'kelly_suggested_units': 2.4,
                'kelly_risk_level': 'Medium',
                'view_count': 1450,
                'settled': True,
                'won': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(days=8),
                'created_at': datetime.now(timezone.utc) - timedelta(days=9),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=8)
            },
            # College Football Parlay Cards
            {
                'platform': 'twitter',
                'sport_id': 41,
                'legs': [
                    {'player': 'Caleb Williams', 'market': 'passing_yards', 'line': 295.5, 'odds': -110},
                    {'player': 'Drake Maye', 'market': 'passing_yards', 'line': 275.5, 'odds': -110},
                    {'player': 'Shedeur Sanders', 'market': 'passing_yards', 'line': 285.5, 'odds': -110}
                ],
                'leg_count': 3,
                'total_odds': 6.00,
                'decimal_odds': 7.00,
                'parlay_probability': 0.1429,
                'parlay_ev': 0.0357,
                'overall_grade': 'A-',
                'label': 'College Football QB Parlay',
                'kelly_suggested_units': 3.1,
                'kelly_risk_level': 'High',
                'view_count': 1780,
                'settled': True,
                'won': False,
                'settled_at': datetime.now(timezone.utc) - timedelta(days=9),
                'created_at': datetime.now(timezone.utc) - timedelta(days=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=9)
            },
            # Multi-Sport Parlay Cards
            {
                'platform': 'discord',
                'sport_id': 99,  # Multi-sport indicator
                'legs': [
                    {'player': 'LeBron James', 'sport': 'NBA', 'market': 'points', 'line': 24.5, 'odds': -110},
                    {'player': 'Patrick Mahomes', 'sport': 'NFL', 'market': 'passing_yards', 'line': 285.5, 'odds': -110},
                    {'player': 'Aaron Judge', 'sport': 'MLB', 'market': 'home_runs', 'line': 1.5, 'odds': -110}
                ],
                'leg_count': 3,
                'total_odds': 6.00,
                'decimal_odds': 7.00,
                'parlay_probability': 0.1429,
                'parlay_ev': 0.0250,
                'overall_grade': 'A-',
                'label': 'Multi-Sport Superstars Parlay',
                'kelly_suggested_units': 2.8,
                'kelly_risk_level': 'High',
                'view_count': 2340,
                'settled': True,
                'won': True,
                'settled_at': datetime.now(timezone.utc) - timedelta(days=10),
                'created_at': datetime.now(timezone.utc) - timedelta(days=11),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=10)
            },
            # Recent Unsettled Cards
            {
                'platform': 'twitter',
                'sport_id': 30,
                'legs': [
                    {'player': 'Stephen Curry', 'market': 'three_pointers', 'line': 4.5, 'odds': -110},
                    {'player': 'Klay Thompson', 'market': 'three_pointers', 'line': 3.5, 'odds': -110},
                    {'player': 'Damian Lillard', 'market': 'three_pointers', 'line': 3.5, 'odds': -110}
                ],
                'leg_count': 3,
                'total_odds': 6.00,
                'decimal_odds': 7.00,
                'parlay_probability': 0.1429,
                'parlay_ev': 0.0321,
                'overall_grade': 'A',
                'label': 'NBA Three-Point Specialists Parlay',
                'kelly_suggested_units': 3.0,
                'kelly_risk_level': 'High',
                'view_count': 890,
                'settled': False,
                'won': None,
                'settled_at': None,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=6),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=6)
            },
            {
                'platform': 'reddit',
                'sport_id': 1,
                'legs': [
                    {'player': 'Travis Kelce', 'market': 'receiving_yards', 'line': 75.5, 'odds': -110},
                    {'player': 'George Kittle', 'market': 'receiving_yards', 'line': 65.5, 'odds': -110},
                    {'player': 'Mark Andrews', 'market': 'receiving_yards', 'line': 60.5, 'odds': -110}
                ],
                'leg_count': 3,
                'total_odds': 6.00,
                'decimal_odds': 7.00,
                'parlay_probability': 0.1429,
                'parlay_ev': 0.0179,
                'overall_grade': 'B+',
                'label': 'NFL Tight Ends Receiving Parlay',
                'kelly_suggested_units': 2.2,
                'kelly_risk_level': 'Medium',
                'view_count': 670,
                'settled': False,
                'won': None,
                'settled_at': None,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=12),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=12)
            }
        ]
        
        # Insert shared cards data
        for card in shared_cards:
            await conn.execute("""
                INSERT INTO shared_cards (
                    platform, sport_id, legs, leg_count, total_odds, decimal_odds,
                    parlay_probability, parlay_ev, overall_grade, label,
                    kelly_suggested_units, kelly_risk_level, view_count,
                    settled, won, settled_at, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
            """, 
                card['platform'],
                card['sport_id'],
                json.dumps(card['legs']),
                card['leg_count'],
                card['total_odds'],
                card['decimal_odds'],
                card['parlay_probability'],
                card['parlay_ev'],
                card['overall_grade'],
                card['label'],
                card['kelly_suggested_units'],
                card['kelly_risk_level'],
                card['view_count'],
                card['settled'],
                card['won'],
                card['settled_at'],
                card['created_at'],
                card['updated_at']
            )
        
        print("Sample shared cards data populated successfully")
        
        # Get shared cards statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_cards,
                COUNT(DISTINCT platform) as unique_platforms,
                COUNT(DISTINCT sport_id) as unique_sports,
                COUNT(DISTINCT leg_count) as unique_leg_counts,
                AVG(total_odds) as avg_total_odds,
                AVG(decimal_odds) as avg_decimal_odds,
                AVG(parlay_probability) as avg_parlay_probability,
                AVG(parlay_ev) as avg_parlay_ev,
                COUNT(CASE WHEN overall_grade = 'A' THEN 1 END) as grade_a_cards,
                COUNT(CASE WHEN overall_grade LIKE 'A-%' THEN 1 END) as grade_a_minus_cards,
                COUNT(CASE WHEN overall_grade LIKE 'B+%' THEN 1 END) as grade_b_plus_cards,
                COUNT(CASE WHEN overall_grade = 'B' THEN 1 END) as grade_b_cards,
                COUNT(CASE WHEN settled = true THEN 1 END) as settled_cards,
                COUNT(CASE WHEN settled = false THEN 1 END) as unsettled_cards,
                COUNT(CASE WHEN settled = true AND won = true THEN 1 END) as won_cards,
                COUNT(CASE WHEN settled = true AND won = false THEN 1 END) as lost_cards,
                SUM(view_count) as total_views,
                AVG(view_count) as avg_views_per_card
            FROM shared_cards
        """)
        
        print(f"\nShared Cards Statistics:")
        print(f"  Total Cards: {stats['total_cards']}")
        print(f"  Unique Platforms: {stats['unique_platforms']}")
        print(f"  Unique Sports: {stats['unique_sports']}")
        print(f"  Unique Leg Counts: {stats['unique_leg_counts']}")
        print(f"  Avg Total Odds: {stats['avg_total_odds']:.2f}")
        print(f"  Avg Decimal Odds: {stats['avg_decimal_odds']:.2f}")
        print(f"  Avg Parlay Probability: {stats['avg_parlay_probability']:.4f}")
        print(f"  Avg Parlay EV: {stats['avg_parlay_ev']:.4f}")
        print(f"  Grade A Cards: {stats['grade_a_cards']}")
        print(f"  Grade A- Cards: {stats['grade_a_minus_cards']}")
        print(f"  Grade B+ Cards: {stats['grade_b_plus_cards']}")
        print(f"  Grade B Cards: {stats['grade_b_cards']}")
        print(f"  Settled Cards: {stats['settled_cards']}")
        print(f"  Unsettled Cards: {stats['unsettled_cards']}")
        print(f"  Won Cards: {stats['won_cards']}")
        print(f"  Lost Cards: {stats['lost_cards']}")
        print(f"  Total Views: {stats['total_views']}")
        print(f"  Avg Views per Card: {stats['avg_views_per_card']:.1f}")
        
        # Get cards by platform
        by_platform = await conn.fetch("""
            SELECT 
                platform,
                COUNT(*) as total_cards,
                COUNT(DISTINCT sport_id) as unique_sports,
                AVG(total_odds) as avg_total_odds,
                AVG(parlay_ev) as avg_parlay_ev,
                COUNT(CASE WHEN settled = true THEN 1 END) as settled_cards,
                COUNT(CASE WHEN settled = true AND won = true THEN 1 END) as won_cards,
                SUM(view_count) as total_views,
                AVG(view_count) as avg_views_per_card
            FROM shared_cards
            GROUP BY platform
            ORDER BY total_cards DESC
        """)
        
        print(f"\nCards by Platform:")
        for platform in by_platform:
            print(f"  {platform}:")
            print(f"    Total Cards: {platform['total_cards']}")
            print(f"    Unique Sports: {platform['unique_sports']}")
            print(f"    Avg Total Odds: {platform['avg_total_odds']:.2f}")
            print(f"    Avg Parlay EV: {platform['avg_parlay_ev']:.4f}")
            print(f"    Settled Cards: {platform['settled_cards']}")
            print(f"    Won Cards: {platform['won_cards']}")
            print(f"    Total Views: {platform['total_views']}")
            print(f"    Avg Views per Card: {platform['avg_views_per_card']:.1f}")
        
        # Get cards by sport
        by_sport = await conn.fetch("""
            SELECT 
                sport_id,
                COUNT(*) as total_cards,
                COUNT(DISTINCT platform) as unique_platforms,
                AVG(total_odds) as avg_total_odds,
                AVG(parlay_ev) as avg_parlay_ev,
                COUNT(CASE WHEN settled = true THEN 1 END) as settled_cards,
                COUNT(CASE WHEN settled = true AND won = true THEN 1 END) as won_cards,
                SUM(view_count) as total_views,
                AVG(view_count) as avg_views_per_card
            FROM shared_cards
            GROUP BY sport_id
            ORDER BY total_cards DESC
        """)
        
        print(f"\nCards by Sport:")
        sport_mapping = {
            1: "NFL",
            2: "MLB",
            30: "NBA",
            32: "NCAA Basketball",
            41: "College Football",
            53: "NHL",
            99: "Multi-Sport"
        }
        
        for sport in by_sport:
            sport_name = sport_mapping.get(sport['sport_id'], f"Sport {sport['sport_id']}")
            print(f"  {sport_name}:")
            print(f"    Total Cards: {sport['total_cards']}")
            print(f"    Unique Platforms: {sport['unique_platforms']}")
            print(f"    Avg Total Odds: {sport['avg_total_odds']:.2f}")
            print(f"    Avg Parlay EV: {sport['avg_parlay_ev']:.4f}")
            print(f"    Settled Cards: {sport['settled_cards']}")
            print(f"    Won Cards: {sport['won_cards']}")
            print(f"    Total Views: {sport['total_views']}")
            print(f"    Avg Views per Card: {sport['avg_views_per_card']:.1f}")
        
        # Get performance by grade
        by_grade = await conn.fetch("""
            SELECT 
                overall_grade,
                COUNT(*) as total_cards,
                COUNT(CASE WHEN settled = true THEN 1 END) as settled_cards,
                COUNT(CASE WHEN settled = true AND won = true THEN 1 END) as won_cards,
                COUNT(CASE WHEN settled = true AND won = false THEN 1 END) as lost_cards,
                ROUND(COUNT(CASE WHEN settled = true AND won = true THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN settled = true THEN 1 END), 0), 2) as win_rate_percentage,
                AVG(parlay_ev) as avg_parlay_ev,
                AVG(kelly_suggested_units) as avg_kelly_units,
                SUM(view_count) as total_views,
                AVG(view_count) as avg_views_per_card
            FROM shared_cards
            GROUP BY overall_grade
            ORDER BY overall_grade DESC
        """)
        
        print(f"\nPerformance by Grade:")
        for grade in by_grade:
            print(f"  Grade {grade['overall_grade']}:")
            print(f"    Total Cards: {grade['total_cards']}")
            print(f"    Settled Cards: {grade['settled_cards']}")
            print(f"    Won Cards: {grade['won_cards']}")
            print(f"    Lost Cards: {grade['lost_cards']}")
            print(f"    Win Rate: {grade['win_rate_percentage']:.2f}%")
            print(f"    Avg Parlay EV: {grade['avg_parlay_ev']:.4f}")
            print(f"    Avg Kelly Units: {grade['avg_kelly_units']:.2f}")
            print(f"    Total Views: {grade['total_views']}")
            print(f"    Avg Views per Card: {grade['avg_views_per_card']:.1f}")
        
        # Get recent cards
        recent = await conn.fetch("""
            SELECT * FROM shared_cards 
            ORDER BY created_at DESC, updated_at DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent Shared Cards:")
        for card in recent:
            print(f"  - {card['label']}")
            print(f"    Platform: {card['platform']}")
            print(f"    Sport: {sport_mapping.get(card['sport_id'], f'Sport {card['sport_id']}')}")
            print(f"    Legs: {card['leg_count']}, Odds: {card['total_odds']}")
            print(f"    Grade: {card['overall_grade']}, EV: {card['parlay_ev']:.4f}")
            print(f"    Kelly: {card['kelly_suggested_units']:.2f} units ({card['kelly_risk_level']})")
            print(f"    Views: {card['view_count']}")
            print(f"    Status: {'Won' if card['won'] else 'Lost' if card['won'] == False else 'Pending'}")
            print(f"    Created: {card['created_at']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_shared_cards())
