#!/usr/bin/env python3
"""
Check frontend code for common issues
"""
import os
import re

def check_frontend_code():
    """Check frontend code for issues"""
    print("CHECKING FRONTEND CODE")
    print("="*80)
    
    frontend_dir = "c:\\Users\\preio\\perplex-edge\\frontend"
    src_dir = os.path.join(frontend_dir, "src")
    
    # 1. Check for API URL configuration
    print("\n1. Checking API URL configuration...")
    api_configs = [
        os.path.join(src_dir, "api.ts"),
        os.path.join(src_dir, "config.ts"),
        os.path.join(src_dir, "constants.ts"),
        os.path.join(src_dir, "env.ts"),
    ]
    
    api_found = False
    for config in api_configs:
        if os.path.exists(config):
            print(f"   Checking {config}...")
            try:
                with open(config, "r") as f:
                    content = f.read()
                    if "VITE_API_BASE_URL" in content:
                        print(f"   OK: API configuration found in {config}")
                        api_found = True
                        # Check if it's using environment variable
                        if "import.meta.env.VITE_API_BASE_URL" in content:
                            print("   OK: Using environment variable for API URL")
            except:
                print(f"   ERROR: Could not read {config}")
    
    if not api_found:
        print("   WARNING: No API configuration found")
    
    # 2. Check for hardcoded URLs
    print("\n2. Checking for hardcoded URLs...")
    hardcoded_issues = []
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding='utf-8') as f:
                        content = f.read()
                        # Check for hardcoded URLs
                        urls = re.findall(r'https?://[^\s"\'`]+', content)
                        for url in urls:
                            if 'localhost' in url or '127.0.0.1' in url:
                                hardcoded_issues.append((filepath, url))
                except:
                    pass
    
    if hardcoded_issues:
        print(f"   WARNING: Found {len(hardcoded_issues)} hardcoded URLs:")
        for filepath, url in hardcoded_issues[:5]:
            rel_path = os.path.relpath(filepath, frontend_dir)
            print(f"     - {rel_path}: {url}")
        if len(hardcoded_issues) > 5:
            print(f"     ... and {len(hardcoded_issues) - 5} more")
    else:
        print("   OK: No hardcoded localhost URLs found")
    
    # 3. Check for console.log statements
    print("\n3. Checking for console.log statements...")
    console_logs = []
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines, 1):
                            if 'console.log' in line and not line.strip().startswith('//'):
                                console_logs.append((filepath, i, line.strip()))
                except:
                    pass
    
    if console_logs:
        print(f"   WARNING: Found {len(console_logs)} console.log statements:")
        for filepath, line_num, line in console_logs[:5]:
            rel_path = os.path.relpath(filepath, frontend_dir)
            print(f"     - {rel_path}:{line_num}: {line[:80]}")
        if len(console_logs) > 5:
            print(f"     ... and {len(console_logs) - 5} more")
    else:
        print("   OK: No console.log statements found")
    
    # 4. Check for missing error handling
    print("\n4. Checking for error handling...")
    try_catch_blocks = 0
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding='utf-8') as f:
                        content = f.read()
                        # Count try/catch blocks
                        try_catch_blocks += content.count('try {')
                except:
                    pass
    
    print(f"   Found {try_catch_blocks} try/catch blocks")
    
    # 5. Check environment variables
    print("\n5. Checking environment variables...")
    env_files = [
        os.path.join(frontend_dir, ".env"),
        os.path.join(frontend_dir, ".env.production"),
        os.path.join(frontend_dir, ".env.example"),
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"   Found: {os.path.basename(env_file)}")
            try:
                with open(env_file, "r") as f:
                    content = f.read()
                    if "VITE_API_BASE_URL" in content:
                        print(f"     OK: Contains VITE_API_BASE_URL")
            except:
                print(f"     ERROR: Could not read {env_file}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_frontend_code()
