#!/usr/bin/env python3
"""
Run 10 separate diagnostic checks on API files
Each check focuses on different aspects
"""
import os
import re
import ast
import json
from collections import defaultdict

def check_1_syntax_errors():
    """Check 1: Syntax errors and parsing issues"""
    print("\n" + "="*80)
    print("CHECK 1: SYNTAX ERRORS AND PARSING ISSUES")
    print("="*80)
    
    api_dir = "backend/app/api"
    errors = []
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    ast.parse(content)
                except SyntaxError as e:
                    errors.append({
                        'file': os.path.relpath(filepath, api_dir),
                        'line': e.lineno,
                        'error': str(e)
                    })
                except Exception as e:
                    errors.append({
                        'file': os.path.relpath(filepath, api_dir),
                        'error': f'Parse error: {e}'
                    })
    
    if errors:
        print(f"Found {len(errors)} syntax errors:")
        for err in errors[:10]:
            print(f"  {err['file']}: Line {err.get('line', '?')} - {err['error']}")
    else:
        print("✓ No syntax errors found")
    
    return len(errors)

def check_2_import_consistency():
    """Check 2: Import statement consistency"""
    print("\n" + "="*80)
    print("CHECK 2: IMPORT STATEMENT CONSISTENCY")
    print("="*80)
    
    api_dir = "backend/app/api"
    issues = []
    imports_by_file = defaultdict(list)
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines, 1):
                        line = line.strip()
                        if line.startswith('from ') or line.startswith('import '):
                            imports_by_file[os.path.relpath(filepath, api_dir)].append((i, line))
                            
                            # Check for inconsistent import styles
                            if line.startswith('from ') and ' import ' in line:
                                if ',' in line and '(' not in line:  # Multi-import without parentheses
                                    issues.append({
                                        'file': os.path.relpath(filepath, api_dir),
                                        'line': i,
                                        'issue': 'Multi-import without parentheses',
                                        'code': line
                                    })
                except Exception as e:
                    issues.append({
                        'file': os.path.relpath(filepath, api_dir),
                        'error': f'Error reading file: {e}'
                    })
    
    print(f"Total files with imports: {len(imports_by_file)}")
    print(f"Import issues found: {len(issues)}")
    
    if issues:
        print("\nSample issues:")
        for issue in issues[:5]:
            print(f"  {issue['file']}:{issue['line']} - {issue['issue']}")
            print(f"    {issue['code']}")
    
    return len(issues)

def check_3_function_naming():
    """Check 3: Function and variable naming conventions"""
    print("\n" + "="*80)
    print("CHECK 3: FUNCTION AND VARIABLE NAMING CONVENTIONS")
    print("="*80)
    
    api_dir = "backend/app/api"
    issues = []
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Check function naming (should be snake_case)
                            if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                                issues.append({
                                    'file': os.path.relpath(filepath, api_dir),
                                    'line': node.lineno,
                                    'type': 'function',
                                    'name': node.name,
                                    'issue': 'Function name should be snake_case'
                                })
                        
                        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                            # Check variable naming (should be snake_case)
                            if isinstance(node.id, str) and not node.id.startswith('_'):
                                if not re.match(r'^[a-z_][a-z0-9_]*$', node.id):
                                    # Skip constants (ALL_CAPS) and class names (CamelCase)
                                    if not node.id.isupper() and not node.id[0].isupper():
                                        issues.append({
                                            'file': os.path.relpath(filepath, api_dir),
                                            'line': node.lineno,
                                            'type': 'variable',
                                            'name': node.id,
                                            'issue': 'Variable name should be snake_case'
                                        })
                except Exception as e:
                    issues.append({
                        'file': os.path.relpath(filepath, api_dir),
                        'error': f'Error parsing file: {e}'
                    })
    
    print(f"Naming issues found: {len(issues)}")
    
    if issues:
        print("\nSample issues:")
        for issue in issues[:5]:
            print(f"  {issue['file']}:{issue['line']} - {issue['type']} '{issue['name']}'")
            print(f"    {issue['issue']}")
    
    return len(issues)

def check_4_docstring_coverage():
    """Check 4: Docstring coverage"""
    print("\n" + "="*80)
    print("CHECK 4: DOCSTRING COVERAGE")
    print("="*80)
    
    api_dir = "backend/app/api"
    functions = 0
    with_docstrings = 0
    issues = []
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            functions += 1
                            if (node.body and 
                                isinstance(node.body[0], ast.Expr) and 
                                isinstance(node.body[0].value, ast.Constant) and 
                                isinstance(node.body[0].value.value, str)):
                                with_docstrings += 1
                            elif node.name.startswith('_'):
                                # Skip private functions
                                pass
                            else:
                                issues.append({
                                    'file': os.path.relpath(filepath, api_dir),
                                    'line': node.lineno,
                                    'function': node.name,
                                    'issue': 'Missing docstring'
                                })
                except Exception as e:
                    issues.append({
                        'file': os.path.relpath(filepath, api_dir),
                        'error': f'Error parsing file: {e}'
                    })
    
    coverage = (with_docstrings / functions * 100) if functions > 0 else 0
    print(f"Total functions: {functions}")
    print(f"Functions with docstrings: {with_docstrings}")
    print(f"Coverage: {coverage:.1f}%")
    print(f"Missing docstrings: {len([i for i in issues if 'function' in i])}")
    
    return len(issues)

