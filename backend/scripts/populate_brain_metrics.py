#!/usr/bin/env python3
"""
POPULATE BRAIN BUSINESS METRICS - Initialize and populate the brain_business_metrics table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
import random

async def populate_brain_metrics():
    """Populate brain_business_metrics table with initial data"""
    
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
                WHERE table_name = 'brain_business_metrics'
            )
        """)
        
        if not table_check:
            print("Creating brain_business_metrics table...")
            await conn.execute("""
                CREATE TABLE brain_business_metrics (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    total_recommendations INTEGER DEFAULT 0,
                    recommendation_hit_rate FLOAT DEFAULT 0.0,
                    average_ev FLOAT DEFAULT 0.0,
                    clv_trend FLOAT DEFAULT 0.0,
                    prop_volume INTEGER DEFAULT 0,
                    user_confidence_score FLOAT DEFAULT 0.0,
                    api_response_time_ms INTEGER DEFAULT 0,
                    error_rate FLOAT DEFAULT 0.0,
                    throughput FLOAT DEFAULT 0.0,
                    cpu_usage FLOAT DEFAULT 0.0,
                    memory_usage FLOAT DEFAULT 0.0,
                    disk_usage FLOAT DEFAULT 0.0
                )
            """)
            print("Table created")
        
        # Generate initial data for the last 7 days
        print("Generating initial metrics data...")
        
        base_time = datetime.now(timezone.utc) - timedelta(days=7)
        
        for i in range(168):  # 7 days * 24 hours
            timestamp = base_time + timedelta(hours=i)
            
            # Generate realistic metrics with some variation
            total_recommendations = random.randint(50, 200)
            recommendation_hit_rate = random.uniform(0.45, 0.65)  # 45-65% hit rate
            average_ev = random.uniform(0.05, 0.25)  # 5-25% average EV
            clv_trend = random.uniform(-0.1, 0.3)  # CLV trend
            prop_volume = random.randint(100, 500)
            user_confidence_score = random.uniform(0.7, 0.95)
            api_response_time_ms = random.randint(50, 300)
            error_rate = random.uniform(0.01, 0.05)  # 1-5% error rate
            throughput = random.uniform(10, 50)  # requests per second
            cpu_usage = random.uniform(0.2, 0.8)  # 20-80% CPU
            memory_usage = random.uniform(0.3, 0.7)  # 30-70% memory
            disk_usage = random.uniform(0.4, 0.6)  # 40-60% disk
            
            await conn.execute("""
                INSERT INTO brain_business_metrics (
                    timestamp, total_recommendations, recommendation_hit_rate, average_ev,
                    clv_trend, prop_volume, user_confidence_score, api_response_time_ms,
                    error_rate, throughput, cpu_usage, memory_usage, disk_usage
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            """, timestamp, total_recommendations, recommendation_hit_rate, average_ev,
                clv_trend, prop_volume, user_confidence_score, api_response_time_ms,
                error_rate, throughput, cpu_usage, memory_usage, disk_usage)
        
        print("Initial data populated successfully")
        
        # Get current metrics
        current_metrics = await conn.fetchrow("""
            SELECT * FROM brain_business_metrics 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        
        if current_metrics:
            print(f"\nCurrent metrics (as of {current_metrics['timestamp']}):")
            print(f"  Total Recommendations: {current_metrics['total_recommendations']}")
            print(f"  Hit Rate: {current_metrics['recommendation_hit_rate']:.2%}")
            print(f"  Average EV: {current_metrics['average_ev']:.2%}")
            print(f"  CLV Trend: {current_metrics['clv_trend']:.2%}")
            print(f"  Prop Volume: {current_metrics['prop_volume']}")
            print(f"  User Confidence: {current_metrics['user_confidence_score']:.2%}")
            print(f"  API Response Time: {current_metrics['api_response_time_ms']}ms")
            print(f"  Error Rate: {current_metrics['error_rate']:.2%}")
            print(f"  Throughput: {current_metrics['throughput']:.1f} req/s")
            print(f"  CPU Usage: {current_metrics['cpu_usage']:.1%}")
            print(f"  Memory Usage: {current_metrics['memory_usage']:.1%}")
            print(f"  Disk Usage: {current_metrics['disk_usage']:.1%}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate_brain_metrics())
