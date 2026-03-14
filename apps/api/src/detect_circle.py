import sys
import os
import importlib.util

sys.path.append('.')

def trace_imports(module_name, visited=None, stack=None):
    if visited is None: visited = set()
    if stack is None: stack = []
    
    if module_name in stack:
        print(f"CIRCLE DETECTED: {' -> '.join(stack)} -> {module_name}")
        return
    
    if module_name in visited:
        return
    
    visited.add(module_name)
    stack.append(module_name)
    
    try:
        # Find the module spec
        spec = importlib.util.find_spec(module_name)
        if spec and spec.origin and spec.origin.endswith('.py'):
            with open(spec.origin, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    parts = line.split()
                    if line.startswith('import '):
                        sub = parts[1].split(',')[0]
                    else:
                        sub = parts[1]
                    
                    # Handle relative imports
                    if sub.startswith('.'):
                        parent = '.'.join(module_name.split('.')[:-1])
                        if sub == '.':
                            sub = parent
                        else:
                            sub = parent + sub
                    
                    if sub.startswith('models') or sub.startswith('services') or sub.startswith('routers') or sub in ['database', 'main', 'dependencies']:
                        trace_imports(sub, visited, stack)
    except Exception as e:
        pass
    
    stack.pop()

print("Analyzing imports...")
trace_imports('main')
print("Done.")