def check_5_type_hints():
    """Check 5: Type hints coverage"""
    print("\n" + "="*80)
    print("CHECK 5: TYPE HINTS COVERAGE")
    print("="*80)
    
    api_dir = "backend/app/api"
    functions = 0
    with_type_hints = 0
    issues = []
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            functions += 1
                            has_return_type = node.returns is not None
                            has_arg_types = all(arg.annotation is not None for arg in node.args.args)
                            
                            if has_return_type or has_arg_types:
                                with_type_hints += 1
                            elif not node.name.startswith('_'):
                                issues.append({
                                    'file': os.path.relpath(filepath, api_dir),
                                    'line': node.lineno,
                                    'function': node.name,
                                    'issue': 'Missing type hints'
                                })
                except Exception as e:
                    issues.append({
                        'file': os.path.relpath(filepath, api_dir),
                        'error': f'Error parsing file: {e}'
                    })
    
    coverage = (with_type_hints / functions * 100) if functions > 0 else 0
    print(f"Total functions: {functions}")
    print(f"Functions with type hints: {with_type_hints}")
    print(f"Coverage: {coverage:.1f}%")
    print(f"Missing type hints: {len([i for i in issues if 'function' in i])}")
    
    return len(issues)

def check_6_error_handling():
    """Check 6: Error handling patterns"""
    print("\n" + "="*80)
    print("CHECK 6: ERROR HANDLING PATTERNS")
    print("="*80)
    
    api_dir = "backend/app/api"
    try_blocks = 0
    except_blocks = 0
    issues = []
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Try):
                            try_blocks += 1
                            
                            # Check if all exceptions are caught
                            if not node.handlers:
                                issues.append({
                                    'file': os.path.relpath(filepath, api_dir),
                                    'line': node.lineno,
                                    'issue': 'Try block without except handler'
                                })
                            else:
                                except_blocks += len(node.handlers)
                                
                                # Check for bare except
                                for handler in node.handlers:
                                    if handler.type is None:
                                        issues.append({
                                            'file': os.path.relpath(filepath, api_dir),
                                            'line': handler.lineno,
                                            'issue': 'Bare except clause'
                                        })
                except Exception as e:
                    issues.append({
                        'file': os.path.relpath(filepath, api_dir),
                        'error': f'Error parsing file: {e}'
                    })
    
    print(f"Try blocks: {try_blocks}")
    print(f"Except blocks: {except_blocks}")
    print(f"Error handling issues: {len(issues)}")
    
    if issues:
        print("\nSample issues:")
        for issue in issues[:5]:
            print(f"  {issue['file']}:{issue['line']} - {issue['issue']}")
    
    return len(issues)

def check_7_unused_imports():
    """Check 7: Unused imports"""
    print("\n" + "="*80)
    print("CHECK 7: UNUSED IMPORTS")
    print("="*80)
    
    api_dir = "backend/app/api"
    issues = []
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    
                    # Get all imports
                    imports = set()
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.add(alias.asname or alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            for alias in node.names:
                                if alias.name != '*':
                                    imports.add(alias.asname or alias.name)
                    
                    # Get all names used in the code
                    used_names = set()
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Name):
                            used_names.add(node.id)
                    
                    # Find unused imports
                    unused = imports - used_names
                    for imp in sorted(unused):
                        if not imp.startswith('_'):  # Skip underscore imports
                            issues.append({
                                'file': os.path.relpath(filepath, api_dir),
                                'issue': f'Unused import: {imp}'
                            })
                except Exception as e:
                    issues.append({
                        'file': os.path.relpath(filepath, api_dir),
                        'error': f'Error parsing file: {e}'
                    })
    
    print(f"Unused imports found: {len(issues)}")
    
    if issues:
        print("\nSample unused imports:")
        for issue in issues[:10]:
            print(f"  {issue['file']} - {issue['issue']}")
    
    return len(issues)

def check_8_endpoint_consistency():
    """Check 8: Endpoint naming and HTTP method consistency"""
    print("\n" + "="*80)
    print("CHECK 8: ENDPOINT CONSISTENCY")
    print("="*80)
    
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
                        endpoints.append({
                            'file': os.path.relpath(filepath, api_dir),
                            'method': method.upper(),
                            'path': path
                        })
                        
                        # Check for common issues
                        if path.endswith('/'):
                            issues.append({
                                'file': os.path.relpath(filepath, api_dir),
                                'issue': f'Trailing slash in endpoint: {method} {path}'
                            })
                        
                        if '{' in path and '}' in path:
                            params = re.findall(r'\{([^}]+)\}', path)
                            for param in params:
                                if not re.match(r'^[a-z_][a-z0-9_]*$', param):
                                    issues.append({
                                        'file': os.path.relpath(filepath, api_dir),
                                        'issue': f'Invalid path parameter: {param} in {path}'
                                    })
                except Exception as e:
                    issues.append({
                        'file': os.path.relpath(filepath, api_dir),
                        'error': f'Error parsing file: {e}'
                    })
    
    print(f"Total endpoints: {len(endpoints)}")
    print(f"Endpoint issues: {len(issues)}")
    
    # Check for duplicate endpoints
    endpoint_counts = defaultdict(int)
    for ep in endpoints:
        endpoint_counts[(ep['method'], ep['path'])] += 1
    
    duplicates = [(ep, count) for ep, count in endpoint_counts.items() if count > 1]
    if duplicates:
        print(f"\nDuplicate endpoints: {len(duplicates)}")
        for (method, path), count in duplicates[:5]:
            print(f"  {method} {path} - {count} times")
    
    return len(issues)

