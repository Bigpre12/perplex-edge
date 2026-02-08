#!/usr/bin/env python3
"""
Simple diagnostic check for API files
"""
import os
import re

def check_syntax():
    """Check syntax errors"""
    api_dir = "backend/app/api"
    errors = []
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    compile(content, filepath, 'exec')
                except SyntaxError as e:
                    errors.append(f"{os.path.relpath(filepath, api_dir)}: Line {e.lineno} - {e}")
                except Exception as e:
                    errors.append(f"{os.path.relpath(filepath, api_dir)}: {e}")
    
    return errors

def check_imports():
    """Check for common import issues"""
    api_dir = "backend/app/api"
    issues = []
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for regex deprecation
                    if 'regex=' in content:
                        issues.append(f"{os.path.relpath(filepath, api_dir)}: Uses deprecated 'regex=' parameter")
                    
                    # Check for Query/Path issues
                    if 'Query(default=' in content and '{' in content:
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'Query(default=' in line and '{' in line:
                                issues.append(f"{os.path.relpath(filepath, api_dir)}:{i+1}: Possible Query/Path issue")
                                break
                except Exception as e:
                    issues.append(f"{os.path.relpath(filepath, api_dir)}: Error reading file - {e}")
    
    return issues

def check_endpoints():
    """Check endpoint patterns"""
    api_dir = "backend/app/api"
    endpoints = []
    issues = []
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find route decorators
                    route_pattern = r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
                    matches = re.findall(route_pattern, content)
                    
                    for method, path in matches:
                        endpoints.append((os.path.relpath(filepath, api_dir), method.upper(), path))
                        
                        # Check for issues
                        if not path.startswith('/'):
                            issues.append(f"{os.path.relpath(filepath, api_dir)}: Path '{path}' doesn't start with /")
                        if path.endswith('/') and path != '/':
                            issues.append(f"{os.path.relpath(filepath, api_dir)}: Path '{path}' has trailing slash")
                except Exception as e:
                    issues.append(f"{os.path.relpath(filepath, api_dir)}: Error parsing file - {e}")
    
    return endpoints, issues

def main():
    """Run simple diagnostic"""
    print("SIMPLE DIAGNOSTIC CHECK")
    print("="*80)
    
    # Check 1: Syntax
    print("\n1. SYNTAX CHECK")
    syntax_errors = check_syntax()
    if syntax_errors:
        print(f"   Found {len(syntax_errors)} syntax errors:")
        for err in syntax_errors[:5]:
            print(f"   {err}")
    else:
        print("   OK No syntax errors found")
    
    # Check 2: Imports
    print("\n2. IMPORT CHECK")
    import_issues = check_imports()
    if import_issues:
        print(f"   Found {len(import_issues)} import issues:")
        for issue in import_issues[:5]:
            print(f"   {issue}")
    else:
        print("   OK No import issues found")
    
    # Check 3: Endpoints
    print("\n3. ENDPOINT CHECK")
    endpoints, endpoint_issues = check_endpoints()
    print(f"   Total endpoints: {len(endpoints)}")
    if endpoint_issues:
        print(f"   Found {len(endpoint_issues)} endpoint issues:")
        for issue in endpoint_issues[:5]:
            print(f"   {issue}")
    else:
        print("   OK No endpoint issues found")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Syntax errors: {len(syntax_errors)}")
    print(f"Import issues: {len(import_issues)}")
    print(f"Endpoint issues: {len(endpoint_issues)}")
    print(f"Total issues: {len(syntax_errors) + len(import_issues) + len(endpoint_issues)}")

if __name__ == "__main__":
    main()
