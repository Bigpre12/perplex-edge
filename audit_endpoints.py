#!/usr/bin/env python3
"""
Audit all API endpoints for consistency
"""
import os
import re
from collections import defaultdict

def audit_endpoints():
    """Audit all API endpoints across files"""
    
    api_dir = "backend/app/api"
    endpoints = defaultdict(list)
    issues = []
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if not filename.endswith('.py'):
                continue
                
            filepath = os.path.join(root, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all route decorators
                route_pattern = r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
                matches = re.findall(route_pattern, content)
                
                for method, path in matches:
                    endpoints[filename].append((method, path))
                    
                    # Check for common issues
                    if path.startswith('/'):
                        if not path.startswith('/api/'):
                            issues.append(f"{filename}: Path '{path}' doesn't start with /api/")
                    else:
                        issues.append(f"{filename}: Path '{path}' doesn't start with /")
                    
                    # Check for trailing slashes inconsistency
                    if path != '/' and path.endswith('/'):
                        issues.append(f"{filename}: Path '{path}' has trailing slash")
                    
                    # Check for path parameters
                    if '{' in path and '}' in path:
                        params = re.findall(r'\{([^}]+)\}', path)
                        for param in params:
                            if not param.replace('_', '').isalnum():
                                issues.append(f"{filename}: Invalid path parameter '{param}' in '{path}'")
                    
            except Exception as e:
                issues.append(f"{filename}: Error reading file - {e}")
    
    # Print results
    print("=" * 80)
    print("API ENDPOINT AUDIT")
    print("=" * 80)
    
    print("\nENDPOINTS BY FILE:")
    for filename, paths in sorted(endpoints.items()):
        print(f"\n{filename}:")
        for method, path in sorted(paths):
            print(f"  {method.upper():6} {path}")
    
    if issues:
        print("\nISSUES FOUND:")
        for issue in sorted(issues):
            print(f"  {issue}")
    else:
        print("\nNo endpoint issues found!")
    
    # Check for duplicate endpoints
    all_paths = []
    for paths in endpoints.values():
        for method, path in paths:
            all_paths.append((method.upper(), path))
    
    duplicates = []
    seen = set()
    for item in all_paths:
        if item in seen:
            duplicates.append(item)
        seen.add(item)
    
    if duplicates:
        print("\nDUPLICATE ENDPOINTS:")
        for dup in duplicates:
            print(f"  {dup[0]} {dup[1]}")
    
    print("\n" + "=" * 80)
    print(f"TOTAL ENDPOINTS: {len(all_paths)}")
    print(f"FILES CHECKED: {len(endpoints)}")
    print(f"ISSUES FOUND: {len(issues)}")
    print("=" * 80)

if __name__ == "__main__":
    audit_endpoints()
