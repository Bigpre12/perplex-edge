#!/usr/bin/env python3
"""
POPULATE BRAIN SYSTEM STATE - Initialize and populate the brain_system_state table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_brain_system_state():
    """Populate brain_system_state table with initial data"""
    
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
                WHERE table_name = 'brain_system_state'
            )
        """)
        
        if not table_check:
            print("Creating brain_system_state table...")
            await conn.execute("""
                CREATE TABLE brain_system_state (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    cycle_count INTEGER DEFAULT 0,
                    overall_status VARCHAR(20) DEFAULT 'initializing',
                    heals_attempted INTEGER DEFAULT 0,
                    heals_succeeded INTEGER DEFAULT 0,
                    consecutive_failures INTEGER DEFAULT 0,
                    sport_priority VARCHAR(20) DEFAULT 'balanced',
                    quota_budget INTEGER DEFAULT 100,
                    auto_commit_enabled BOOLEAN DEFAULT TRUE,
                    git_commits_made INTEGER DEFAULT 0,
                    betting_opportunities_found INTEGER DEFAULT 0,
                    strong_bets_identified INTEGER DEFAULT 0,
                    last_betting_scan TIMESTAMP WITH TIME ZONE,
                    top_betting_opportunities JSONB,
                    last_cycle_duration_ms INTEGER,
                    uptime_hours FLOAT DEFAULT 0.0
                )
            """)
            print("Table created")
        
        # Generate sample brain system state data
        print("Generating sample brain system state data...")
        
        system_states = [
            # Initial system state
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=72),
                'cycle_count': 0,
                'overall_status': 'initializing',
                'heals_attempted': 0,
                'heals_succeeded': 0,
                'consecutive_failures': 0,
                'sport_priority': 'balanced',
                'quota_budget': 100,
                'auto_commit_enabled': True,
                'git_commits_made': 0,
                'betting_opportunities_found': 0,
                'strong_bets_identified': 0,
                'last_betting_scan': None,
                'top_betting_opportunities': {
                    'total_opportunities': 0,
                    'strong_bets': 0,
                    'medium_bets': 0,
                    'weak_bets': 0,
                    'sports_breakdown': {}
                },
                'last_cycle_duration_ms': 0,
                'uptime_hours': 0.0
            },
            # First successful cycle
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=48),
                'cycle_count': 1,
                'overall_status': 'healthy',
                'heals_attempted': 2,
                'heals_succeeded': 2,
                'consecutive_failures': 0,
                'sport_priority': 'nfl_priority',
                'quota_budget': 100,
                'auto_commit_enabled': True,
                'git_commits_made': 1,
                'betting_opportunities_found': 15,
                'strong_bets_identified': 3,
                'last_betting_scan': datetime.now(timezone.utc) - timedelta(hours=48),
                'top_betting_opportunities': {
                    'total_opportunities': 15,
                    'strong_bets': 3,
                    'medium_bets': 7,
                    'weak_bets': 5,
                    'sports_breakdown': {
                        'nfl': 8,
                        'nba': 4,
                        'mlb': 3
                    }
                },
                'last_cycle_duration_ms': 45000,
                'uptime_hours': 24.0
            },
            # System under stress
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=36),
                'cycle_count': 2,
                'overall_status': 'degraded',
                'heals_attempted': 5,
                'heals_succeeded': 3,
                'consecutive_failures': 2,
                'sport_priority': 'nfl_priority',
                'quota_budget': 80,
                'auto_commit_enabled': False,
                'git_commits_made': 2,
                'betting_opportunities_found': 8,
                'strong_bets_identified': 1,
                'last_betting_scan': datetime.now(timezone.utc) - timedelta(hours=36),
                'top_betting_opportunities': {
                    'total_opportunities': 8,
                    'strong_bets': 1,
                    'medium_bets': 3,
                    'weak_bets': 4,
                    'sports_breakdown': {
                        'nfl': 5,
                        'nba': 2,
                        'mlb': 1
                    }
                },
                'last_cycle_duration_ms': 78000,
                'uptime_hours': 36.0
            },
            # Recovery cycle
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=24),
                'cycle_count': 3,
                'overall_status': 'recovering',
                'heals_attempted': 8,
                'heals_succeeded': 6,
                'consecutive_failures': 1,
                'sport_priority': 'balanced',
                'quota_budget': 90,
                'auto_commit_enabled': True,
                'git_commits_made': 3,
                'betting_opportunities_found': 12,
                'strong_bets_identified': 2,
                'last_betting_scan': datetime.now(timezone.utc) - timedelta(hours=24),
                'top_betting_opportunities': {
                    'total_opportunities': 12,
                    'strong_bets': 2,
                    'medium_bets': 5,
                    'weak_bets': 5,
                    'sports_breakdown': {
                        'nfl': 6,
                        'nba': 4,
                        'mlb': 2
                    }
                },
                'last_cycle_duration_ms': 62000,
                'uptime_hours': 48.0
            },
            # Optimal performance
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=18),
                'cycle_count': 4,
                'overall_status': 'optimal',
                'heals_attempted': 10,
                'heals_succeeded': 9,
                'consecutive_failures': 0,
                'sport_priority': 'super_bowl_priority',
                'quota_budget': 100,
                'auto_commit_enabled': True,
                'git_commits_made': 5,
                'betting_opportunities_found': 25,
                'strong_bets_identified': 8,
                'last_betting_scan': datetime.now(timezone.utc) - timedelta(hours=18),
                'top_betting_opportunities': {
                    'total_opportunities': 25,
                    'strong_bets': 8,
                    'medium_bets': 10,
                    'weak_bets': 7,
                    'sports_breakdown': {
                        'nfl': 15,
                        'nba': 7,
                        'mlb': 3
                    }
                },
                'last_cycle_duration_ms': 38000,
                'uptime_hours': 54.0
            },
            # High activity period
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=12),
                'cycle_count': 5,
                'overall_status': 'active',
                'heals_attempted': 12,
                'heals_succeeded': 11,
                'consecutive_failures': 0,
                'sport_priority': 'multi_sport',
                'quota_budget': 120,
                'auto_commit_enabled': True,
                'git_commits_made': 7,
                'betting_opportunities_found': 35,
                'strong_bets_identified': 12,
                'last_betting_scan': datetime.now(timezone.utc) - timedelta(hours=12),
                'top_betting_opportunities': {
                    'total_opportunities': 35,
                    'strong_bets': 12,
                    'medium_bets': 15,
                    'weak_bets': 8,
                    'sports_breakdown': {
                        'nfl': 18,
                        'nba': 12,
                        'mlb': 5
                    }
                },
                'last_cycle_duration_ms': 42000,
                'uptime_hours': 60.0
            },
            # Maintenance mode
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=6),
                'cycle_count': 6,
                'overall_status': 'maintenance',
                'heals_attempted': 15,
                'heals_succeeded': 13,
                'consecutive_failures': 0,
                'sport_priority': 'low_priority',
                'quota_budget': 50,
                'auto_commit_enabled': False,
                'git_commits_made': 8,
                'betting_opportunities_found': 5,
                'strong_bets_identified': 1,
                'last_betting_scan': datetime.now(timezone.utc) - timedelta(hours=6),
                'top_betting_opportunities': {
                    'total_opportunities': 5,
                    'strong_bets': 1,
                    'medium_bets': 2,
                    'weak_bets': 2,
                    'sports_breakdown': {
                        'nfl': 3,
                        'nba': 2,
                        'mlb': 0
                    }
                },
                'last_cycle_duration_ms': 28000,
                'uptime_hours': 66.0
            },
            # Current state
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=3),
                'cycle_count': 7,
                'overall_status': 'healthy',
                'heals_attempted': 18,
                'heals_succeeded': 17,
                'consecutive_failures': 0,
                'sport_priority': 'super_bowl_priority',
                'quota_budget': 100,
                'auto_commit_enabled': True,
                'git_commits_made': 10,
                'betting_opportunities_found': 42,
                'strong_bets_identified': 15,
                'last_betting_scan': datetime.now(timezone.utc) - timedelta(hours=3),
                'top_betting_opportunities': {
                    'total_opportunities': 42,
                    'strong_bets': 15,
                    'medium_bets': 18,
                    'weak_bets': 9,
                    'sports_breakdown': {
                        'nfl': 25,
                        'nba': 12,
                        'mlb': 5
                    }
                },
                'last_cycle_duration_ms': 35000,
                'uptime_hours': 69.0
            },
            # Recent state
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=1),
                'cycle_count': 8,
                'overall_status': 'healthy',
                'heals_attempted': 20,
                'heals_succeeded': 19,
                'consecutive_failures': 0,
                'sport_priority': 'balanced',
                'quota_budget': 100,
                'auto_commit_enabled': True,
                'git_commits_made': 12,
                'betting_opportunities_found': 38,
                'strong_bets_identified': 14,
                'last_betting_scan': datetime.now(timezone.utc) - timedelta(hours=1),
                'top_betting_opportunities': {
                    'total_opportunities': 38,
                    'strong_bets': 14,
                    'medium_bets': 16,
                    'weak_bets': 8,
                    'sports_breakdown': {
                        'nfl': 22,
                        'nba': 11,
                        'mlb': 5
                    }
                },
                'last_cycle_duration_ms': 33000,
                'uptime_hours': 71.0
            },
            # Latest state
            {
                'timestamp': datetime.now(timezone.utc),
                'cycle_count': 9,
                'overall_status': 'optimal',
                'heals_attempted': 22,
                'heals_succeeded': 21,
                'consecutive_failures': 0,
                'sport_priority': 'super_bowl_priority',
                'quota_budget': 100,
                'auto_commit_enabled': True,
                'git_commits_made': 14,
                'betting_opportunities_found': 48,
                'strong_bets_identified': 18,
                'last_betting_scan': datetime.now(timezone.utc) - timedelta(minutes=30),
                'top_betting_opportunities': {
                    'total_opportunities': 48,
                    'strong_bets': 18,
                    'medium_bets': 20,
                    'weak_bets': 10,
                    'sports_breakdown': {
                        'nfl': 28,
                        'nba': 15,
                        'mlb': 5
                    }
                },
                'last_cycle_duration_ms': 31000,
                'uptime_hours': 72.0
            }
        ]
        
        # Insert system states
        for state in system_states:
            await conn.execute("""
                INSERT INTO brain_system_state (
                    timestamp, cycle_count, overall_status, heals_attempted, heals_succeeded,
                    consecutive_failures, sport_priority, quota_budget, auto_commit_enabled,
                    git_commits_made, betting_opportunities_found, strong_bets_identified,
                    last_betting_scan, top_betting_opportunities, last_cycle_duration_ms, uptime_hours
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
            """, 
                state['timestamp'],
                state['cycle_count'],
                state['overall_status'],
                state['heals_attempted'],
                state['heals_succeeded'],
                state['consecutive_failures'],
                state['sport_priority'],
                state['quota_budget'],
                state['auto_commit_enabled'],
                state['git_commits_made'],
                state['betting_opportunities_found'],
                state['strong_bets_identified'],
                state['last_betting_scan'],
                json.dumps(state['top_betting_opportunities']),
                state['last_cycle_duration_ms'],
                state['uptime_hours']
            )
        
        print("Sample brain system state data populated successfully")
        
        # Get system state statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_states,
                COUNT(CASE WHEN overall_status = 'optimal' THEN 1 END) as optimal_states,
                COUNT(CASE WHEN overall_status = 'healthy' THEN 1 END) as healthy_states,
                COUNT(CASE WHEN overall_status = 'degraded' THEN 1 END) as degraded_states,
                COUNT(CASE WHEN overall_status = 'maintenance' THEN 1 END) as maintenance_states,
                COUNT(CASE WHEN overall_status = 'recovering' THEN 1 END) as recovering_states,
                COUNT(CASE WHEN overall_status = 'active' THEN 1 END) as active_states,
                COUNT(CASE WHEN overall_status = 'initializing' THEN 1 END) as initializing_states,
                AVG(heals_attempted) as avg_heals_attempted,
                AVG(heals_succeeded) as avg_heals_succeeded,
                AVG(consecutive_failures) as avg_consecutive_failures,
                AVG(last_cycle_duration_ms) as avg_cycle_duration,
                AVG(uptime_hours) as avg_uptime,
                SUM(git_commits_made) as total_commits,
                SUM(betting_opportunities_found) as total_opportunities,
                SUM(strong_bets_identified) as total_strong_bets
            FROM brain_system_state
        """)
        
        print(f"\nSystem State Statistics:")
        print(f"  Total States: {stats['total_states']}")
        print(f"  Optimal: {stats['optimal_states']}")
        print(f"  Healthy: {stats['healthy_states']}")
        print(f"  Degraded: {stats['degraded_states']}")
        print(f"  Maintenance: {stats['maintenance_states']}")
        print(f"  Recovering: {stats['recovering_states']}")
        print(f"  Active: {stats['active_states']}")
        print(f"  Initializing: {stats['initializing_states']}")
        print(f"  Avg Heals Attempted: {stats['avg_heals_attempted']:.1f}")
        print(f"  Avg Heals Succeeded: {stats['avg_heals_succeeded']:.1f}")
        print(f"  Avg Consecutive Failures: {stats['avg_consecutive_failures']:.1f}")
        print(f"  Avg Cycle Duration: {stats['avg_cycle_duration_ms']:.0f}ms")
        print(f"  Avg Uptime: {stats['avg_uptime']:.1f} hours")
        print(f"  Total Git Commits: {stats['total_commits']}")
        print(f"  Total Opportunities: {stats['total_opportunities']}")
        print(f"  Total Strong Bets: {stats['total_strong_bets']}")
        
        # Get latest state
        latest = await conn.fetchrow("""
            SELECT * FROM brain_system_state 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        
        if latest:
            print(f"\nLatest System State:")
            print(f"  Status: {latest['overall_status']}")
            print(f"  Cycle Count: {latest['cycle_count']}")
            print(f"  Heals: {latest['heals_succeeded']}/{latest['heals_attempted']}")
            print(f"  Sport Priority: {latest['sport_priority']}")
            print(f"  Quota Budget: {latest['quota_budget']}")
            print(f"  Auto Commit: {latest['auto_commit_enabled']}")
            print(f"  Git Commits: {latest['git_commits_made']}")
            print(f"  Opportunities: {latest['betting_opportunities_found']}")
            print(f"  Strong Bets: {latest['strong_bets_identified']}")
            print(f"  Uptime: {latest['uptime_hours']:.1f} hours")
            print(f"  Last Cycle: {latest['last_cycle_duration_ms']}ms")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_brain_system_state())
