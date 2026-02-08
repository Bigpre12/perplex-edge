#!/usr/bin/env python3
"""
Identify the most critical data blocking issues
"""
import os
import re

def find_critical_blocking_issues():
    """Find the most critical issues that could block data"""
    api_dir = "backend/app/api"
    critical_issues = []
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, api_dir)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines):
                        # 1. Synchronous operations in async functions (CRITICAL)
                        if 'async def' in line:
                            # Check next few lines for sync operations
                            for j in range(i + 1, min(i + 20, len(lines))):
                                next_line = lines[j]
                                if 'time.sleep(' in next_line and 'await' not in next_line:
                                    critical_issues.append({
                                        'severity': 'CRITICAL',
                                        'type': 'sync_sleep_in_async',
                                        'file': rel_path,
                                        'line': j + 1,
                                        'issue': 'Synchronous sleep blocking async function',
                                        'code': next_line.strip(),
                                        'impact': 'Blocks entire event loop'
                                    })
                                elif 'requests.' in next_line and 'await' not in next_line:
                                    critical_issues.append({
                                        'severity': 'CRITICAL',
                                        'type': 'sync_http_in_async',
                                        'file': rel_path,
                                        'line': j + 1,
                                        'issue': 'Synchronous HTTP request in async function',
                                        'code': next_line.strip(),
                                        'impact': 'Blocks entire event loop'
                                    })
                        
                        # 2. Large queries without limits (HIGH)
                        if '.all()' in line and 'limit' not in line.lower():
                            # Check if it's a database query
                            if any(x in line for x in ['result.', 'execute(', 'query']):
                                critical_issues.append({
                                    'severity': 'HIGH',
                                    'type': 'unlimited_query',
                                    'file': rel_path,
                                    'line': i + 1,
                                    'issue': 'Query without limit could return large result set',
                                    'code': line.strip(),
                                    'impact': 'Memory exhaustion, slow response'
                                })
                        
                        # 3. Missing timeouts on external calls (HIGH)
                        if 'httpx' in line.lower() or 'requests' in line.lower():
                            if '.get(' in line or '.post(' in line:
                                if 'timeout' not in line.lower():
                                    critical_issues.append({
                                        'severity': 'HIGH',
                                        'type': 'no_http_timeout',
                                        'file': rel_path,
                                        'line': i + 1,
                                        'issue': 'HTTP request without timeout',
                                        'code': line.strip(),
                                        'impact': 'Request could hang indefinitely'
                                    })
                        
                        # 4. Database operations without timeout (MEDIUM)
                        if 'execute(' in line and 'timeout' not in line.lower():
                            critical_issues.append({
                                'severity': 'MEDIUM',
                                'type': 'no_db_timeout',
                                'file': rel_path,
                                'line': i + 1,
                                'issue': 'Database operation without explicit timeout',
                                'code': line.strip(),
                                'impact': 'Query could hang, blocking response'
                            })
                        
                        # 5. N+1 query patterns (MEDIUM)
                        if 'for ' in line and 'in ' in line:
                            # Look for queries in the next few lines
                            for j in range(i + 1, min(i + 10, len(lines))):
                                if any(x in lines[j] for x in ['execute(', 'query(', 'get(']):
                                    critical_issues.append({
                                        'severity': 'MEDIUM',
                                        'type': 'n_plus_1_query',
                                        'file': rel_path,
                                        'line': j + 1,
                                        'issue': 'Possible N+1 query pattern - query inside loop',
                                        'code': lines[j].strip(),
                                        'impact': 'Multiple database calls, slow response'
                                    })
                                    break
                
                except Exception as e:
                    critical_issues.append({
                        'severity': 'ERROR',
                        'type': 'file_error',
                        'file': rel_path,
                        'line': 0,
                        'issue': f'Error reading file: {e}',
                        'code': '',
                        'impact': 'Could not analyze file'
                    })
    
    return critical_issues

def main():
    """Main analysis"""
    print("IDENTIFYING CRITICAL DATA BLOCKING ISSUES")
    print("="*80)
    
    issues = find_critical_blocking_issues()
    
    # Group by severity
    by_severity = {}
    for issue in issues:
        severity = issue['severity']
        if severity not in by_severity:
            by_severity[severity] = []
        by_severity[severity].append(issue)
    
    # Print by severity
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'ERROR']:
        if severity in by_severity:
            print(f"\n{severity} ISSUES ({len(by_severity[severity])}):")
            print("-" * 40)
            for issue in by_severity[severity][:5]:
                print(f"  {issue['file']}:{issue['line']}")
                print(f"    Issue: {issue['issue']}")
                print(f"    Impact: {issue['impact']}")
                if issue['code']:
                    print(f"    Code: {issue['code']}")
                print()
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total issues: {len(issues)}")
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'ERROR']:
        count = len(by_severity.get(severity, []))
        if count > 0:
            print(f"  {severity}: {count}")
    
    # Top problematic files
    file_counts = {}
    for issue in issues:
        file_counts[issue['file']] = file_counts.get(issue['file'], 0) + 1
    
    print("\nTop 5 most problematic files:")
    for filename, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {filename}: {count} issues")
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    if 'CRITICAL' in by_severity:
        print("\n1. FIX CRITICAL ISSUES FIRST:")
        print("   - Replace time.sleep() with asyncio.sleep() in async functions")
        print("   - Use httpx.AsyncClient instead of requests in async functions")
        print("   - Add 'await' before async operations")
    
    if 'HIGH' in by_severity:
        print("\n2. FIX HIGH PRIORITY ISSUES:")
        print("   - Add .limit() to all queries")
        print("   - Add timeout parameter to all HTTP requests")
        print("   - Consider pagination for large result sets")
    
    if 'MEDIUM' in by_severity:
        print("\n3. FIX MEDIUM PRIORITY ISSUES:")
        print("   - Optimize N+1 queries with joins or bulk operations")
        print("   - Add query timeouts")
        print("   - Implement caching for frequently accessed data")
    
    print("="*80)

if __name__ == "__main__":
    main()
