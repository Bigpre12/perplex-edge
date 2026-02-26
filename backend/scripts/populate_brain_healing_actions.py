#!/usr/bin/env python3
"""
POPULATE BRAIN HEALING ACTIONS - Initialize and populate the brain_healing_actions table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random
import uuid

async def populate_brain_healing_actions():
    """Populate brain_healing_actions table with initial data"""
    
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
                WHERE table_name = 'brain_healing_actions'
            )
        """)
        
        if not table_check:
            print("Creating brain_healing_actions table...")
            await conn.execute("""
                CREATE TABLE brain_healing_actions (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    action VARCHAR(100) NOT NULL,
                    target VARCHAR(100) NOT NULL,
                    reason TEXT,
                    result VARCHAR(20) DEFAULT 'pending',
                    duration_ms INTEGER,
                    details JSONB,
                    success_rate FLOAT,
                    consecutive_failures INTEGER DEFAULT 0
                )
            """)
            print("Table created")
        
        # Generate sample brain healing actions
        print("Generating sample brain healing action data...")
        
        healing_actions = [
            # Database connection healing
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=6),
                'action': 'increase_database_pool_size',
                'target': 'database_connection_pool',
                'reason': 'Database connection pool exhausted causing 8% error rate. Current pool size of 10 insufficient for peak load of 45 concurrent requests.',
                'result': 'successful',
                'duration_ms': 2340,
                'details': {
                    'initial_pool_size': 10,
                    'new_pool_size': 20,
                    'error_rate_before': 0.08,
                    'error_rate_after': 0.015,
                    'peak_concurrent_requests': 45,
                    'connection_timeout_ms': 5000,
                    'auto_scaling_enabled': True,
                    'monitoring_added': True
                },
                'success_rate': 0.85,
                'consecutive_failures': 0
            },
            # API response time healing
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=5),
                'action': 'add_response_caching_layer',
                'target': 'api_response_time',
                'reason': 'API response time increased to 450ms average (threshold: 200ms). Identified bottleneck in player props calculation without caching.',
                'result': 'successful',
                'duration_ms': 4560,
                'details': {
                    'avg_response_time_before': 450,
                    'avg_response_time_after': 95,
                    'cache_hit_rate': 0.78,
                    'cache_ttl_seconds': 300,
                    'cached_endpoints': ['player-props', 'parlays', 'metrics'],
                    'memory_usage_increase': 0.15,
                    'cpu_usage_decrease': 0.25
                },
                'success_rate': 0.92,
                'consecutive_failures': 0
            },
            # Memory leak healing
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=4),
                'action': 'restart_recommendation_service',
                'target': 'memory_leak_recommendation_engine',
                'reason': 'Memory usage consistently increasing to 95% over 2-hour period. Memory leak detected in recommendation engine component.',
                'result': 'successful',
                'duration_ms': 12340,
                'details': {
                    'memory_usage_before': 0.95,
                    'memory_usage_after': 0.42,
                    'service_downtime_ms': 2340,
                    'affected_components': ['recommendation_engine', 'model_optimizer'],
                    'root_cause': 'unreleased model references',
                    'fix_applied': 'automatic garbage collection',
                    'monitoring_added': True
                },
                'success_rate': 0.78,
                'consecutive_failures': 1
            },
            # Model accuracy healing
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=3),
                'action': 'retrain_prediction_model',
                'target': 'model_accuracy_degradation',
                'reason': 'Model accuracy dropped from 68% to 52% over 24 hours. Detected concept drift in passing yards predictions.',
                'result': 'successful',
                'duration_ms': 45670,
                'details': {
                    'accuracy_before': 0.52,
                    'accuracy_after': 0.71,
                    'model_type': 'passing_yards_predictor',
                    'training_data_points': 15000,
                    'validation_accuracy': 0.69,
                    'training_time_ms': 45670,
                    'feature_importance_updated': True,
                    'regularization_adjusted': True
                },
                'success_rate': 0.88,
                'consecutive_failures': 0
            },
            # External API healing
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=2),
                'action': 'switch_to_backup_odds_provider',
                'target': 'external_odds_api_failure',
                'reason': 'Primary odds API provider experiencing 40% timeout rate. Backup provider available with 99% uptime.',
                'result': 'successful',
                'duration_ms': 890,
                'details': {
                    'primary_provider': 'the_odds_api',
                    'backup_provider': 'sportsdata_io',
                    'timeout_rate_before': 0.40,
                    'timeout_rate_after': 0.01,
                    'data_consistency_check': 'passed',
                    'switch_over_time_ms': 234,
                    'auto_failover_enabled': True
                },
                'success_rate': 0.95,
                'consecutive_failures': 0
            },
            # CPU usage healing
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=1),
                'action': 'scale_horizontal_processing',
                'target': 'high_cpu_usage_parlay_builder',
                'reason': 'CPU usage sustained at 92% during parlay construction. Single-threaded processing insufficient for peak load.',
                'result': 'successful',
                'duration_ms': 5670,
                'details': {
                    'cpu_usage_before': 0.92,
                    'cpu_usage_after': 0.45,
                    'processing_threads_before': 1,
                    'processing_threads_after': 4,
                    'parlay_construction_time_before': 2340,
                    'parlay_construction_time_after': 590,
                    'horizontal_scaling_factor': 4,
                    'load_balancer_configured': True
                },
                'success_rate': 0.91,
                'consecutive_failures': 0
            },
            # User confidence healing
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=30),
                'action': 'adjust_confidence_calculation',
                'target': 'user_confidence_decline',
                'reason': 'User confidence scores dropped 15% after series of poor recommendations. Psychological overconfidence identified as factor.',
                'result': 'pending',
                'duration_ms': 1230,
                'details': {
                    'confidence_before': 0.92,
                    'confidence_after': 0.85,
                    'user_trust_before': 0.68,
                    'user_trust_after': 'pending',
                    'confidence_cap_applied': 0.85,
                    'internal_accuracy_preserved': True,
                    'ab_test_planned': True
                },
                'success_rate': 0.0,
                'consecutive_failures': 0
            },
            # Network latency healing
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=15),
                'action': 'optimize_network_routing',
                'target': 'network_latency_spike',
                'reason': 'Network latency increased to 350ms (baseline: 45ms). Identified inefficient routing to database server.',
                'result': 'successful',
                'duration_ms': 3450,
                'details': {
                    'latency_before': 350,
                    'latency_after': 42,
                    'routing_optimization': 'connection_pooling',
                    'database_connection_reused': True,
                    'connection_multiplexing_enabled': True,
                    'network_path_optimized': True
                },
                'success_rate': 0.96,
                'consecutive_failures': 0
            },
            # Disk space healing
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=5),
                'action': 'cleanup_old_logs',
                'target': 'disk_space_exhaustion',
                'reason': 'Disk usage reached 94% capacity. Old log files consuming 45GB of space. Automatic cleanup triggered.',
                'result': 'successful',
                'duration_ms': 1890,
                'details': {
                    'disk_usage_before': 0.94,
                    'disk_usage_after': 0.67,
                    'space_freed_gb': 45,
                    'logs_retention_days': 7,
                    'compression_enabled': True,
                    'automatic_cleanup_scheduled': True,
                    'monitoring_threshold': 0.80
                },
                'success_rate': 0.89,
                'consecutive_failures': 0
            }
        ]
        
        # Insert healing actions
        for action in healing_actions:
            await conn.execute("""
                INSERT INTO brain_healing_actions (
                    timestamp, action, target, reason, result, duration_ms,
                    details, success_rate, consecutive_failures
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
                action['timestamp'],
                action['action'],
                action['target'],
                action['reason'],
                action['result'],
                action['duration_ms'],
                json.dumps(action['details']),
                action['success_rate'],
                action['consecutive_failures']
            )
        
        print("Sample brain healing actions populated successfully")
        
        # Get healing action statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_actions,
                COUNT(CASE WHEN result = 'successful' THEN 1 END) as successful_actions,
                COUNT(CASE WHEN result = 'pending' THEN 1 END) as pending_actions,
                COUNT(CASE WHEN result = 'failed' THEN 1 END) as failed_actions,
                AVG(duration_ms) as avg_duration_ms,
                AVG(success_rate) as avg_success_rate,
                MAX(consecutive_failures) as max_consecutive_failures
            FROM brain_healing_actions
        """)
        
        print(f"\nHealing Action Statistics:")
        print(f"  Total: {stats['total_actions']}")
        print(f"  Successful: {stats['successful_actions']}")
        print(f"  Pending: {stats['pending_actions']}")
        print(f"  Failed: {stats['failed_actions']}")
        print(f"  Avg Duration: {stats['avg_duration_ms']:.0f}ms")
        print(f"  Avg Success Rate: {stats['avg_success_rate']:.2%}")
        print(f"  Max Consecutive Failures: {stats['max_consecutive_failures']}")
        
        # Get action type breakdown
        action_types = await conn.fetch("""
            SELECT action, COUNT(*) as count, 
                   COUNT(CASE WHEN result = 'successful' THEN 1 END) as successful,
                   AVG(duration_ms) as avg_duration
            FROM brain_healing_actions 
            GROUP BY action
            ORDER BY count DESC
        """)
        
        print(f"\nHealing Action Types:")
        for action in action_types:
            success_rate = (action['successful'] / action['count'] * 100) if action['count'] > 0 else 0
            print(f"  {action['action']}: {action['count']} actions ({success_rate:.1f}% success, {action['avg_duration']:.0f}ms avg)")
        
        # Get target breakdown
        targets = await conn.fetch("""
            SELECT target, COUNT(*) as count,
                   COUNT(CASE WHEN result = 'successful' THEN 1 END) as successful
            FROM brain_healing_actions 
            GROUP BY target
            ORDER BY count DESC
        """)
        
        print(f"\nHealing Targets:")
        for target in targets:
            success_rate = (target['successful'] / target['count'] * 100) if target['count'] > 0 else 0
            print(f"  {target['target']}: {target['count']} actions ({success_rate:.1f}% success)")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_brain_healing_actions())
