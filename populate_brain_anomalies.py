#!/usr/bin/env python3
"""
POPULATE BRAIN ANOMALIES - Initialize and populate the brain_anomalies table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random

async def populate_brain_anomalies():
    """Populate brain_anomalies table with initial data"""
    
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
                WHERE table_name = 'brain_anomalies'
            )
        """)
        
        if not table_check:
            print("Creating brain_anomalies table...")
            await conn.execute("""
                CREATE TABLE brain_anomalies (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    metric_name VARCHAR(100) NOT NULL,
                    baseline_value FLOAT NOT NULL,
                    current_value FLOAT NOT NULL,
                    change_pct FLOAT NOT NULL,
                    severity VARCHAR(20) DEFAULT 'medium',
                    status VARCHAR(20) DEFAULT 'active',
                    details TEXT,
                    resolved_at TIMESTAMP WITH TIME ZONE,
                    resolution_method VARCHAR(100)
                )
            """)
            print("Table created")
        
        # Generate sample anomalies
        print("Generating sample anomaly data...")
        
        anomalies = [
            # High error rate anomaly
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=6),
                'metric_name': 'error_rate',
                'baseline_value': 0.02,
                'current_value': 0.08,
                'change_pct': 300.0,
                'severity': 'high',
                'status': 'resolved',
                'details': 'API error rate spiked to 8% due to database connection issues',
                'resolved_at': datetime.now(timezone.utc) - timedelta(hours=5),
                'resolution_method': 'Database connection pool increased'
            },
            # Low hit rate anomaly
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=12),
                'metric_name': 'recommendation_hit_rate',
                'baseline_value': 0.60,
                'current_value': 0.35,
                'change_pct': -41.7,
                'severity': 'high',
                'status': 'active',
                'details': 'Recommendation hit rate dropped significantly during market volatility',
                'resolved_at': None,
                'resolution_method': None
            },
            # High response time anomaly
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=18),
                'metric_name': 'api_response_time_ms',
                'baseline_value': 100,
                'current_value': 450,
                'change_pct': 350.0,
                'severity': 'medium',
                'status': 'resolved',
                'details': 'API response time increased due to high traffic volume',
                'resolved_at': datetime.now(timezone.utc) - timedelta(hours=16),
                'resolution_method': 'Added caching layer'
            },
            # CPU usage anomaly
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=24),
                'metric_name': 'cpu_usage',
                'baseline_value': 0.50,
                'current_value': 0.92,
                'change_pct': 84.0,
                'severity': 'high',
                'status': 'resolved',
                'details': 'CPU usage spiked due to memory leak in recommendation engine',
                'resolved_at': datetime.now(timezone.utc) - timedelta(hours=22),
                'resolution_method': 'Fixed memory leak and restarted service'
            },
            # Low throughput anomaly
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=30),
                'metric_name': 'throughput',
                'baseline_value': 30.0,
                'current_value': 12.5,
                'change_pct': -58.3,
                'severity': 'medium',
                'status': 'resolved',
                'details': 'Throughput decreased due to network latency issues',
                'resolved_at': datetime.now(timezone.utc) - timedelta(hours=28),
                'resolution_method': 'Optimized network configuration'
            },
            # Memory usage anomaly
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=36),
                'metric_name': 'memory_usage',
                'baseline_value': 0.60,
                'current_value': 0.95,
                'change_pct': 58.3,
                'severity': 'high',
                'status': 'active',
                'details': 'Memory usage approaching critical levels',
                'resolved_at': None,
                'resolution_method': None
            },
            # Low user confidence anomaly
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=48),
                'metric_name': 'user_confidence_score',
                'baseline_value': 0.85,
                'current_value': 0.65,
                'change_pct': -23.5,
                'severity': 'medium',
                'status': 'resolved',
                'details': 'User confidence dropped after series of poor recommendations',
                'resolved_at': datetime.now(timezone.utc) - timedelta(hours=45),
                'resolution_method': 'Improved recommendation algorithm'
            },
            # Negative EV anomaly
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=60),
                'metric_name': 'average_ev',
                'baseline_value': 0.15,
                'current_value': -0.05,
                'change_pct': -133.3,
                'severity': 'high',
                'status': 'resolved',
                'details': 'Average expected value turned negative due to market inefficiency',
                'resolved_at': datetime.now(timezone.utc) - timedelta(hours=58),
                'resolution_method': 'Updated market data sources'
            },
            # Low prop volume anomaly
            {
                'timestamp': datetime.now(timezone.utc) - timedelta(hours=72),
                'metric_name': 'prop_volume',
                'baseline_value': 400,
                'current_value': 150,
                'change_pct': -62.5,
                'severity': 'medium',
                'status': 'resolved',
                'details': 'Prop volume decreased during off-season period',
                'resolved_at': datetime.now(timezone.utc) - timedelta(hours=70),
                'resolution_method': 'Seasonal adjustment - normal pattern'
            }
        ]
        
        # Insert anomalies
        for anomaly in anomalies:
            await conn.execute("""
                INSERT INTO brain_anomalies (
                    timestamp, metric_name, baseline_value, current_value, change_pct,
                    severity, status, details, resolved_at, resolution_method
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, 
                anomaly['timestamp'],
                anomaly['metric_name'],
                anomaly['baseline_value'],
                anomaly['current_value'],
                anomaly['change_pct'],
                anomaly['severity'],
                anomaly['status'],
                anomaly['details'],
                anomaly['resolved_at'],
                anomaly['resolution_method']
            )
        
        print("Sample anomalies populated successfully")
        
        # Get current anomalies
        current_anomalies = await conn.fetch("""
            SELECT * FROM brain_anomalies 
            WHERE status = 'active'
            ORDER BY timestamp DESC
        """)
        
        print(f"\nActive anomalies: {len(current_anomalies)}")
        for anomaly in current_anomalies:
            print(f"  - {anomaly['metric_name']}: {anomaly['change_pct']:.1f}% change ({anomaly['severity']})")
        
        # Get anomaly statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_anomalies,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_anomalies,
                COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_anomalies,
                COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_severity,
                COUNT(CASE WHEN severity = 'medium' THEN 1 END) as medium_severity,
                COUNT(CASE WHEN severity = 'low' THEN 1 END) as low_severity
            FROM brain_anomalies
        """)
        
        print(f"\nAnomaly Statistics:")
        print(f"  Total: {stats['total_anomalies']}")
        print(f"  Active: {stats['active_anomalies']}")
        print(f"  Resolved: {stats['resolved_anomalies']}")
        print(f"  High Severity: {stats['high_severity']}")
        print(f"  Medium Severity: {stats['medium_severity']}")
        print(f"  Low Severity: {stats['low_severity']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_brain_anomalies())
