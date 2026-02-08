#!/usr/bin/env python3
"""
Check database schema for model_picks table
"""
import requests

def check_db_schema():
    """Check database schema for model_picks table"""
    base_url = "https://railway-engine-production.up.railway.app"
    
    print("CHECKING DATABASE SCHEMA FOR MODEL_PICKS")
    print("="*80)
    
    # Try to get table schema
    print("\n1. Check Model Picks Schema:")
    
    # Try to get a single pick to see what columns exist
    try:
        # Try to get any pick to see the error
        response = requests.get(f"{base_url}/api/sports/30/picks/player-props?limit=1", timeout=5)
        if response.status_code == 500:
            error_text = response.text
            print(f"   Error shows: {error_text[:200]}")
            
            # Extract SQL from error if present
            if "SELECT" in error_text and "model_picks" in error_text:
                print("\n   SQL Query from Error:")
                # Try to extract the SELECT statement
                import re
                sql_match = re.search(r'SELECT.*?FROM model_picks', error_text)
                if sql_match:
                    print(f"   {sql_match.group()}")
                    # Extract columns
                    columns = re.findall(r'model_picks\.(\w+)', error_text)
                    if columns:
                        print(f"   Columns referenced: {columns}")
    except Exception as e:
        print(f"   Error checking schema: {e}")
    
    print("\n" + "="*80)
    print("DIAGNOSIS:")
    print("- The error shows model_picks.closing_odds doesn't exist")
    print("- Need to either:")
    print("  1. Add the column to the database")
    print("  2. Or remove references from code")
    print("\nRECOMMENDATION:")
    print("- Add the column (quick fix)")
    print("- Then real picks will load")
    print("="*80)

if __name__ == "__main__":
    check_db_schema()
