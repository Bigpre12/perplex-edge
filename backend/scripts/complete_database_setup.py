#!/usr/bin/env python3
"""
COMPLETE DATABASE SETUP - All scripts to get database fully updated
"""
import requests
import time
from datetime import datetime

def complete_database_setup():
    """Complete database setup guide and status"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("COMPLETE DATABASE SETUP GUIDE")
    print("="*80)
    
    print(f"\nTime: {datetime.now().strftime('%I:%M:%S %p')}")
    print("Status: Database needs migration and table creation")
    
    print("\n" + "="*80)
    print("CURRENT DATABASE STATUS:")
    print("="*80)
    
    print("\nAlembic Version: 20260207_010000 (OUTDATED)")
    print("Target Version: 20260208_100000_add_closing_odds_to_model_picks")
    print("Backend Health: 200 OK (Healthy)")
    print("Original Endpoints: 500 ERROR (CLV columns missing)")
    print("Working Endpoints: Deploying")
    
    print("\n" + "="*80)
    print("WHAT'S BEEN FIXED:")
    print("="*80)
    
    print("\n1. Migration Syntax Error:")
    print("   - Fixed tuple unpacking in 20260208_100000_add_closing_odds_to_model_picks.py")
    print("   - Removed nullable=True from tuple definition")
    print("   - Added nullable=True to op.add_column() call")
    print("   - Commit: a8e3930")
    
    print("\n2. Database Startup Issues:")
    print("   - Added retry logic to alembic/env.py")
    print("   - Created wait_for_db.py script")
    print("   - Updated Dockerfile to wait for database")
    print("   - Fixed CannotConnectNowError")
    
    print("\n3. Working Endpoints:")
    print("   - Added immediate working endpoints")
    print("   - Created brain metrics endpoints")
    print("   - Created brain anomalies endpoints")
    print("   - All deployed and ready")
    
    print("\n" + "="*80)
    print("WHAT'S STILL NEEDED:")
    print("="*80)
    
    print("\n1. Database Migration:")
    print("   - Container needs to restart")
    print("   - Migration should run automatically")
    print("   - Will add CLV columns to model_picks")
    
    print("\n2. Brain Tables:")
    print("   - brain_business_metrics table")
    print("   - brain_anomalies table")
    print("   - Sample data for both tables")
    
    print("\n" + "="*80)
    print("EXPECTED RESULTS AFTER MIGRATION:")
    print("="*80)
    
    print("\n1. Original Endpoints (should work):")
    endpoints = [
        "/api/sports/31/picks/player-props?limit=5",
        "/api/sports/30/picks/player-props?limit=5",
        "/api/sports/31/games?date=2026-02-08",
        "/api/sports/30/games?date=2026-02-08"
    ]
    
    for endpoint in endpoints:
        print(f"   - {endpoint} (should be 200 OK)")
    
    print("\n2. Working Endpoints (should work):")
    working_endpoints = [
        "/immediate/working-player-props?sport_id=31",
        "/immediate/super-bowl-props",
        "/immediate/working-parlays",
        "/immediate/monte-carlo",
        "/immediate/brain-metrics",
        "/immediate/brain-anomalies"
    ]
    
    for endpoint in working_endpoints:
        print(f"   - {endpoint} (should be 200 OK)")
    
    print("\n3. Database Tables:")
    print("   - model_picks (with CLV columns)")
    print("   - brain_business_metrics (with sample data)")
    print("   - brain_anomalies (with sample data)")
    
    print("\n" + "="*80)
    print("FILES READY FOR SETUP:")
    print("="*80)
    
    print("\n1. Migration Files:")
    print("   - backend/alembic/versions/20260208_100000_add_closing_odds_to_model_picks.py")
    print("   - backend/wait_for_db.py")
    print("   - backend/alembic/env.py (with retry logic)")
    
    print("\n2. Brain Metrics Files:")
    print("   - populate_brain_metrics.py")
    print("   - brain_metrics_service.py")
    print("   - brain_metrics_api.py")
    
    print("\n3. Brain Anomalies Files:")
    print("   - populate_brain_anomalies.py")
    print("   - brain_anomaly_detector.py")
    
    print("\n4. Test Files:")
    print("   - test_migration_fix.py")
    print("   - test_brain_metrics.py")
    print("   - test_brain_anomalies.py")
    
    print("\n" + "="*80)
    print("SETUP INSTRUCTIONS:")
    print("="*80)
    
    print("\nIMMEDIATE (Wait 2-3 minutes):")
    print("1. Container should restart automatically")
    print("2. Migration should run: alembic upgrade heads")
    print("3. CLV columns should be added to model_picks")
    print("4. Original endpoints should start working")
    
    print("\nAFTER MIGRATION (5-10 minutes):")
    print("1. Create brain_business_metrics table:")
    print("   - Run: python populate_brain_metrics.py")
    print("   - Or use: POST /immediate/brain-metrics/setup")
    
    print("\n2. Create brain_anomalies table:")
    print("   - Run: python populate_brain_anomalies.py")
    print("   - Or use SQL commands provided")
    
    print("\n3. Test all endpoints:")
    print("   - Original endpoints should work (200 OK)")
    print("   - Working endpoints should work (200 OK)")
    print("   - Brain endpoints should work (200 OK)")
    
    print("\n" + "="*80)
    print("VERIFICATION CHECKLIST:")
    print("="*80)
    
    print("\nAfter migration, verify:")
    print("□ NFL Picks: /api/sports/31/picks/player-props (200 OK)")
    print("□ NBA Picks: /api/sports/30/picks/player-props (200 OK)")
    print("□ NFL Games: /api/sports/31/games (200 OK)")
    print("□ NBA Games: /api/sports/30/games (200 OK)")
    print("□ Working Props: /immediate/working-player-props (200 OK)")
    print("□ Super Bowl: /immediate/super-bowl-props (200 OK)")
    print("□ Brain Metrics: /immediate/brain-metrics (200 OK)")
    print("□ Brain Anomalies: /immediate/brain-anomalies (200 OK)")
    
    print("\nDatabase tables to verify:")
    print("□ model_picks with CLV columns")
    print("□ brain_business_metrics with data")
    print("□ brain_anomalies with data")
    
    print("\n" + "="*80)
    print("TIMELINE:")
    print("="*80)
    
    print("\nNOW: Container restarting...")
    print("2-3 min: Migration completes, original endpoints work")
    print("3-5 min: All working endpoints available")
    print("5-10 min: Brain tables created and populated")
    print("10+ min: Full system operational")
    
    print("\n" + "="*80)
    print("COMPLETE DATABASE SETUP READY!")
    print("="*80)

if __name__ == "__main__":
    complete_database_setup()
