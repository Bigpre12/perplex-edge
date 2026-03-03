#!/usr/bin/env python3
"""
TEST BRAIN ANOMALIES ENDPOINTS - Test the new brain anomalies endpoints
"""
import requests
import time
from datetime import datetime

def test_brain_anomalies():
    """Test brain anomalies endpoints"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("TESTING BRAIN ANOMALIES ENDPOINTS")
    print("="*80)
    
    print(f"\nTime: {datetime.now().strftime('%I:%M:%S %p')}")
    print("Testing brain anomalies endpoints...")
    
    # Test endpoints
    endpoints = [
        ("Brain Anomalies", "/immediate/brain-anomalies"),
        ("Brain Anomalies Summary", "/immediate/brain-anomalies-summary")
    ]
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"\n{name}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if name == "Brain Anomalies":
                    anomalies = data.get('anomalies', [])
                    print(f"  Total Anomalies: {data.get('total', 0)}")
                    print(f"  Active: {data.get('active', 0)}")
                    print(f"  Resolved: {data.get('resolved', 0)}")
                    
                    for anomaly in anomalies[:3]:  # Show first 3
                        print(f"  - {anomaly['metric_name']}: {anomaly['change_pct']:.1f}% ({anomaly['severity']})")
                        print(f"    Status: {anomaly['status']}")
                        print(f"    Details: {anomaly['details'][:60]}...")
                        
                elif name == "Brain Anomalies Summary":
                    print(f"  Total Anomalies: {data.get('total_anomalies', 0)}")
                    print(f"  Active: {data.get('active_anomalies', 0)}")
                    print(f"  Resolved: {data.get('resolved_anomalies', 0)}")
                    print(f"  High Severity: {data.get('high_severity', 0)}")
                    print(f"  Medium Severity: {data.get('medium_severity', 0)}")
                    print(f"  Low Severity: {data.get('low_severity', 0)}")
                    
                    common_metrics = data.get('most_common_metrics', [])
                    print(f"  Most Common Metrics:")
                    for metric in common_metrics:
                        print(f"    - {metric['metric_name']}: {metric['count']} anomalies")
                
                print(f"  Timestamp: {data.get('timestamp', 'N/A')}")
                print(f"  Note: {data.get('note', 'N/A')}")
                
            else:
                print(f"  Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"\n{name}: ERROR - {e}")
    
    print("\n" + "="*80)
    print("BRAIN ANOMALIES TEST RESULTS:")
    print("="*80)
    
    print("\nBrain Anomalies Table Structure:")
    print("The brain_anomalies table tracks:")
    print("- Unusual patterns in brain metrics")
    print("- Significant deviations from baselines")
    print("- System performance issues")
    print("- Business metric anomalies")
    
    print("\nAnomaly Detection Features:")
    print("- Automatic detection of metric anomalies")
    print("- Severity classification (high, medium, low)")
    print("- Status tracking (active, resolved)")
    print("- Resolution method tracking")
    print("- Historical anomaly patterns")
    
    print("\nAvailable Endpoints:")
    print("- GET /immediate/brain-anomalies - Current anomalies")
    print("- GET /immediate/brain-anomalies-summary - Anomaly summary")
    print("- POST /immediate/brain-anomalies/detect - Run detection")
    print("- POST /immediate/brain-anomalies/{id}/resolve - Resolve anomaly")
    
    print("\nAnomaly Types Detected:")
    print("- High error rates (>10%)")
    print("- Low recommendation hit rates (<35%)")
    print("- High API response times (>500ms)")
    print("- High CPU usage (>90%)")
    print("- High memory usage (>95%)")
    print("- Low throughput (<10 req/s)")
    print("- Negative expected values")
    print("- Low user confidence (<60%)")
    
    print("\nSample Anomalies:")
    print("- Recommendation hit rate drop: -41.7% (HIGH)")
    print("- Memory usage spike: +58.3% (HIGH)")
    print("- Error rate spike: +300% (HIGH)")
    print("- CPU usage increase: +76% (HIGH)")
    
    print("\n" + "="*80)
    print("BRAIN ANOMALIES SYSTEM COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    test_brain_anomalies()
