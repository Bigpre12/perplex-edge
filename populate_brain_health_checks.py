#!/usr/bin/env python3
"""
POPULATE BRAIN HEALTH CHECKS - Initialize and populate the brain_health_checks table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random

async def populate_brain_health_checks():
    """Populate brain_health_checks table with initial data"""
    
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
                WHERE table_name = 'brain_health_checks'
            )
        """)
        
        if not table_check:
            print("Creating brain_health_checks table...")
            await conn.execute("""
                CREATE TABLE brain_health_checks (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    component VARCHAR(100) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    message TEXT,
                    details JSONB,
                    response_time_ms INTEGER,
                    error_count INTEGER DEFAULT 0
                )
            """)
            print("Table created")
        
        # Generate sample brain health check data
        print("Generating sample brain health check data...")
        
        health_checks = [
            # Database health checks
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=5),
                'component': 'database_connection_pool',
                'status': 'healthy',
                'message': 'Database connection pool operating normally',
                'details': {
                    'active_connections': 8,
                    'max_connections': 20,
                    'pool_utilization': 0.40,
                    'avg_response_time_ms': 45,
                    'connection_timeout_rate': 0.01,
                    'last_error': None,
                    'health_score': 0.95
                },
                'response_time_ms': 23,
                'error_count': 0
            },
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=10),
                'component': 'database_query_performance',
                'status': 'healthy',
                'message': 'Database query performance within acceptable ranges',
                'details': {
                    'avg_query_time_ms': 125,
                    'slow_query_threshold': 500,
                    'slow_queries_per_minute': 2,
                    'connection_utilization': 0.35,
                    'index_hit_rate': 0.89,
                    'table_scan_rate': 0.05,
                    'health_score': 0.88
                },
                'response_time_ms': 45,
                'error_count': 0
            },
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=15),
                'component': 'database_replication',
                'status': 'warning',
                'message': 'Replication lag slightly elevated but within limits',
                'details': {
                    'replication_lag_ms': 2500,
                    'max_acceptable_lag_ms': 5000,
                    'replica_status': 'connected',
                    'sync_health': 'good',
                    'last_sync_timestamp': (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat(),
                    'health_score': 0.75
                },
                'response_time_ms': 67,
                'error_count': 0
            },
            # API health checks
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=3),
                'component': 'api_response_time',
                'status': 'healthy',
                'message': 'API response times are optimal',
                'details': {
                    'avg_response_time_ms': 95,
                    'p95_response_time_ms': 180,
                    'p99_response_time_ms': 250,
                    'requests_per_second': 45.2,
                    'cache_hit_rate': 0.78,
                    'health_score': 0.92
                },
                'response_time_ms': 12,
                'error_count': 0
            },
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=8),
                'component': 'api_error_rate',
                'status': 'healthy',
                'message': 'API error rate within acceptable range',
                'details': {
                    'error_rate': 0.015,
                    'max_acceptable_error_rate': 0.05,
                    'total_requests': 15000,
                    'error_count_last_hour': 225,
                    'common_errors': ['timeout', 'rate_limit'],
                    'health_score': 0.85
                },
                'response_time_ms': 8,
                'error_count': 0
            },
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=12),
                'component': 'api_throughput',
                'status': 'healthy',
                'message': 'API throughput is healthy',
                'details': {
                    'requests_per_second': 45.2,
                    'max_capacity': 100,
                    'utilization': 0.45,
                    'peak_requests_per_second': 78,
                    'health_score': 0.90
                },
                'response_time_ms': 15,
                'error_count': 0
            },
            # Model health checks
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=6),
                'component': 'model_accuracy',
                'status': 'healthy',
                'message': 'Model accuracy is within acceptable range',
                'details': {
                    'current_accuracy': 0.71,
                    'minimum_acceptable_accuracy': 0.65,
                    'model_type': 'passing_yards_predictor',
                    'validation_accuracy': 0.69,
                    'last_training_date': (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                    'training_data_points': 15000,
                    'health_score': 0.82
                },
                'response_time_ms': 34,
                'error_count': 0
            },
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=20),
                'component': 'model_prediction_confidence',
                'status': 'warning',
                'message': 'Model prediction confidence slightly low for some markets',
                'details': {
                    'avg_confidence': 0.72,
                    'min_acceptable_confidence': 0.70,
                    'low_confidence_markets': ['complex_parlays', 'long_shot_props'],
                    'confidence_distribution': {
                        'high': 0.45,
                        'medium': 0.35,
                        'low': 0.20
                    },
                    'health_score': 0.68
                },
                'response_time_ms': 56,
                'error_count': 0
            },
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=25),
                'component': 'model_training_status',
                'status': 'healthy',
                'message': 'Model training system is operational',
                'details': {
                    'last_training_completed': (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                    'next_training_scheduled': (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
                    'training_queue_length': 0,
                    'model_version': 'v2.1.3',
                    'health_score': 0.95
                },
                'response_time_ms': 23,
                'error_count': 0
            },
            # System resource health checks
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=2),
                'component': 'memory_usage',
                'status': 'healthy',
                'message': 'Memory usage is within normal range',
                'details': {
                    'current_usage': 0.42,
                    'max_acceptable_usage': 0.85,
                    'available_memory_gb': 11.6,
                    'total_memory_gb': 20,
                    'gc_pressure': 'low',
                    'memory_leak_detected': False,
                    'health_score': 0.88
                },
                'response_time_ms': 18,
                'error_count': 0
            },
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=7),
                'component': 'cpu_usage',
                'status': 'healthy',
                'message': 'CPU usage is optimal',
                'details': {
                    'current_usage': 0.45,
                    'max_acceptable_usage': 0.80,
                    'cpu_cores': 8,
                    'load_average': [0.42, 0.48, 0.45, 0.43],
                    'process_count': 45,
                    'health_score': 0.91
                },
                'response_time_ms': 14,
                'error_count': 0
            },
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=18),
                'component': 'disk_space',
                'status': 'warning',
                'message': 'Disk usage approaching threshold',
                'details': {
                    'current_usage': 0.78,
                    'max_acceptable_usage': 0.90,
                    'available_space_gb': 4.4,
                    'total_space_gb': 20,
                    'disk_io_utilization': 0.35,
                    'health_score': 0.72
                },
                'response_time_ms': 28,
                'error_count': 0
            },
            # External service health checks
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=4),
                'component': 'external_odds_api',
                'status': 'healthy',
                'message': 'External odds API is responsive',
                'details': {
                    'provider': 'sportsdata_io',
                    'response_time_ms': 145,
                    'timeout_rate': 0.01,
                    'success_rate': 0.99,
                    'last_successful_request': (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
                    'health_score': 0.96
                },
                'response_time_ms': 145,
                'error_count': 0
            },
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=30),
                'component': 'backup_odds_api',
                'status': 'healthy',
                'message': 'Backup odds API is available',
                'details': {
                    'provider': 'the_odds_api',
                    'response_time_ms': 280,
                    'timeout_rate': 0.02,
                    'success_rate': 0.98,
                    'last_successful_request': (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                    'health_score': 0.88
                },
                'response_time_ms': 280,
                'error_count': 0
            },
            # Application health checks
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=1),
                'component': 'user_session_health',
                'status': 'healthy',
                'message': 'User sessions are functioning normally',
                'details': {
                    'active_sessions': 1247,
                    'max_concurrent_sessions': 2000,
                    'session_duration_avg_minutes': 23,
                    'authentication_success_rate': 0.98,
                    'session_timeout_rate': 0.02,
                    'health_score': 0.93
                },
                'response_time_ms': 19,
                'error_count': 0
            },
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=9),
                'component': 'recommendation_engine',
                'status': 'healthy',
                'message': 'Recommendation engine is performing well',
                'details': {
                    'recommendations_per_second': 15.2,
                    'avg_processing_time_ms': 89,
                    'queue_length': 3,
                    'success_rate': 0.85,
                    'confidence_avg': 0.78,
                    'health_score': 0.86
                },
                'response_time_ms': 41,
                'error_count': 0
            },
            # Parlay builder health
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=11),
                'component': 'parlay_builder',
                'status': 'healthy',
                'message': 'Parlay builder is operating normally',
                'details': {
                    'parlays_per_minute': 8.5,
                    'avg_construction_time_ms': 590,
                    'max_concurrent_builds': 10,
                    'success_rate': 0.92,
                    'complex_parlay_success_rate': 0.88,
                    'health_score': 0.89
                },
                'response_time_ms': 67,
                'error_count': 0
            },
            # Monitoring system health
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=13),
                'component': 'monitoring_system',
                'status': 'healthy',
                'message': 'Monitoring system is fully operational',
                'details': {
                    'metrics_collected_per_minute': 1200,
                    'alert_system_status': 'active',
                    'dashboard_refresh_rate': 30,
                    'data_retention_days': 30,
                    'monitoring_coverage': 0.95,
                    'health_score': 0.97
                },
                'response_time_ms': 8,
                'error_count': 0
            },
            # Brain system health
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=16),
                'component': 'brain_decision_system',
                'status': 'healthy',
                'message': 'Brain decision system is functioning optimally',
                'details': {
                    'decisions_per_hour': 45,
                    'avg_decision_time_ms': 426,
                    'success_rate': 0.75,
                    'active_healing_actions': 0,
                    'learning_loop_status': 'active',
                    'health_score': 0.82
                },
                'response_time_ms': 34,
                'error_count': 0
            },
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=22),
                'component': 'brain_healing_system',
                'status': 'healthy',
                'message': 'Brain healing system is ready',
                'details': {
                    'auto_healing_enabled': True,
                    'last_healing_cycle': (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                    'healing_success_rate': 0.889,
                    'active_monitors': 8,
                    'health_score': 0.91
                },
                'response_time_ms': 25,
                'error_count': 0
            },
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(minutes=28),
                'component': 'brain_anomaly_detection',
                'status': 'healthy',
                'message': 'Anomaly detection system is monitoring',
                'details': {
                    'active_anomalies': 2,
                    'anomalies_detected_today': 4,
                    'false_positive_rate': 0.05,
                    'detection_accuracy': 0.92,
                    'alert_response_time_avg_ms': 120,
                    'health_score': 0.88
                },
                'response_time_ms': 31,
                'error_count': 0
            }
        ]
        
        # Insert health checks
        for check in health_checks:
            await conn.execute("""
                INSERT INTO brain_health_checks (
                    timestamp, component, status, message, details,
                    response_time_ms, error_count
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, 
                check['timestamp'],
                check['component'],
                check['status'],
                check['message'],
                json.dumps(check['details']),
                check['response_time_ms'],
                check['error_count']
            )
        
        print("Sample brain health checks populated successfully")
        
        # Get health check statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_checks,
                COUNT(CASE WHEN status = 'healthy' THEN 1 END) as healthy_checks,
                COUNT(CASE WHEN status = 'warning' THEN 1 END) as warning_checks,
                COUNT(CASE WHEN status = 'critical' THEN 1 END) as critical_checks,
                COUNT(CASE WHEN status = 'error' THEN 1 END) as error_checks,
                AVG(response_time_ms) as avg_response_time_ms,
                AVG(error_count) as avg_error_count
            FROM brain_health_checks
        """)
        
        print(f"\nHealth Check Statistics:")
        print(f"  Total: {stats['total_checks']}")
        print(f"  Healthy: {stats['healthy_checks']}")
        print(f"  Warning: {stats['warning_checks']}")
        print(f"  Critical: {stats['critical_checks']}")
        print(f"  Error: {stats['error_checks']}")
        print(f"  Avg Response Time: {stats['avg_response_time_ms']:.0f}ms")
        print(f"  Avg Error Count: {stats['avg_error_count']:.1f}")
        
        # Get component breakdown
        components = await conn.fetch("""
            SELECT component, COUNT(*) as count, 
                   COUNT(CASE WHEN status = 'healthy' THEN 1 END) as healthy,
                   AVG(response_time_ms) as avg_response
            FROM brain_health_checks 
            GROUP BY component
            ORDER BY count DESC
        """)
        
        print(f"\nComponent Health:")
        for comp in components:
            health_rate = (comp['healthy'] / comp['count'] * 100) if comp['count'] > 0 else 0
            print(f"  {comp['component']}: {comp['count']} checks ({health_rate:.1f}% healthy, {comp['avg_response']:.0f}ms avg)")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_brain_health_checks())
