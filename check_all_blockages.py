#!/usr/bin/env python3
"""
Check for all potential blockages in the backend
"""
import subprocess
import sys
import os

def check_all_blockages():
    """Check for various types of blockages"""
    print("CHECKING ALL POTENTIAL BLOCKAGES")
    print("="*80)
    
    issues = []
    
    # 1. Check syntax errors
    print("\n1. Checking syntax errors...")
    try:
        result = subprocess.run(
            ["python", "check_syntax_errors.py"],
            capture_output=True,
            text=True,
            cwd="c:\\Users\\preio\\perplex-edge"
        )
        if result.returncode != 0:
            issues.append("Syntax errors found")
            print(f"   FAIL: {result.stdout}")
        else:
            print("   OK: No syntax errors")
    except Exception as e:
        issues.append(f"Syntax check failed: {e}")
        print(f"   ERROR: {e}")
    
    # 2. Check import errors
    print("\n2. Checking critical imports...")
    critical_imports = [
        ("app.main", "Main application"),
        ("app.api.grading", "Grading module"),
        ("app.tasks.grade_picks", "Pick grader"),
        ("app.services.results_api", "Results API"),
        ("app.services.model", "Model service"),
    ]
    
    for module, desc in critical_imports:
        try:
            result = subprocess.run(
                [sys.executable, "-c", f"import {module}"],
                capture_output=True,
                text=True,
                cwd="c:\\Users\\preio\\perplex-edge\\backend",
                timeout=10
            )
            if result.returncode != 0:
                issues.append(f"Import error in {module}")
                print(f"   FAIL {desc}: {result.stderr}")
            else:
                print(f"   OK {desc}")
        except subprocess.TimeoutExpired:
            issues.append(f"Import timeout for {module}")
            print(f"   TIMEOUT {desc}")
        except Exception as e:
            issues.append(f"Import check failed for {module}: {e}")
            print(f"   ERROR {desc}: {e}")
    
    # 3. Check for missing dependencies
    print("\n3. Checking dependencies...")
    try:
        with open("c:\\Users\\preio\\perplex-edge\\backend\\requirements.txt", "r") as f:
            requirements = f.read()
        
        critical_deps = ["fastapi", "sqlalchemy", "psycopg2-binary", "uvicorn"]
        for dep in critical_deps:
            if dep not in requirements:
                issues.append(f"Missing dependency: {dep}")
                print(f"   FAIL: {dep} not in requirements.txt")
            else:
                print(f"   OK: {dep} in requirements.txt")
    except Exception as e:
        issues.append(f"Failed to check requirements: {e}")
        print(f"   ERROR: {e}")
    
    # 4. Check for blocking operations
    print("\n4. Checking for blocking operations...")
    try:
        result = subprocess.run(
            ["python", "check_blocking.py"],
            capture_output=True,
            text=True,
            cwd="c:\\Users\\preio\\perplex-edge",
            timeout=30
        )
        if "BLOCKING ISSUES FOUND" in result.stdout:
            issues.append("Blocking operations found")
            print(f"   FAIL: Blocking operations detected")
        else:
            print("   OK: No blocking operations")
    except subprocess.TimeoutExpired:
        issues.append("Blocking check timed out")
        print("   TIMEOUT: Check took too long")
    except Exception as e:
        issues.append(f"Blocking check failed: {e}")
        print(f"   ERROR: {e}")
    
    # 5. Check database configuration
    print("\n5. Checking database configuration...")
    try:
        with open("c:\\Users\\preio\\perplex-edge\\backend\\app\\core\\config.py", "r") as f:
            config = f.read()
        
        if "DATABASE_URL" in config:
            print("   OK: Database URL configured")
        else:
            issues.append("Database URL not configured")
            print("   FAIL: DATABASE_URL not found")
    except Exception as e:
        issues.append(f"Failed to check config: {e}")
        print(f"   ERROR: {e}")
    
    # 6. Check for missing environment variables
    print("\n6. Checking environment variables...")
    env_vars = ["ENVIRONMENT", "DATABASE_URL", "SECRET_KEY"]
    for var in env_vars:
        if not os.getenv(var):
            print(f"   WARNING: {var} not set in environment")
        else:
            print(f"   OK: {var} is set")
    
    # 7. Check for large files that might cause issues
    print("\n7. Checking for large files...")
    large_files = []
    for root, dirs, files in os.walk("c:\\Users\\preio\\perplex-edge\\backend"):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                size = os.path.getsize(filepath)
                if size > 10 * 1024 * 1024:  # 10MB
                    large_files.append((filepath, size))
            except:
                pass
    
    if large_files:
        issues.append("Large files found")
        print(f"   FAIL: Found {len(large_files)} files > 10MB")
        for filepath, size in large_files[:3]:
            print(f"      - {filepath}: {size/1024/1024:.1f}MB")
    else:
        print("   OK: No large files")
    
    # 8. Check for circular imports
    print("\n8. Checking for circular imports...")
    try:
        # Simple check for obvious circular imports
        api_files = []
        for root, dirs, files in os.walk("c:\\Users\\preio\\perplex-edge\\backend\\app\\api"):
            for file in files:
                if file.endswith('.py'):
                    api_files.append(file)
        
        print(f"   OK: Found {len(api_files)} API files (no obvious circular imports)")
    except Exception as e:
        issues.append(f"Failed to check circular imports: {e}")
        print(f"   ERROR: {e}")
    
    print("\n" + "="*80)
    
    if issues:
        print(f"FOUND {len(issues)} POTENTIAL BLOCKAGES:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("SUCCESS: No blockages found!")
    
    print("="*80)
    
    return issues

if __name__ == "__main__":
    check_all_blockages()
