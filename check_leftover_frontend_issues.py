#!/usr/bin/env python3
"""
Check for any remaining frontend issues
"""
import os
import re

def check_remaining_frontend_issues():
    """Check for any remaining frontend issues"""
    print("CHECKING REMAINING FRONTEND ISSUES")
    print("="*80)
    
    frontend_dir = "c:\\Users\\preio\\perplex-edge\\frontend"
    src_dir = os.path.join(frontend_dir, "src")
    
    issues = []
    
    # 1. Check for any remaining console.log statements
    print("\n1. Checking for console.log statements...")
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
                                # Check if it's properly guarded
                                if 'import.meta.env.DEV' not in line:
                                    # Check if it's in a conditional block
                                    context = '\n'.join(lines[max(0, i-3):i+2])
                                    if 'import.meta.env.DEV' not in context:
                                        console_logs.append((filepath, i, line.strip()))
                except:
                    pass
    
    if console_logs:
        issues.append(f"Found {len(console_logs)} unguarded console.log statements")
        print(f"   WARNING: Found {len(console_logs)} unguarded console.log statements:")
        for filepath, line_num, line in console_logs[:5]:
            rel_path = os.path.relpath(filepath, frontend_dir)
            print(f"     - {rel_path}:{line_num}: {line[:80]}")
        if len(console_logs) > 5:
            print(f"     ... and {len(console_logs) - 5} more")
    else:
        print("   OK: All console.log statements are properly guarded")
    
    # 2. Check for TODO or FIXME comments
    print("\n2. Checking for TODO/FIXME comments...")
    todos = []
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines, 1):
                            if 'TODO:' in line or 'FIXME:' in line or 'XXX:' in line:
                                todos.append((filepath, i, line.strip()))
                except:
                    pass
    
    if todos:
        issues.append(f"Found {len(todos)} TODO/FIXME comments")
        print(f"   INFO: Found {len(todos)} TODO/FIXME comments:")
        for filepath, line_num, line in todos[:5]:
            rel_path = os.path.relpath(filepath, frontend_dir)
            print(f"     - {rel_path}:{line_num}: {line[:80]}")
        if len(todos) > 5:
            print(f"     ... and {len(todos) - 5} more")
    else:
        print("   OK: No TODO/FIXME comments found")
    
    # 3. Check for potential performance issues
    print("\n3. Checking for potential performance issues...")
    perf_issues = []
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding='utf-8') as f:
                        content = f.read()
                        
                    # Check for potential issues
                    if 'useEffect(() => {' in content and 'console.log' in content:
                        # Check if useEffect has console.log without proper dependencies
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'useEffect(() => {' in line:
                                # Look ahead for console.log
                                for j in range(i+1, min(i+10, len(lines))):
                                    if 'console.log' in lines[j] and 'import.meta.env.DEV' not in lines[j]:
                                        perf_issues.append((filepath, i+1, "useEffect with unguarded console.log"))
                                        break
                except:
                    pass
    
    if perf_issues:
        issues.append(f"Found {len(perf_issues)} potential performance issues")
        print(f"   WARNING: Found {len(perf_issues)} potential performance issues:")
        for filepath, line_num, issue in perf_issues[:3]:
            rel_path = os.path.relpath(filepath, frontend_dir)
            print(f"     - {rel_path}:{line_num}: {issue}")
        if len(perf_issues) > 3:
            print(f"     ... and {len(perf_issues) - 3} more")
    else:
        print("   OK: No obvious performance issues found")
    
    # 4. Check for missing error boundaries
    print("\n4. Checking for error boundaries...")
    error_boundaries = 0
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.tsx', '.jsx')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding='utf-8') as f:
                        content = f.read()
                        if 'componentDidCatch' in content or 'ErrorBoundary' in content:
                            error_boundaries += 1
                except:
                    pass
    
    print(f"   Found {error_boundaries} error boundary components")
    
    # 5. Check for unused imports
    print("\n5. Checking for unused imports...")
    unused_imports = []
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.ts', '.tsx')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding='utf-8') as f:
                        content = f.read()
                    
                    # Simple check for imports that might be unused
                    lines = content.split('\n')
                    for line in lines:
                        if 'import' in line and 'React' in line and file.endswith('.tsx'):
                            # Check if React is actually used
                            if 'React.' not in content and '<React.' not in content:
                                unused_imports.append((filepath, "React import might be unused"))
                except:
                    pass
    
    if unused_imports:
        issues.append(f"Found {len(unused_imports)} potentially unused imports")
        print(f"   INFO: Found {len(unused_imports)} potentially unused imports:")
        for filepath, issue in unused_imports[:3]:
            rel_path = os.path.relpath(filepath, frontend_dir)
            print(f"     - {rel_path}: {issue}")
        if len(unused_imports) > 3:
            print(f"     ... and {len(unused_imports) - 3} more")
    else:
        print("   OK: No obviously unused imports found")
    
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
    check_remaining_frontend_issues()
