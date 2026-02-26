#!/usr/bin/env python3
"""
Check and launch all brain services
"""
import requests

def check_brain_services():
    """Check and launch all brain services"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING AND LAUNCHING ALL BRAIN SERVICES")
    print("="*80)
    
    # Check brain health
    print("\n1. Brain Health:")
    brain_health_url = f"{base_url}/admin/brain/health"
    
    try:
        response = requests.get(brain_health_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Brain Health: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check brain analyze
    print("\n2. Brain Analyze:")
    brain_analyze_url = f"{base_url}/admin/brain/analyze"
    
    try:
        response = requests.post(brain_analyze_url, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Brain Analysis: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check brain analyze auto-fix
    print("\n3. Brain Auto-Fix:")
    auto_fix_url = f"{base_url}/admin/brain/analyze/auto-fix"
    
    try:
        response = requests.post(auto_fix_url, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Auto-Fix: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check brain analyze commit
    print("\n4. Brain Analyze Commit:")
    commit_url = f"{base_url}/admin/brain/analyze/commit"
    
    try:
        response = requests.post(commit_url, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Commit: {data}")
        else:
            print(f"   Error: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check brain analyze expand
    print("\n5. Brain Analyze Expand:")
    expand_url = f"{base_url}/admin/brain/analyze/expand"
    
    try:
        response = requests.post(expand_url, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Expand: {data}")
        else:
            print(f"   Error: {response.status_code}")
    except Exception as e:
        print(f"   Analyze Expand Error: {e}")
    
    # Check brain analyze summary
    print("\n6. Brain Analyze Summary:")
    summary_url = f"{base_url}/admin/brain/analyze/summary"
    
    try:
        response = requests.get(summary_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Summary: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check if brain is processing picks
    print("\n7. Check Brain Pick Processing:")
    
    # Try to trigger pick generation
    try:
        gen_picks_url = f"{base_url}/admin/jobs/generate-picks?sport_id=30"
        response = requests.post(gen_picks_url, timeout=30)
        print(f"   Generate NBA Picks Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Result: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except:
        pass
    
    # Check if brain is monitoring
    print("\n8. Check Brain Monitoring:")
    monitoring_url = f"{base_url}/admin/monitoring/api"
    
    try:
        response = requests.get(monitoring_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Monitoring: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except:
        pass
    
    # Check brain metrics
    print("\n9. Check Brain Metrics:")
    metrics_url = f"{base_url}/admin/metrics/dashboard"
    
    try:
        response = requests.get(metrics_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Metrics: {data}")
        else:
            print(f"   Error: {response.text[:100]}")
    except:
        pass
    
    # Check if brain is connected to database
    print("\n10. Check Brain Database Connection:")
    try:
        # Try to get brain status through a query
        response = requests.post(f"{base_url}/admin/brain", json={"query": "SELECT 1;"}, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Brain DB Connection: Working")
        else:
            print(f"   Error: {response.text[:100]}")
    except:
        pass
    
    print("\n" + "="*80)
    print("BRAIN SERVICES STATUS:")
    print("- Brain Health: Checking...")
    print("- Brain Analyze: Checking...")
    print("- Auto-Fix: Checking...")
    print("- Pick Generation: Checking...")
    print("- Monitoring: Checking...")
    print("- Database Connection: Checking...")
    print("="*80)

if __name__ == "__main__":
    check_brain_services()
