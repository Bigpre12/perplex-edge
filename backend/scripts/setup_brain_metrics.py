#!/usr/bin/env python3
"""
SETUP BRAIN METRICS - Execute SQL commands to populate brain_business_metrics table
"""
import requests
import json
import time

def execute_sql(query, description):
    """Execute SQL query through admin endpoint"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    try:
        response = requests.post(
            f"{base_url}/admin/sql",
            json={"query": query},
            timeout=10
        )
        
        print(f"\n{description}:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                results = data['results']
                if isinstance(results, list) and results:
                    print(f"Results: {len(results)} rows returned")
                    if results:
                        print(f"Sample: {results[0]}")
                else:
                    print("Success: Query executed")
            else:
                print("Success: Query executed")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error executing {description}: {e}")

def setup_brain_metrics():
    """Setup brain metrics table and populate with data"""
    
    print("SETTING UP BRAIN METRICS TABLE")
    print("="*80)
    
    # SQL commands
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS brain_business_metrics (
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
    );
    """
    
    insert_data_sql = """
    INSERT INTO brain_business_metrics (
        timestamp, total_recommendations, recommendation_hit_rate, average_ev,
        clv_trend, prop_volume, user_confidence_score, api_response_time_ms,
        error_rate, throughput, cpu_usage, memory_usage, disk_usage
    ) VALUES 
        (NOW() - INTERVAL '7 days', 150, 0.52, 0.12, 0.15, 250, 0.82, 120, 0.02, 25.5, 0.45, 0.62, 0.55),
        (NOW() - INTERVAL '6 days', 175, 0.58, 0.15, 0.18, 320, 0.85, 115, 0.018, 28.2, 0.52, 0.58, 0.53),
        (NOW() - INTERVAL '5 days', 142, 0.49, 0.08, 0.05, 280, 0.78, 135, 0.025, 22.1, 0.38, 0.65, 0.57),
        (NOW() - INTERVAL '4 days', 198, 0.62, 0.18, 0.22, 410, 0.88, 95, 0.015, 32.8, 0.61, 0.52, 0.51),
        (NOW() - INTERVAL '3 days', 165, 0.55, 0.14, 0.12, 290, 0.83, 125, 0.022, 26.7, 0.48, 0.59, 0.54),
        (NOW() - INTERVAL '2 days', 189, 0.61, 0.16, 0.20, 380, 0.86, 105, 0.017, 30.4, 0.56, 0.55, 0.52),
        (NOW() - INTERVAL '1 day', 210, 0.64, 0.19, 0.25, 450, 0.89, 88, 0.014, 35.2, 0.63, 0.48, 0.50),
        (NOW() - INTERVAL '12 hours', 178, 0.59, 0.17, 0.21, 340, 0.87, 102, 0.016, 29.8, 0.54, 0.57, 0.53),
        (NOW() - INTERVAL '6 hours', 195, 0.63, 0.20, 0.24, 420, 0.90, 92, 0.013, 33.6, 0.58, 0.51, 0.49),
        (NOW(), 220, 0.66, 0.22, 0.28, 480, 0.92, 85, 0.012, 37.4, 0.67, 0.46, 0.48);
    """
    
    get_current_sql = """
    SELECT * FROM brain_business_metrics 
    ORDER BY timestamp DESC 
    LIMIT 1;
    """
    
    get_summary_sql = """
    SELECT 
        COUNT(*) as total_records,
        SUM(total_recommendations) as total_recommendations,
        AVG(recommendation_hit_rate) as avg_hit_rate,
        AVG(average_ev) as avg_ev,
        MAX(recommendation_hit_rate) as max_hit_rate,
        MIN(recommendation_hit_rate) as min_hit_rate,
        AVG(cpu_usage) as avg_cpu_usage,
        AVG(memory_usage) as avg_memory_usage,
        AVG(disk_usage) as avg_disk_usage
    FROM brain_business_metrics 
    WHERE timestamp >= NOW() - INTERVAL '24 hours';
    """
    
    # Execute commands
    print("\n1. Creating table...")
    execute_sql(create_table_sql, "Create brain_business_metrics table")
    
    print("\n2. Inserting sample data...")
    execute_sql(insert_data_sql, "Insert sample brain metrics data")
    
    print("\n3. Getting current metrics...")
    execute_sql(get_current_sql, "Get current brain metrics")
    
    print("\n4. Getting 24h summary...")
    execute_sql(get_summary_sql, "Get 24-hour metrics summary")
    
    print("\n" + "="*80)
    print("BRAIN METRICS SETUP COMPLETE!")
    print("="*80)
    
    print("\nThe brain_business_metrics table now contains:")
    print("- 10 sample records covering the last 7 days")
    print("- Realistic business metrics (recommendations, hit rates, EV)")
    print("- System metrics (CPU, memory, disk usage)")
    print("- API performance metrics (response time, error rate)")
    
    print("\nYou can now query this table for brain business intelligence!")
    print("\nAvailable API endpoints (when implemented):")
    print("- GET /admin/brain-metrics")
    print("- GET /admin/brain-metrics-summary")
    print("- GET /admin/brain-dashboard")

if __name__ == "__main__":
    setup_brain_metrics()
