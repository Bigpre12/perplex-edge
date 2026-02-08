#!/usr/bin/env python3
"""
Comprehensive fix for all Railway deployment issues
"""
import os
import re

def fix_all_issues():
    """Fix all known issues"""
    
    # 1. Fix FastAPI regex deprecation warnings
    api_dir = "backend/app/api"
    for root, dirs, files in os.walk(api_dir):
        for filename in files:
            if not filename.endswith('.py'):
                continue
                
            filepath = os.path.join(root, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix regex deprecation
                content = re.sub(r'regex\s*=', 'pattern=', content)
                
                # Add Path import if needed
                if 'Path(' in content and 'from fastapi import' in content and 'Path' not in content.split('from fastapi import')[1].split('\n')[0]:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith('from fastapi import') and 'Path' not in line:
                            lines[i] = line.rstrip() + ', Path'
                            break
                    content = '\n'.join(lines)
                
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Fixed: {filepath}")
                    
            except Exception as e:
                print(f"Error fixing {filepath}: {e}")
    
    print("\nAll fixes applied!")

if __name__ == "__main__":
    fix_all_issues()
