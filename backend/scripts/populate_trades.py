#!/usr/bin/env python3
"""
POPULATE TRADES - Initialize and populate the trades table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_trades():
    """Populate trades table with initial data"""
    
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
                WHERE table_name = 'trades'
            )
        """)
        
        if not table_check:
            print("Creating trades table...")
            await conn.execute("""
                CREATE TABLE trades (
                    id SERIAL PRIMARY KEY,
                    trade_date DATE NOT NULL,
                    season_year INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    headline VARCHAR(200) NOT NULL,
                    source_url VARCHAR(500),
                    source VARCHAR(50),
                    is_applied BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Table created")
        
        # Generate sample trades data
        print("Generating sample trades data...")
        
        trades = [
            # NBA Trades
            {
                'trade_date': datetime(2024, 2, 8).date(),
                'season_year': 2024,
                'description': 'The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.',
                'headline': 'Blockbuster: Suns Trade Durant to Celtics for Booker',
                'source_url': 'https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker',
                'source': 'ESPN',
                'is_applied': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'trade_date': datetime(2024, 2, 13).date(),
                'season_year': 2024,
                'description': 'The Toronto Raptors and Denver Nuggets agreed to a trade that sends point guard Kyle Lowry to Denver in exchange for center Nikola Jokic. The deal addresses both teams needs with the Raptors getting a dominant big man and the Nuggets adding veteran leadership.',
                'headline': 'Raptors Trade Lowry to Nuggets for Jokic',
                'source_url': 'https://www.nba.com/news/raptors-trade-lowry-to-nuggets-for-jokic',
                'source': 'NBA.com',
                'is_applied': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=25)
            },
            {
                'trade_date': datetime(2024, 2, 18).date(),
                'season_year': 2024,
                'description': 'The Indiana Pacers and Portland Trail Blazers completed a trade sending rising star Tyrese Haliburton to Portland in exchange for veteran scorer Damian Lillard. The Pacers get immediate championship help while the Trail Blazers build around their new young star.',
                'headline': 'Pacers Send Haliburton to Trail Blazers for Lillard',
                'source_url': 'https://www.bleacherreport.com/nba/articles/pacers-send-haliburton-to-trail-blazers-for-lillard',
                'source': 'Bleacher Report',
                'is_applied': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=20),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=20)
            },
            {
                'trade_date': datetime(2024, 2, 23).date(),
                'season_year': 2024,
                'description': 'The Philadelphia 76ers and Chicago Bulls swapped defensive specialists with Matisse Thybulle heading to Chicago and Patrick Williams joining Philadelphia. Both teams look to strengthen their respective defensive identities.',
                'headline': '76ers and Bulls Swap Defensive Specialists',
                'source_url': 'https://www.sportsillustrated.com/nba/76ers-bulls-swap-defensive-specialists',
                'source': 'Sports Illustrated',
                'is_applied': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=15)
            },
            {
                'trade_date': datetime(2024, 2, 28).date(),
                'season_year': 2024,
                'description': 'The Indiana Pacers acquired a 2025 first-round draft pick from the Cleveland Cavaliers in exchange for young center Walker Kessler. The Pacers add future assets while the Cavaliers get immediate help in the paint.',
                'headline': 'Pacers Acquire 2025 First-Round Pick from Cavaliers',
                'source_url': 'https://www.theathletic.com/nba/pacers-acquire-2025-first-round-pick-from-cavaliers',
                'source': 'The Athletic',
                'is_applied': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=10),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=10)
            },
            # NFL Trades
            {
                'trade_date': datetime(2024, 3, 15).date(),
                'season_year': 2024,
                'description': 'The Green Bay Packers traded future Hall of Fame quarterback Aaron Rodgers to the Las Vegas Raiders in exchange for star wide receiver Davante Adams. The Raiders get their franchise quarterback while the Packers add a proven weapon for their new QB.',
                'headline': 'Packers Trade Rodgers to Raiders for Adams',
                'source_url': 'https://www.nfl.com/news/packers-trade-rodgers-to-raiders-for-adams',
                'source': 'NFL.com',
                'is_applied': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=35),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=35)
            },
            {
                'trade_date': datetime(2024, 3, 22).date(),
                'season_year': 2024,
                'description': 'The Carolina Panthers traded running back Christian McCaffrey to the San Francisco 49ers in exchange for veteran linebacker Bobby Wagner. The 49ers add an elite offensive weapon while the Panthers strengthen their defense.',
                'headline': 'Panthers Trade McCaffrey to 49ers for Wagner',
                'source_url': 'https://www.espn.com/nfl/story/_/id/23456789/panthers-trade-mccaffrey-to-49ers-for-wagner',
                'source': 'ESPN',
                'is_applied': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=28),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=28)
            },
            {
                'trade_date': datetime(2024, 3, 29).date(),
                'season_year': 2024,
                'description': 'The Cleveland Browns traded elite edge rusher Myles Garrett to the Los Angeles Rams in exchange for Pro Bowl cornerback Jaire Alexander. Both teams address major needs with this high-profile swap.',
                'headline': 'Browns Trade Garrett to Rams for Alexander',
                'source_url': 'https://www.profootballtalk.com/nfl/browns-trade-garrett-to-rams-for-alexander',
                'source': 'Pro Football Talk',
                'is_applied': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=21),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=21)
            },
            {
                'trade_date': datetime(2024, 4, 5).date(),
                'season_year': 2024,
                'description': 'The Tennessee Titans traded a 2025 second-round draft pick to the Baltimore Ravens in exchange for veteran safety Kevin Byard. The Ravens add depth to their secondary while the Titans accumulate future assets.',
                'headline': 'Titans Trade 2025 Second-Round Pick to Ravens for Byard',
                'source_url': 'https://www.nfl.com/news/titans-trade-2025-second-round-pick-to-ravens-for-byard',
                'source': 'NFL.com',
                'is_applied': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=15),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=15)
            },
            # MLB Trades
            {
                'trade_date': datetime(2024, 7, 31).date(),
                'season_year': 2024,
                'description': 'The New York Mets traded power-hitting first baseman Pete Alonso to the Los Angeles Dodgers in exchange for ace pitcher Jacob deGrom. The Dodgers add a middle-of-the-order bat while the Mets acquire a frontline starter.',
                'headline': 'Mets Trade Alonso to Dodgers for deGrom',
                'source_url': 'https://www.mlb.com/trade-news/mets-trade-alonso-to-dodgers-for-degrom',
                'source': 'MLB.com',
                'is_applied': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=40),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=40)
            },
            {
                'trade_date': datetime(2024, 7, 28).date(),
                'season_year': 2024,
                'description': 'The Los Angeles Angels traded superstar Mike Trout to the San Diego Padres in exchange for All-Star third baseman Manny Machado. The Padres add a generational talent while the Angels get a proven power hitter.',
                'headline': 'Angels Trade Trout to Padres for Machado',
                'source_url': 'https://www.baseballamerica.com/mlb/angels-trade-trout-to-padres-for-machado',
                'source': 'Baseball America',
                'is_applied': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=32),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=32)
            },
            {
                'trade_date': datetime(2024, 7, 25).date(),
                'season_year': 2024,
                'description': 'The New York Yankees traded Cy Young winner Gerrit Cole to the Houston Astros in exchange for Hall of Fame closer Craig Kimbrel. The Astros add an ace to their rotation while the Yankees get a proven closer.',
                'headline': 'Yankees Trade Cole to Astros for Kimbrel',
                'source_url': 'https://www.si.com/mlb/yankees-trade-cole-to-astros-for-kimbrel',
                'source': 'Sports Illustrated',
                'is_applied': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=25),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=25)
            },
            # NHL Trades
            {
                'trade_date': datetime(2024, 3, 8).date(),
                'season_year': 2024,
                'description': 'The Edmonton Oilers traded elite center Connor McDavid to the Toronto Maple Leafs in exchange for power forward Nathan MacKinnon. The Maple Leafs get their franchise center while the Oilers add a dominant power forward.',
                'headline': 'Oilers Trade McDavid to Maple Leafs for MacKinnon',
                'source_url': 'https://www.tsn.ca/nhl/oilers-trade-mcdavid-to-maple-leafs-for-mackinnon',
                'source': 'TSN',
                'is_applied': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=38),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=38)
            },
            {
                'trade_date': datetime(2024, 3, 12).date(),
                'season_year': 2024,
                'description': 'The Tampa Bay Lightning traded elite goaltender Andrei Vasilevskiy to the Colorado Avalanche in exchange for offensive defenseman Victor Hedman. The Avalanche add a Vezina-caliber goalie while the Lightning get a top-pairing defenseman.',
                'headline': 'Lightning Trade Vasilevskiy to Avalanche for Hedman',
                'source_url': 'https://www.nhl.com/news/lightning-trade-vasilevskiy-to-avalanche-for-hedman',
                'source': 'NHL.com',
                'is_applied': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=30),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=30)
            },
            {
                'trade_date': datetime(2024, 3, 16).date(),
                'season_year': 2024,
                'description': 'The Toronto Maple Leafs traded goal-scoring winger Auston Matthews to the Vegas Golden Knights in exchange for two-way defenseman Roman Josi. The Golden Knights add an elite goal scorer while the Maple Leafs strengthen their blue line.',
                'headline': 'Maple Leafs Trade Matthews to Golden Knights for Josi',
                'source_url': 'https://www.espn.com/nhl/story/_/id/34567890/maple-leafs-trade-matthews-to-golden-knights-for-josi',
                'source': 'ESPN',
                'is_applied': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=22),
                'updated_at': datetime.now(timezone.utc) - timedelta(days=22)
            }
        ]
        
        # Insert trades data
        for trade in trades:
            await conn.execute("""
                INSERT INTO trades (
                    trade_date, season_year, description, headline, source_url, source,
                    is_applied, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
                trade['trade_date'],
                trade['season_year'],
                trade['description'],
                trade['headline'],
                trade['source_url'],
                trade['source'],
                trade['is_applied'],
                trade['created_at'],
                trade['updated_at']
            )
        
        print("Sample trades data populated successfully")
        
        # Get trades statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_trades,
                COUNT(DISTINCT season_year) as unique_seasons,
                COUNT(DISTINCT source) as unique_sources,
                COUNT(CASE WHEN is_applied = true THEN 1 END) as applied_trades,
                COUNT(CASE WHEN is_applied = false THEN 1 END) as pending_trades,
                MIN(trade_date) as earliest_trade,
                MAX(trade_date) as latest_trade,
                AVG(LENGTH(description)) as avg_description_length,
                AVG(LENGTH(headline)) as avg_headline_length
            FROM trades
        """)
        
        print(f"\nTrades Statistics:")
        print(f"  Total Trades: {stats['total_trades']}")
        print(f"  Unique Seasons: {stats['unique_seasons']}")
        print(f"  Unique Sources: {stats['unique_sources']}")
        print(f"  Applied Trades: {stats['applied_trades']}")
        print(f"  Pending Trades: {stats['pending_trades']}")
        print(f"  Earliest Trade: {stats['earliest_trade']}")
        print(f"  Latest Trade: {stats['latest_trade']}")
        print(f"  Avg Description Length: {stats['avg_description_length']:.1f}")
        print(f"  Avg Headline Length: {stats['avg_headline_length']:.1f}")
        
        # Get trades by season
        by_season = await conn.fetch("""
            SELECT 
                season_year,
                COUNT(*) as total_trades,
                COUNT(CASE WHEN is_applied = true THEN 1 END) as applied_trades,
                COUNT(DISTINCT source) as unique_sources,
                MIN(trade_date) as first_trade,
                MAX(trade_date) as last_trade,
                AVG(LENGTH(description)) as avg_description_length
            FROM trades
            GROUP BY season_year
            ORDER BY season_year DESC
        """)
        
        print(f"\nTrades by Season:")
        for season in by_season:
            print(f"  {season['season_year']}:")
            print(f"    Total Trades: {season['total_trades']}")
            print(f"    Applied Trades: {season['applied_trades']}")
            print(f"    Unique Sources: {season['unique_sources']}")
            print(f"    Period: {season['first_trade']} to {season['last_trade']}")
            print(f"    Avg Description Length: {season['avg_description_length']:.1f}")
        
        # Get trades by source
        by_source = await conn.fetch("""
            SELECT 
                source,
                COUNT(*) as total_trades,
                COUNT(DISTINCT season_year) as unique_seasons,
                COUNT(CASE WHEN is_applied = true THEN 1 END) as applied_trades,
                MIN(trade_date) as first_trade,
                MAX(trade_date) as last_trade
            FROM trades
            GROUP BY source
            ORDER BY total_trades DESC
        """)
        
        print(f"\nTrades by Source:")
        for source in by_source:
            print(f"  {source}:")
            print(f"    Total Trades: {source['total_trades']}")
            print(f"    Unique Seasons: {source['unique_seasons']}")
            print(f"    Applied Trades: {source['applied_trades']}")
            print(f"    Period: {source['first_trade']} to {source['last_trade']}")
        
        # Get trades by month
        by_month = await conn.fetch("""
            SELECT 
                DATE_TRUNC('month', trade_date) as trade_month,
                COUNT(*) as total_trades,
                COUNT(DISTINCT season_year) as unique_seasons,
                COUNT(CASE WHEN is_applied = true THEN 1 END) as applied_trades,
                COUNT(DISTINCT source) as unique_sources
            FROM trades
            GROUP BY DATE_TRUNC('month', trade_date)
            ORDER BY trade_month DESC
        """)
        
        print(f"\nTrades by Month:")
        for month in by_month:
            print(f"  {month['trade_month'].strftime('%B %Y')}:")
            print(f"    Total Trades: {month['total_trades']}")
            print(f"    Unique Seasons: {month['unique_seasons']}")
            print(f"    Applied Trades: {month['applied_trades']}")
            print(f"    Unique Sources: {month['unique_sources']}")
        
        # Recent trades
        recent = await conn.fetch("""
            SELECT * FROM trades 
            ORDER BY trade_date DESC, created_at DESC 
            LIMIT 5
        """)
        
        print(f"\nRecent Trades:")
        for trade in recent:
            print(f"  - {trade['headline']}")
            print(f"    Date: {trade['trade_date']}")
            print(f"    Season: {trade['season_year']}")
            print(f"    Source: {trade['source']}")
            print(f"    Applied: {'Yes' if trade['is_applied'] else 'No'}")
            print(f"    Created: {trade['created_at']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_trades())