def check_9_security_patterns():
    """Check 9: Security patterns and best practices"""
    print("\n" + "="*80)
    print("CHECK 9: SECURITY PATTERNS")
    print("="*80)
    
    api_dir = "backend/app/api"
    issues = []
    
    security_patterns = {
        'SQL injection': r'execute\s*\(\s*["\'].*\%.*["\']',
        'Hardcoded secrets': r'(password|secret|key|token)\s*=\s*["\'][^"\']{8,}["\']',
        'Debug prints': r'print\s*\(',
        'Eval usage': r'eval\s*\(',
        'Exec usage': r'exec\s*\(',
    }
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines, 1):
                        for pattern_name, pattern in security_patterns.items():
                            if re.search(pattern, line, re.IGNORECASE):
                                issues.append({
                                    'file': os.path.relpath(filepath, api_dir),
                                    'line': i,
                                    'issue': f'{pattern_name} detected',
                                    'code': line.strip()[:80]
                                })
                except Exception as e:
                    issues.append({
                        'file': os.path.relpath(filepath, api_dir),
                        'error': f'Error reading file: {e}'
                    })
    
    print(f"Security issues found: {len(issues)}")
    
    if issues:
        print("\nSample issues:")
        for issue in issues[:5]:
            print(f"  {issue['file']}:{issue['line']} - {issue['issue']}")
            print(f"    {issue['code']}")
    
    return len(issues)

def check_10_performance_patterns():
    """Check 10: Performance patterns and optimizations"""
    print("\n" + "="*80)
    print("CHECK 10: PERFORMANCE PATTERNS")
    print("="*80)
    
    api_dir = "backend/app/api"
    issues = []
    
    performance_patterns = {
        'N+1 query risk': r'\.get\s*\([^)]*\)\s*\.get',
        'Missing async/await': r'async def.*(?!\s*await)',
        'Large list comprehension': r'\[.*for.*in.*if.*for.*in',
        'Inefficient string concatenation': r'\w+\s*\+\s*\w+\s*\+\s*\w+',
        'Missing pagination': r'limit\s*=\s*None',
    }
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines, 1):
                        for pattern_name, pattern in performance_patterns.items():
                            if re.search(pattern, line, re.IGNORECASE):
                                issues.append({
                                    'file': os.path.relpath(filepath, api_dir),
                                    'line': i,
                                    'issue': f'{pattern_name} possible',
                                    'code': line.strip()[:80]
                                })
                except Exception as e:
                    issues.append({
                        'file': os.path.relpath(filepath, api_dir),
                        'error': f'Error reading file: {e}'
                    })
    
    print(f"Performance issues found: {len(issues)}")
    
    if issues:
        print("\nSample issues:")
        for issue in issues[:5]:
            print(f"  {issue['file']}:{issue['line']} - {issue['issue']}")
            print(f"    {issue['code']}")
    
    return len(issues)

def main():
    """Run all 10 diagnostic checks"""
    print("RUNNING 10 SEPARATE DIAGNOSTIC CHECKS")
    print("="*80)
    
    results = {}
    
    # Run all checks
    checks = [
        check_1_syntax_errors,
        check_2_import_consistency,
        check_3_function_naming,
        check_4_docstring_coverage,
        check_5_type_hints,
        check_6_error_handling,
        check_7_unused_imports,
        check_8_endpoint_consistency,
        check_9_security_patterns,
        check_10_performance_patterns,
    ]
    
    for i, check in enumerate(checks, 1):
        results[f'check_{i}'] = check()
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY - ALL 10 DIAGNOSTIC CHECKS")
    print("="*80)
    
    total_issues = sum(results.values())
    print(f"Total issues found: {total_issues}")
    
    print("\nIssues by check:")
    for check_name, count in results.items():
        check_num = check_name.split('_')[1]
        check_titles = {
            '1': 'Syntax Errors',
            '2': 'Import Consistency',
            '3': 'Naming Conventions',
            '4': 'Docstring Coverage',
            '5': 'Type Hints',
            '6': 'Error Handling',
            '7': 'Unused Imports',
            '8': 'Endpoint Consistency',
            '9': 'Security Patterns',
            '10': 'Performance Patterns'
        }
        title = check_titles.get(check_num, f'Check {check_num}')
        print(f"  {title}: {count} issues")
    
    print("\n" + "="*80)
    print("DIAGNOSTIC COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
