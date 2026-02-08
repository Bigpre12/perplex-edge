#!/usr/bin/env python3
"""
Fix all FastAPI Query/Path parameter issues across API files.
This script finds all instances where path parameters use Query instead of Path.
"""

import os
import re

api_dir = "backend/app/api"
fixed_files = []
errors = []

# Find all Python files in the API directory
for root, dirs, files in os.walk(api_dir):
    for filename in files:
        if not filename.endswith('.py'):
            continue
            
        filepath = os.path.join(root, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Check if Path is already imported
            has_path_import = 'from fastapi import' in content and 'Path' in content.split('from fastapi import')[1].split('\n')[0]
            
            # Add Path import if needed
            if not has_path_import and 'from fastapi import' in content:
                content = content.replace(
                    'from fastapi import',
                    'from fastapi import'
                )
                # Find the fastapi import line and add Path
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('from fastapi import') and 'Path' not in line:
                        lines[i] = line.rstrip() + ', Path'
                        break
                content = '\n'.join(lines)
            
            # Find all @router.get/@router.post/etc with path parameters like {sport_id}
            # and fix the corresponding function parameters that use Query instead of Path
            
            # Pattern to find route decorators with path params
            route_pattern = r'(@router\.(get|post|put|delete)\(["\']([^"\']*\{([^}]+)\}[^"\']*)["\'][^)]*\)\nasync def [^(]+\([^)]*\))'
            
            matches = list(re.finditer(route_pattern, content, re.MULTILINE))
            
            for match in matches:
                # Get the function signature
                func_start = match.end()
                func_end = content.find('):', func_start)
                if func_end == -1:
                    continue
                    
                func_signature = content[func_start:func_end]
                
                # Check if any path parameter uses Query
                path_param = match.group(4)  # The parameter name inside {}
                
                # Fix common patterns where path params use Query
                for param in ['sport_id', 'pick_id', 'player_id', 'game_id', 'market_id', 'team_id', 'id', 'player_name', 'market', 'stat_type', 'date']:
                    # Pattern: param: int = Query(...) or param: str = Query(...)
                    query_pattern = rf'({param}:\s*(?:int|str)\s*=\s*)Query\('
                    if re.search(query_pattern, func_signature):
                        # Check if this param is in the path
                        if f'{{{param}}}' in match.group(3):
                            func_signature = re.sub(query_pattern, r'\1Path(', func_signature)
                
                content = content[:func_start] + func_signature + content[func_end:]
            
            # Also handle cases where the decorator and function are on separate lines
            # Find function definitions that follow route decorators
            lines = content.split('\n')
            new_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # Check if this is a route decorator with path params
                route_match = re.match(r'@(router|app)\.\w+\(["\'][^"\']*\{(\w+)\}[^"\']*["\']', line)
                if route_match:
                    path_param = route_match.group(2)
                    new_lines.append(line)
                    i += 1
                    
                    # Find the function definition line
                    while i < len(lines) and not lines[i].strip().startswith('async def ') and not lines[i].strip().startswith('def '):
                        new_lines.append(lines[i])
                        i += 1
                    
                    if i < len(lines):
                        func_line = lines[i]
                        # Replace Query with Path for the path parameter
                        query_pattern = rf'({path_param}:\s*(?:int|str|float)\s*=\s*)Query\('
                        if re.search(query_pattern, func_line) and f'{{{path_param}}}' in line:
                            func_line = re.sub(query_pattern, r'\1Path(', func_line)
                        new_lines.append(func_line)
                        i += 1
                else:
                    new_lines.append(line)
                    i += 1
            
            content = '\n'.join(new_lines)
            
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(filepath)
                print(f"✓ Fixed: {filepath}")
                
        except Exception as e:
            errors.append(f"{filepath}: {str(e)}")
            print(f"✗ Error in {filepath}: {e}")

print(f"\n{'='*60}")
print(f"SUMMARY:")
print(f"  Fixed files: {len(fixed_files)}")
print(f"  Errors: {len(errors)}")
print(f"{'='*60}")

if fixed_files:
    print("\nFixed files:")
    for f in fixed_files:
        print(f"  - {f}")
        
if errors:
    print("\nErrors:")
    for e in errors:
        print(f"  - {e}")
