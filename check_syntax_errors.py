#!/usr/bin/env python3
"""
Check all API files for syntax errors
"""
import os
import ast

def check_syntax_errors():
    """Check all Python files for syntax errors"""
    api_dir = "backend/app/api"
    syntax_errors = []
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, api_dir)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Try to parse the file
                    ast.parse(content)
                except SyntaxError as e:
                    syntax_errors.append({
                        'file': rel_path,
                        'line': e.lineno,
                        'column': e.offset,
                        'error': str(e)
                    })
                except Exception as e:
                    syntax_errors.append({
                        'file': rel_path,
                        'error': f'Error reading file: {e}'
                    })
    
    return syntax_errors

def main():
    """Main check function"""
    print("CHECKING ALL API FILES FOR SYNTAX ERRORS")
    print("="*80)
    
    errors = check_syntax_errors()
    
    if errors:
        print(f"Found {len(errors)} syntax errors:")
        for error in errors:
            print(f"  {error['file']}:")
            if 'line' in error:
                print(f"    Line {error['line']}: {error['error']}")
            else:
                print(f"    {error['error']}")
    else:
        print("OK No syntax errors found")
    
    print("="*80)
    
    return len(errors)

if __name__ == "__main__":
    main()
