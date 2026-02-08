#!/usr/bin/env python3
"""
Check for any remaining frontend issues
"""
import os
import re
import json

def check_remaining_issues():
    """Check for remaining frontend issues"""
    print("CHECKING REMAINING FRONTEND ISSUES")
    print("="*80)
    
    frontend_dir = "c:\\Users\\preio\\perplex-edge\\frontend"
    src_dir = os.path.join(frontend_dir, "src")
    
    issues = []
    
    # 1. Check for any remaining hardcoded URLs
    print("\n1. Checking for hardcoded URLs...")
    hardcoded_urls = []
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding='utf-8') as f:
                        content = f.read()
                        # Check for any hardcoded URLs
                        urls = re.findall(r'https?://[^\s"\'`]+', content)
                        for url in urls:
                            if 'localhost' in url or '127.0.0.1' in url:
                                hardcoded_urls.append((filepath, url))
                except:
                    pass
    
    if hardcoded_urls:
        issues.append(f"Found {len(hardcoded_urls)} hardcoded URLs")
        print(f"   WARNING: Found {len(hardcoded_urls)} hardcoded URLs:")
        for filepath, url in hardcoded_urls:
            rel_path = os.path.relpath(filepath, frontend_dir)
            print(f"     - {rel_path}: {url}")
    else:
        print("   OK: No hardcoded URLs found")
    
    # 2. Check for unguarded console.log
    print("\n2. Checking for unguarded console.log...")
    unguarded_logs = []
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines, 1):
                            if 'console.log' in line:
                                # Check if it's guarded
                                if 'import.meta.env.DEV' not in line and not line.strip().startswith('//'):
                                    unguarded_logs.append((filepath, i, line.strip()))
                except:
                    pass
    
    if unguarded_logs:
        issues.append(f"Found {len(unguarded_logs)} unguarded console.log statements")
        print(f"   WARNING: Found {len(unguarded_logs)} unguarded console.log statements:")
        for filepath, line_num, line in unguarded_logs[:5]:
            rel_path = os.path.relpath(filepath, frontend_dir)
            print(f"     - {rel_path}:{line_num}: {line[:80]}")
        if len(unguarded_logs) > 5:
            print(f"     ... and {len(unguarded_logs) - 5} more")
    else:
        print("   OK: All console.log statements are guarded")
    
    # 3. Check package.json for production dependencies
    print("\n3. Checking package.json...")
    package_json = os.path.join(frontend_dir, "package.json")
    if os.path.exists(package_json):
        try:
            with open(package_json, "r") as f:
                data = json.load(f)
                
            # Check for missing production dependencies
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})
            
            critical_deps = ["react", "react-dom", "@clerk/clerk-react"]
            missing_deps = []
            for dep in critical_deps:
                if dep not in deps and dep not in dev_deps:
                    missing_deps.append(dep)
            
            if missing_deps:
                issues.append(f"Missing critical dependencies: {missing_deps}")
                print(f"   WARNING: Missing dependencies: {missing_deps}")
            else:
                print("   OK: All critical dependencies found")
                
        except:
            print("   ERROR: Could not parse package.json")
    
    # 4. Check for missing environment variables
    print("\n4. Checking environment variables...")
    env_files = [
        os.path.join(frontend_dir, ".env"),
        os.path.join(frontend_dir, ".env.production"),
    ]
    
    env_vars_found = []
    for env_file in env_files:
        if os.path.exists(env_file):
            try:
                with open(env_file, "r") as f:
                    content = f.read()
                    if "VITE_API_BASE_URL" in content:
                        env_vars_found.append(os.path.basename(env_file))
            except:
                pass
    
    if not env_vars_found:
        issues.append("No environment files with VITE_API_BASE_URL found")
        print("   WARNING: No environment files with VITE_API_BASE_URL")
    else:
        print(f"   OK: Found environment variables in: {', '.join(env_vars_found)}")
    
    # 5. Check Dockerfile configuration
    print("\n5. Checking Dockerfile...")
    dockerfile = os.path.join(frontend_dir, "Dockerfile")
    if os.path.exists(dockerfile):
        try:
            with open(dockerfile, "r") as f:
                content = f.read()
                
            if "nginx" in content.lower():
                print("   OK: Using nginx for production")
            else:
                issues.append("Dockerfile not configured for nginx")
                print("   WARNING: Dockerfile not using nginx")
                
            if "VITE_API_BASE_URL" in content:
                print("   OK: API URL configured in Dockerfile")
            else:
                issues.append("API URL not configured in Dockerfile")
                print("   WARNING: API URL not configured in Dockerfile")
                
        except:
            print("   ERROR: Could not read Dockerfile")
    
    # 6. Check for TypeScript errors
    print("\n6. Checking for TypeScript configuration...")
    tsconfig = os.path.join(frontend_dir, "tsconfig.json")
    if os.path.exists(tsconfig):
        print("   OK: TypeScript configuration found")
    else:
        issues.append("TypeScript configuration not found")
        print("   WARNING: TypeScript configuration not found")
    
    print("\n" + "="*80)
    
    if issues:
        print(f"FOUND {len(issues)} REMAINING ISSUES:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("SUCCESS: No remaining issues found!")
    
    print("="*80)
    
    return issues

if __name__ == "__main__":
    check_remaining_issues()
