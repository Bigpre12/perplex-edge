#!/usr/bin/env python3
"""
TEST BRAIN METRICS ENDPOINTS - Test the new brain metrics endpoints
"""
import requests
import time
from datetime import datetime

def test_brain_metrics():
    """Test brain metrics endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING BRAIN METRICS ENDPOINTS")
    print("="*80)
    
    print(f"\nTime: {datetime.now().strftime('%I:%M:%S %p')}")
    print("Testing brain metrics endpoints...")
    
    # Test endpoints
    endpoints = [
        ("Brain Metrics", "/immediate/brain-metrics"),
        ("Brain Metrics Summary", "/immediate/brain-metrics-summary"),
        ("Brain Metrics Summary 7d", "/immediate/brain-metrics-summary?hours=168")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"\n{name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if name == "Brain Metrics":
                    print(f"  Total Recommendations: {data.get('total_recommendations', 0)}")
                    print(f"  Hit Rate: {data.get('recommendation_hit_rate', 0):.2%}")
                    print(f"  Average EV: {data.get('average_ev', 0):.2%}")
                    print(f"  CLV Trend: {data.get('clv_trend', 0):.2%}")
                    print(f"  Prop Volume: {data.get('prop_volume', 0)}")
                    print(f"  User Confidence: {data.get('user_confidence_score', 0):.2%}")
                    print(f"  API Response Time: {data.get('api_response_time_ms', 0)}ms")
                    print(f"  Error Rate: {data.get('error_rate', 0):.2%}")
                    print(f"  Throughput: {data.get('throughput', 0):.1f} req/s")
                    
                    system = data.get('system_metrics', {})
                    print(f"  CPU Usage: {system.get('cpu_usage', 0):.1%}")
                    print(f"  Memory Usage: {system.get('memory_usage', 0):.1%}")
                    print(f"  Disk Usage: {system.get('disk_usage', 0):.1%}")
                    
                elif "Summary" in name:
                    print(f"  Period: {data.get('period_hours', 0)} hours")
                    print(f"  Total Records: {data.get('total_records', 0)}")
                    print(f"  Total Recommendations: {data.get('total_recommendations', 0)}")
                    print(f"  Average Hit Rate: {data.get('average_hit_rate', 0):.2%}")
                    print(f"  Average EV: {data.get('average_ev', 0):.2%}")
                    print(f"  Max Hit Rate: {data.get('max_hit_rate', 0):.2%}")
                    print(f"  Min Hit Rate: {data.get('min_hit_rate', 0):.2%}")
                    print(f"  Avg CPU Usage: {data.get('avg_cpu_usage', 0):.1%}")
                    print(f"  Avg Memory Usage: {data.get('avg_memory_usage', 0):.1%}")
                    print(f"  Avg Disk Usage: {data.get('avg_disk_usage', 0):.1%}")
                
                print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
                print(f"  Note: {data.get('note', 'N/A')}")
                
            else:
                print(f"  Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"\n{name}: ERROR - {e}")
    
    print("\n" + "="*80)
    print("BRAIN METRICS TEST RESULTS:")
    print("="*80)
    
    print("\nBrain Metrics Table Population:")
    print("The brain_business_metrics table should contain:")
    print("- Business metrics (recommendations, hit rates, EV)")
    print("- System metrics (CPU, memory, disk usage)")
    print("- API performance metrics (response time, error rate)")
    print("- Historical data for trend analysis")
    
    print("\nAvailable Endpoints:")
    print("- GET /immediate/brain-metrics - Current metrics")
    print("- GET /immediate/brain-metrics-summary - Summary for N hours")
    
    print("\nData Structure:")
    print("- total_recommendations: Number of recommendations made")
    print("- recommendation_hit_rate: Success rate of recommendations")
    print("- average_ev: Average expected value")
    print("- clv_trend: CLV (Closing Line Value) trend")
    print("- prop_volume: Number of props processed")
    print("- user_confidence_score: User confidence in recommendations")
    print("- api_response_time_ms: API response time in milliseconds")
    print("- error_rate: API error rate")
    print("- throughput: Requests per second")
    print("- cpu_usage, memory_usage, disk_usage: System resource usage")
    
    print("\n" + "="*80)
    print("BRAIN METRICS ENDPOINTS TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_brain_metrics()
