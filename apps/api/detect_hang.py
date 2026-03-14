import sys
import os
import builtins
from types import ModuleType

# Force src into path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

stack = []
original_import = builtins.__import__

def debug_import(name, globals=None, locals=None, fromlist=None, level=0):
    if name.startswith(("routers", "services", "models", "config", "database", "common_deps")):
        indent = "  " * len(stack)
        print(f"{indent}Importing: {name}")
        stack.append(name)
        try:
            return original_import(name, globals, locals, fromlist, level)
        finally:
            stack.pop()
    return original_import(name, globals, locals, fromlist, level)

builtins.__import__ = debug_import

print("STAGING: Starting import of main...")
try:
    import main
    print("SUCCESS: main imported!")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
