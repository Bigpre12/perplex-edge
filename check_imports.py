#!/usr/bin/env python3
"""
Check for import errors in the backend
"""
import subprocess
import sys

def check_imports():
    """Check critical imports"""
    imports_to_check = [
        "from app.services.results_api import fetch_game_results",
        "from app.tasks.grade_picks import pick_grader",
        "from app.api.grading import router",
        "from app.api.admin import router",
        "from app.api.public import router",
    ]
    
    print("CHECKING CRITICAL IMPORTS")
    print("="*80)
    
    all_ok = True
    
    for import_stmt in imports_to_check:
        try:
            result = subprocess.run(
                [sys.executable, "-c", import_stmt],
                capture_output=True,
                text=True,
                cwd="c:\\Users\\preio\\perplex-edge\\backend"
            )
            
            if result.returncode == 0:
                print(f"OK {import_stmt}")
            else:
                print(f"FAIL {import_stmt}")
                print(f"  Error: {result.stderr}")
                all_ok = False
        except Exception as e:
            print(f"ERROR {import_stmt}: {e}")
            all_ok = False
    
    print("="*80)
    
    if all_ok:
        print("SUCCESS: All critical imports working")
    else:
        print("FAILURE: Some imports are failing")
    
    return all_ok

if __name__ == "__main__":
    check_imports()
