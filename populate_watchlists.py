#!/usr/bin/env python3
"""
POPULATE WATCHLISTS - Initialize and populate the watchlists table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_watchlists():
    """Populate watchlists table with initial data"""
    
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
                WHERE table_name = 'watchlists'
            )
        """)
        
        if not table_check:
            print("Creating watchlists table...")
            await conn.execute("""
                CREATE TABLE watchlists (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    filters JSONB NOT NULL,
                    alert_enabled BOOLEAN DEFAULT TRUE,
                    alert_discord_webhook VARCHAR(500),
                    alert_email VARCHAR(255),
                    last_check_at TIMESTAMP WITH TIME ZONE,
                    last_match_count INTEGER DEFAULT 0,
                    last_notified_at TIMESTAMP WITH TIME ZONE,
                    sport_id INTEGER,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample watchlists data
        print("Generating sample watchlists data...")
        
        watchlists = [
            # NBA Player Watchlists
            {
                'name': 'NBA Stars Over 25 Points',
                'filters': {
                    'sport_id': 30,
                    'market_type': 'points',
                    'side': 'over',
                    'line_value_min': 25.0,
                    'players': [91, 92, 101, 102],
                    'teams': [3, 4, 5, 6],
                    'min_odds': -110,
                    'max_odds': 150
                },
                'alert_enabled': True,
                'alert_discord_webhook': 'https://discord.com/api/webhooks/1234567890',
                'alert_email': 'user@example.com',
                'last_check_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'last_match_count': 3,
                'last_notified_at': datetime.now(timezone.utc) - timedelta(hours=1),
                'sport_id': 30,
                'created_at': datetime.now(timezone.utc) - timedelta(days=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=1)
            },
            {
                'name': 'NBA Rebounds Leaders',
                'filters': {
                    'sport_id': 30,
                    'market_type': 'rebounds',
                    'side': 'over',
                    'line_value_min': 10.0,
                    'players': [101, 102, 103, 104],
                    'teams': [5, 6, 7, 8],
                    'min_odds': -110,
                    'max_odds': 120
                },
                'alert_enabled': True,
                'alert_discord_webhook': 'https://discord.com/api/webhooks/2345678901',
                'alert_email': 'user@example.com',
                'last_check_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'last_match_count': 2,
                'last_notified_at': datetime.now(timezone.utc) - timedelta(hours=2),
                'sport_id': 30,
                'created_at': datetime.now(timezone.utc) - timedelta(days=7),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=2)
            },
            {
                'name': 'NBA Three-Point Specialists',
                'filters': {
                    'sport_id': 30,
                    'market_type': 'three_pointers',
                    'side': 'over',
                    'line_value_min': 4.0,
                    'players': [92, 105, 106, 107],
                    'teams': [4, 5, 6, 7],
                    'min_odds': -110,
                    'max_odds': 140
                },
                'alert_enabled': False,
                'alert_discord_webhook': None,
                'alert_email': None,
                'last_check_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'last_match_count': 0,
                'last_notified_at': None,
                'sport_id': 30,
                'created_at': datetime.now(timezone.utc) - timedelta(days=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=3))
            },
            # NFL Player Watchlists
            {
                'name': 'NFL Quarterbacks Over 300 Yards',
                'filters': {
                    'sport_id': 1,
                    'market_type': 'passing_yards',
                    'side': 'over',
                    'line_value_min': 300.0,
                    'players': [111, 112, 113, 114],
                    'teams': [101, 102, 103, 104],
                    'min_odds': -110,
                    'max_odds': 130
                },
                'alert_enabled': True,
                'alert_discord_webhook': 'https://discord.com/api/webhooks/34567890123',
                'alert_email': 'user@example.com',
                'last_check_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'last_match_count': 1,
                'last_notified_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'sport_id': 1,
                'created_at': datetime.now(timezone.utc) - timedelta(days=6),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=4)
            },
            {
                'name': 'NFL Rushing Touchdowns',
                'filters': {
                    'sport_id': 1,
                    'market_type': 'rushing_touchdowns',
                    'side': 'over',
                    'line_value_min': 1.0,
                    'players': [115, 116, 117, 118],
                    'teams': [101, 102, 103, 104],
                    'min_odds': -110,
                    'max_odds': 150
                },
                'alert_enabled': True,
                'alert_discord_webhook': 'https://discord.com/api/webhooks/4567890123',
                'alert_email': 'user@example.com',
                'last_check_at': datetime.now(timezone.utc) - timedelta(hours=5),
                'last_match_count': 2,
                'last_notified_at': datetime.now(timezone.utc) - timedelta(hours=5),
                'sport_id': 1,
                'created_at': datetime.now(timezone.utc) - timedelta(days=8),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=5))
            },
            {
                'name': 'NFL Interceptions',
                'filters': {
                    'sport_id': 1,
                    'market_type': 'interceptions',
                    'side': 'over',
                    'line_value_min': 0.5,
                    'players': [119, 120, 121, 122],
                    'teams': [101, 102, 103, 104],
                    'min_odds': 120,
                    'max_odds': 200
                },
                'alert_enabled': False,
                'alert_discord_webhook': None,
                'alert_email': None,
                'last_check_at': datetime.now(timezone.utc) - timedelta(hours=6),
                'last_match_count': 0,
                'last_notified_at': None,
                'sport_id': 1,
                'created_at': datetime.now(timezone.utc) - timedelta(days=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=6))
            },
            # MLB Player Watchlists
            {
                'name': 'MLB Home Run Leaders',
                'filters': {
                    'sport_id': 2,
                    'market_type': 'home_runs',
                    'side': 'over',
                    'line_value_min': 1.5,
                    'players': [201, 202, 203, 204],
                    'teams': [201, 202, 203, 204],
                    'min_odds': -110,
                    'max_odds': 120
                },
                'alert_enabled': True,
                'alert_discord_webhook': 'https://discord.com/api/webhooks/5678901234',
                'alert_email': 'user@example.com',
                'last_check_at': datetime.now(timezone.utc) - timedelta(hours=7),
                'last_match_count': 4,
                'last_notified_at': datetime.now(timezone.utc) - timedelta(hours=7),
                'sport_id': 2,
                'created_at': datetime.now(timezone.utc) - timedelta(days=9),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=7))
            },
            {
                'name': 'MLB Strikeout Kings',
                'filters': {
                    'sport_id': 2,
                    'market_type': 'strikeouts',
                    'side': 'over',
                    'line_value_min': 8.0,
                    'players': [205, 206, 207, 208],
                    'teams': [201, 202, 203, 204],
                    'min_odds': -110,
                    'max_odds': 110
                },
                'alert_enabled': True,
                'alert_discord_webhook': 'https://discord.com/api/webhooks/6789012345',
                'alert_email': 'user@example.com',
                'last_check_at': datetime.now(timezone.utc) - timedelta(hours=8),
                'last_match_count': 3,
                'last_notified_at': datetime.now(timezone.utc) - timedelta(hours=8),
                'sport_id': 2,
                'created_at': datetime.now(timezone.utc) - timedelta(days=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=8))
            },
            {
                'name': 'MLB Batting Average Leaders',
                'filters': {
                    'sport_id': 2,
                    'market_type': 'batting_average',
                    'side': 'over',
                    'line_value_min': 0.300,
                    'players': [209, 210, 211, 212],
                    'teams': [201, 202, 203, 204],
                    'min_odds': -110,
                    'max_odds': 120
                },
                'alert_enabled': False,
                'alert_discord_webhook': None,
                'alert_email': None,
                'last_check_at': datetime.now(timezone.utc) - timedelta(hours=9),
                'last_match_count': 0,
                'last_notified_at': None,
                'sport_id': 2,
                'created_at': datetime.now(timezone.utc) - timedelta(days=5),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=9))
            },
            # NHL Player Watchlists
            {
                'name': 'NHL Point Leaders',
                'filters': {
                    'sport_id': 53,
                    'market_type': 'points',
                    'side': 'over',
                    'line_value_min': 1.5,
                    'players': [301, 302, 303, 304],
                    'teams': [301, 302, 303, 304],
                    'min_odds': -110,
                    'max_odds': 130
                },
                'alert_enabled': True,
                'alert_discord_webhook': 'https://discord.com/api/webhooks/7890123456',
                'alert_email': 'user@example.com',
                'last_check_at': datetime.now(timezone.utc) - timedelta(hours=10),
                'last_match_count': 2,
                'last_notified_at': datetime.now(timezone.utc) - timedelta(hours=10),
                'sport_id': 53,
                'created_at': datetime.now(timezone.utc) - timedelta(days=11),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=10))
            },
            {
                'name': 'NHL Goal Scorers',
                'filters': {
                    'sport_id': 53,
                    'market_type': 'goals',
                    'side': 'over',
                    'line_value_min': 1.0,
                    'players': [305, 306, 307, 308],
                    'teams': [301, 302, 303, 304],
                    'min_odds': -110,
                    'max_odds': 140
                },
                'alert_enabled': True,
                'alert_discord_webhook': 'https://discord.com/api/webhooks/8901234567',
                'alert_email': 'user@example.com',
                'last_check_at': datetime.now(timezone.utc) - timedelta(hours=11),
                'last_match_count': 3,
                'last_notified_at': datetime.now(timezone.utc) - timedelta(hours=11),
                'sport_id': 53,
                'created_at': datetime.now(timezone.utc) - timedelta(days=12),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=11))
            },
            {
                'name': 'NHL Save Leaders',
                'filters': {
                    'sport_id': 53,
                    'market_type': 'saves',
                    'side': 'over',
                    'line_value_min': 25.0,
                    'players': [309, 310, 311, 312],
                    'teams': [301, 302, 303, 304],
                    'min_odds': -110,
                    'max_odds': 110
                },
                'alert_enabled': False,
                'alert_discord_webhook': None,
                'alert_email': None,
                'last_check_at': datetime.now(timezone.utc) - timedelta(hours=12),
                'last_match_count': 0,
                'last_notified_at': None,
                'sport_id': 53,
                'created_at': datetime.now(timezone.utc) - timedelta(days=7),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=12))
            },
            # Multi-Sport Watchlists
            {
                'name': 'Superstar Players',
                'filters': {
                    'players': [91, 92, 111, 112, 201, 202, 301, 302],
                    'min_odds': -110,
                    'max_odds': 150
                },
                'alert_enabled': True,
                'alert_discord_webhook': 'https://discord.com/api/webhooks/9012345678',
                'alert_email': 'user@example.com',
                'last_check_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'last_match_count': 8,
                'last_notified_at': datetime.now(timezone.utc) - timedelta(minutes=30),
                'sport_id': None,
                'created_at': datetime.now(timezone.utc) - timedelta(days=1),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=30))
            },
            {
                'name': 'High Value Bets',
                'filters': {
                    'min_odds': 120,
                    'max_odds': 300,
                    'line_value_min': 1.0
                },
                'alert_enabled': True,
                'alert_discord_webhook': 'https://discord.com/api/webhooks/0123456789',
                'alert_email': 'user@example.com',
                'last_check_at': datetime.now(timezone.utc) - timedelta(minutes=45),
                'last_match_count': 5,
                'last_notified_at': datetime.now(timezone.utc) - timedelta(minutes=45),
                'sport_id': None,
                'created_at': datetime.now(timezone.utc) - timedelta(days=2),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=45))
            },
            {
                'name': 'Live Game Alerts',
                'filters': {
                    'live_games_only': True,
                    'players': [91, 92, 111, 112],
                    'markets': ['points', 'yards', 'home_runs', 'goals']
                },
                'alert_enabled': True,
                'alert_discord_webhook': 'https://discord.com/api/webhooks/1234567890',
                'alert_email': 'user@example.com',
                'last_check_at': datetime.now(timezone.utc) - timedelta(minutes=15),
                'last_match_count': 12,
                'last_notified_at': datetime.now(timezone.utc) - timedelta(minutes=15),
                'sport_id': None,
                'created_at': datetime.now(timezone.utc) - timedelta(hours=3),
                'updated_at': datetime.now(timezone.utc) - timedelta(minutes=15))
            }
        ]
        
        # Insert watchlists data
        for watchlist in watchlists:
            await conn.execute("""
                INSERT INTO watchlists (
                    name, filters, alert_enabled, alert_discord_webhook, alert_email,
                    last_check_at, last_match_count, last_notified_at, sport_id, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """, 
                watchlist['name'],
                json.dumps(watchlist['filters']),
                watchlist['alert_enabled'],
                watchlist['alert_discord_webhook'],
                watchlist['alert_email'],
                watchlist['last_check_at'],
                watchlist['last_match_count'],
                watchlist['last_notified_at'],
                watchlist['sport_id'],
                watchlist['created_at'],
                watchlist['updated_at']
            )
        
        print("Sample watchlists data populated successfully")
        
        # Get watchlists statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_watchlists,
                COUNT(DISTINCT sport_id) as unique_sports,
                COUNT(CASE WHEN alert_enabled = true THEN 1 END) as enabled_alerts,
                COUNT(CASE WHEN alert_enabled = false THEN 1 END) as disabled_alerts,
                COUNT(CASE WHEN alert_discord_webhook IS NOT NULL THEN 1 END) as discord_alerts,
                COUNT(CASE WHEN alert_email IS NOT NULL THEN 1 END) as email_alerts,
                SUM(last_match_count) as total_matches,
                AVG(last_match_count) as avg_matches,
                COUNT(CASE WHEN last_check_at >= NOW() - INTERVAL '1 hour' THEN 1 END) as recent_checks,
                COUNT(CASE WHEN last_notified_at >= NOW() - INTERVAL '1 hour' THEN 1 END) as recent_notifications,
                MIN(created_at) as first_watchlist,
                MAX(created_at) as last_watchlist
            FROM watchlists
        """)
        
        print(f"\nWatchlists Statistics:")
        print(f"  Total Watchlists: {stats['total_watchlists']}")
        print(f"  Unique Sports: {stats['unique_sports']}")
        print(f"  Enabled Alerts: {stats['enabled_alerts']}")
        print(f"  Disabled Alerts: {stats['disabled_alerts']}")
        print(f"  Discord Alerts: {stats['discord_alerts']}")
        print(f"  Email Alerts: {stats['email_alerts']}")
        print(f"  Total Matches: {stats['total_matches']}")
        print(f"  Avg Matches: {stats['avg_matches']:.1f}")
        print(f"  Recent Checks: {stats['recent_checks']}")
        print(f"  Recent Notifications: {stats['recent_notifications']}")
        print(f"  First Watchlist: {stats['first_watchlist']}")
        print(f"  Last Watchlist: {stats['last_watchlist']}")
        
        # Get watchlists by sport
        by_sport = await conn.fetch("""
            SELECT 
                sport_id,
                COUNT(*) as total_watchlists,
                COUNT(CASE WHEN alert_enabled = true THEN 1 END) as enabled_alerts,
                COUNT(CASE WHEN alert_discord_webhook IS NOT NULL THEN 1 END) as discord_alerts,
                COUNT(CASE WHEN alert_email IS NOT NULL THEN 1 END) as email_alerts,
                SUM(last_match_count) as total_matches,
                AVG(last_match_count) as avg_matches,
                MIN(created_at) as first_watchlist,
                MAX(created_at) as last_watchlist
            FROM watchlists
            WHERE sport_id IS NOT NULL
            GROUP BY sport_id
            ORDER BY total_watchlists DESC
        """)
        
        print(f"\nWatchlists by Sport:")
        sport_mapping = {
            1: "NFL",
            2: "MLB",
            30: "NBA",
            53: "NHL"
        }
        
        for sport in by_sport:
            sport_name = sport_mapping.get(sport['sport_id'], f"Sport {sport['sport_id']}")
            print(f"  {sport_name}:")
            print(f"    Total Watchlists: {sport['total_watchlists']}")
            print(f"    Enabled Alerts: {sport['enabled_alerts']}")
            print(f"    Discord Alerts: {sport['discord_alerts']}")
            print(f"    Email Alerts: {sport['email_alerts']}")
            print(f"    Total Matches: {sport['total_matches']}")
            print(f"    Avg Matches: {sport['avg_matches']:.1f}")
            print(f"    Period: {sport['first_watchlist']} to {sport['last_watchlist']}")
        
        # Get watchlists by alert status
        by_alert_status = await conn.fetch("""
            SELECT 
                alert_enabled,
                COUNT(*) as total_watchlists,
                COUNT(CASE WHEN alert_discord_webhook IS NOT NULL THEN 1 END) as discord_alerts,
                COUNT(CASE WHEN alert_email IS NOT NULL THEN 1 END) as email_alerts,
                SUM(last_match_count) as total_matches,
                AVG(last_match_count) as avg_matches,
                MIN(created_at) as first_watchlist,
                MAX(created_at) as last_watchlist
            FROM watchlists
            GROUP BY alert_enabled
            ORDER BY total_watchlists DESC
        """)
        
        print(f"\nWatchlists by Alert Status:")
        for alert in by_alert_status:
            status = "Enabled" if alert['alert_enabled'] else "Disabled"
            print(f"  {status}:")
            print(f"    Total Watchlists: {alert['total_watchlists']}")
            print(f"    Discord Alerts: {alert['discord_alerts']}")
            print(f"    Email Alerts: {alert['email_alerts']}")
            print(f"    Total Matches: {alert['total_matches']}")
            print(f"    Avg Matches: {alert['avg_matches']:.1f}")
            print(f"    Period: {alert['first_watchlist']} to {alert['last_watchlist']}")
        
        # Get watchlists by notification type
        by_notification = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN alert_discord_webhook IS NOT NULL AND alert_email IS NOT NULL THEN 'Both'
                    WHEN alert_discord_webhook IS NOT NULL THEN 'Discord Only'
                    WHEN alert_email IS NOT NULL THEN 'Email Only'
                    ELSE 'No Notifications'
                END as notification_type,
                COUNT(*) as total_watchlists,
                COUNT(CASE WHEN alert_enabled = true THEN 1 END) as enabled_alerts,
                SUM(last_match_count) as total_matches,
                AVG(last_match_count) as avg_matches,
                MIN(created_at) as first_watchlist,
                MAX(created_at) as last_watchlist
            FROM watchlists
            GROUP BY notification_type
            ORDER BY total_watchlists DESC
        """)
        
        print(f"\nWatchlists by Notification Type:")
        for notification in by_notification:
            print(f"  {notification['notification_type']}:")
            print(f"    Total Watchlists: {notification['total_watchlists']}")
            print(f"    Enabled Alerts: {notification['enabled_alerts']}")
            print(f"    Total Matches: {notification['total_matches']}")
            print(f"    Avg Matches: {notification['avg_matches']:.1f}")
            print(f"    Period: {notification['first_watchlist']} to {notification['last_watchlist']}")
        
        # Recent watchlists
        recent = await conn.fetch("""
            SELECT * FROM watchlists 
            ORDER BY created_at DESC, updated_at DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent Watchlists:")
        for watchlist in recent:
            sport_name = sport_mapping.get(watchlist['sport_id'], "Multi-Sport") if watchlist['sport_id'] else "Multi-Sport"
            print(f"  - {watchlist['name']}")
            print(f"    Sport: {sport_name}")
            print(f"    Alert Enabled: {'Yes' if watchlist['alert_enabled'] else 'No'}")
            print(f"    Last Check: {watchlist['last_check_at']}")
            print(f"    Last Matches: {watchlist['last_match_count']}")
            print(f"    Created: {watchlist['created_at']}")
            print(f"    Updated: {watchlist['updated_at']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_watchlists())
