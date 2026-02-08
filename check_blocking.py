#!/usr/bin/env python3
"""
Check what might be blocking data/requests in the API
"""
import os
import re
import ast
from collections import defaultdict

def check_blocking_patterns():
    """Check for patterns that might block data"""
    api_dir = "backend/app/api"
    blocking_issues = []
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, api_dir)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        stripped = line.strip()
                        
                        # Check for synchronous database calls in async functions
                        if 'async def' in line:
                            # Look ahead in the function for sync calls
                            j = i
                            indent_level = len(line) - len(line.lstrip())
                            while j < len(lines) and j < i + 50:  # Check next 50 lines
                                next_line = lines[j]
                                next_indent = len(next_line) - len(next_line.lstrip())
                                
                                if next_indent <= indent_level and next_line.strip():
                                    break  # End of function
                                
                                # Check for sync patterns
                                if re.search(r'\.execute\(', next_line) and 'await' not in next_line:
                                    blocking_issues.append({
                                        'type': 'sync_db_call',
                                        'file': rel_path,
                                        'line': j + 1,
                                        'issue': 'Synchronous database call in async function',
                                        'code': next_line.strip()
                                    })
                                
                                # Check for time.sleep
                                if 'time.sleep(' in next_line and 'await' not in next_line:
                                    blocking_issues.append({
                                        'type': 'sync_sleep',
                                        'file': rel_path,
                                        'line': j + 1,
                                        'issue': 'Synchronous sleep in async function',
                                        'code': next_line.strip()
                                    })
                                
                                # Check for requests.get without await
                                if 'requests.get(' in next_line and 'await' not in next_line:
                                    blocking_issues.append({
                                        'type': 'sync_http',
                                        'file': rel_path,
                                        'line': j + 1,
                                        'issue': 'Synchronous HTTP request in async function',
                                        'code': next_line.strip()
                                    })
                                
                                j += 1
                        
                        # Check for missing await on async calls
                        if 'await' not in line and any(x in line for x in ['.execute(', '.fetchall()', '.fetchone()', '.get(', '.post(']):
                            if not line.strip().startswith('#') and not 'def ' in line:
                                # Check if this might be an async call without await
                                if any(x in line for x in ['session.', 'conn.', 'client.']):
                                    blocking_issues.append({
                                        'type': 'missing_await',
                                        'file': rel_path,
                                        'line': i,
                                        'issue': 'Possible missing await on async call',
                                        'code': line.strip()
                                    })
                        
                        # Check for blocking operations
                        if any(x in line for x in ['os.system(', 'subprocess.call(', 'subprocess.run(']):
                            blocking_issues.append({
                                'type': 'blocking_subprocess',
                                'file': rel_path,
                                'line': i,
                                'issue': 'Blocking subprocess call',
                                'code': line.strip()
                            })
                        
                        # Check for large loops without async
                        if 'for ' in line and 'range(' in line and 'async' not in line:
                            # Check if loop body has database operations
                            if i + 1 < len(lines):
                                next_line = lines[i]
                                if any(x in next_line for x in ['.execute(', '.fetchall(', '.query']):
                                    blocking_issues.append({
                                        'type': 'sync_loop',
                                        'file': rel_path,
                                        'line': i,
                                        'issue': 'Synchronous loop with database operations',
                                        'code': line.strip()
                                    })
                        
                        # Check for cache issues
                        if 'cache' in line.lower():
                            if 'get(' in line and 'await' not in line:
                                blocking_issues.append({
                                    'type': 'sync_cache',
                                    'file': rel_path,
                                    'line': i,
                                    'issue': 'Synchronous cache access in async context',
                                    'code': line.strip()
                                })
                        
                        # Check for session issues
                        if 'session' in line.lower():
                            if '.close()' in line and 'await' not in line:
                                blocking_issues.append({
                                    'type': 'sync_session',
                                    'file': rel_path,
                                    'line': i,
                                    'issue': 'Synchronous session close',
                                    'code': line.strip()
                                })
                
                except Exception as e:
                    blocking_issues.append({
                        'type': 'error',
                        'file': rel_path,
                        'line': 0,
                        'issue': f'Error reading file: {e}',
                        'code': ''
                    })
    
    return blocking_issues

