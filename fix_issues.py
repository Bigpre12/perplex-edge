#!/usr/bin/env python3
"""
Fix misspellings, unneeded words, and code blocks
"""
import os
import re

def fix_file(filepath):
    """Fix issues in a single file"""
    fixed = False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix misspellings (but not common words like tomorrow, weather, yesterday)
        misspellings_to_fix = {
            'paramater': 'parameter',
            'paramaters': 'parameters',
            'endpont': 'endpoint',
            'endponts': 'endpoints',
            'responce': 'response',
            'requst': 'request',
            'requsts': 'requests',
            'authenication': 'authentication',
            'authorzation': 'authorization',
            'conection': 'connection',
            'databse': 'database',
            'databses': 'databases',
            'excecute': 'execute',
            'funtion': 'function',
            'funtions': 'functions',
            'messge': 'message',
            'messges': 'messages',
            'proccess': 'process',
            'sesion': 'session',
            'sesions': 'sessions',
            'validaton': 'validation',
            'validatons': 'validations',
        }
        
        for wrong, correct in misspellings_to_fix.items():
            pattern = re.compile(rf'\b{re.escape(wrong)}\b', re.IGNORECASE)
            content = pattern.sub(correct, content)
        
        # Remove unneeded words
        unneeded_words = ['just ', 'Just ', 'simply ', 'Simply ', 'basically ', 'Basically ']
        for word in unneeded_words:
            content = re.sub(rf'\b{re.escape(word.strip())}\b', '', content)
        
        # Fix long lines by breaking them
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if len(line) > 120 and not line.strip().startswith('#') and not line.strip().startswith('"'):
                # Break long lines at logical points
                if ', ' in line and '=' in line:
                    # Break after comma in assignments
                    parts = line.split(', ')
                    if len(parts) > 1:
                        indent = len(line) - len(line.lstrip())
                        new_line = parts[0]
                        for part in parts[1:]:
                            new_line += ',\n' + ' ' * (indent + 4) + part
                        line = new_line
            new_lines.append(line)
        
        content = '\n'.join(new_lines)
        
        # Fix multiple empty lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            fixed = True
    
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
    
    return fixed

def main():
    """Fix all files"""
    api_dir = "backend/app/api"
    files_fixed = 0
    
    print("FIXING MISSPELLINGS, UNNEEDED WORDS, AND CODE ISSUES")
    print("="*80)
    
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                if fix_file(filepath):
                    files_fixed += 1
                    rel_path = os.path.relpath(filepath, api_dir)
                    print(f"Fixed: {rel_path}")
    
    print(f"\n{'='*80}")
    print(f"FIXES COMPLETE")
    print(f"Files fixed: {files_fixed}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