def check_database_patterns():
    """Check for database patterns that might block"""
    api_dir = "backend/app/api"
    db_issues = []
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, api_dir)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for N+1 query patterns
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'for ' in line and 'in ' in line:
                            # Look for database queries inside loops
                            j = i + 1
                            while j < len(lines) and j < i + 10:
                                if any(x in lines[j] for x in ['.execute(', '.query(', '.get(']):
                                    db_issues.append({
                                        'type': 'n_plus_1',
                                        'file': rel_path,
                                        'line': j + 1,
                                        'issue': 'Possible N+1 query pattern',
                                        'code': lines[j].strip()
                                    })
                                    break
                                j += 1
                        
                        # Check for missing connection close
                        if 'with engine.connect()' in line:
                            db_issues.append({
                                'type': 'connection_leak',
                                'file': rel_path,
                                'line': i + 1,
                                'issue': 'Manual connection management - possible leak',
                                'code': line.strip()
                            })
                        
                        # Check for large result sets
                        if 'limit' not in line.lower() and '.all()' in line:
                            db_issues.append({
                                'type': 'large_result',
                                'file': rel_path,
                                'line': i + 1,
                                'issue': 'Query without limit - possible large result set',
                                'code': line.strip()
                            })
                
                except Exception as e:
                    db_issues.append({
                        'type': 'error',
                        'file': rel_path,
                        'line': 0,
                        'issue': f'Error reading file: {e}',
                        'code': ''
                    })
    
    return db_issues

def check_timeout_settings():
    """Check for timeout settings"""
    api_dir = "backend/app/api"
    timeout_issues = []
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, api_dir)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        # Check for HTTP requests without timeout
                        if 'httpx' in line.lower() or 'requests' in line.lower():
                            if '.get(' in line or '.post(' in line:
                                if 'timeout' not in line.lower():
                                    timeout_issues.append({
                                        'type': 'no_timeout',
                                        'file': rel_path,
                                        'line': i + 1,
                                        'issue': 'HTTP request without timeout',
                                        'code': line.strip()
                                    })
                        
                        # Check for database operations without timeout
                        if 'execute(' in line and 'timeout' not in line.lower():
                            timeout_issues.append({
                                'type': 'no_db_timeout',
                                'file': rel_path,
                                'line': i + 1,
                                'issue': 'Database operation without timeout',
                                'code': line.strip()
                            })
                
                except Exception as e:
                    timeout_issues.append({
                        'type': 'error',
                        'file': rel_path,
                        'line': 0,
                        'issue': f'Error reading file: {e}',
                        'code': ''
                    })
    
    return timeout_issues

def main():
    """Main check function"""
    print("CHECKING FOR DATA BLOCKING ISSUES")
    print("="*80)
    
    # Check 1: Blocking patterns
    print("\n1. BLOCKING PATTERNS")
    blocking_issues = check_blocking_patterns()
    if blocking_issues:
        print(f"   Found {len(blocking_issues)} blocking issues:")
        for issue in blocking_issues[:10]:
            print(f"   {issue['file']}:{issue['line']} - {issue['issue']}")
            print(f"     {issue['code']}")
    else:
        print("   OK No blocking patterns found")
    
    # Check 2: Database patterns
    print("\n2. DATABASE PATTERNS")
    db_issues = check_database_patterns()
    if db_issues:
        print(f"   Found {len(db_issues)} database issues:")
        for issue in db_issues[:10]:
            print(f"   {issue['file']}:{issue['line']} - {issue['issue']}")
            print(f"     {issue['code']}")
    else:
        print("   OK No database issues found")
    
    # Check 3: Timeout settings
    print("\n3. TIMEOUT SETTINGS")
    timeout_issues = check_timeout_settings()
    if timeout_issues:
        print(f"   Found {len(timeout_issues)} timeout issues:")
        for issue in timeout_issues[:10]:
            print(f"   {issue['file']}:{issue['line']} - {issue['issue']}")
            print(f"     {issue['code']}")
    else:
        print("   OK All requests have timeouts")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    # Group by type
    all_issues = blocking_issues + db_issues + timeout_issues
    by_type = defaultdict(int)
    for issue in all_issues:
        by_type[issue['type']] += 1
    
    print(f"Total issues: {len(all_issues)}")
    print(f"Issues by type:")
    for issue_type, count in sorted(by_type.items()):
        print(f"  {issue_type}: {count}")
    
    # Most problematic files
    file_counts = defaultdict(int)
    for issue in all_issues:
        file_counts[issue['file']] += 1
    
    if file_counts:
        print(f"\nMost problematic files:")
        for filename, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {filename}: {count} issues")
    
    print("\n" + "="*80)
    print("BLOCKING ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
