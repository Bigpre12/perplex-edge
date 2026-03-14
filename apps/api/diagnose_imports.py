import sys
import os

# Diagnostics script for Antigravity
try:
    api_dir = os.path.abspath(r"c:\Users\preio\OneDrive\Documents\Untitled\perplex_engine\perplex-edge\apps\api")
    src_dir = os.path.join(api_dir, "src")
    sys.path.append(src_dir)
    os.chdir(api_dir)
    print(f"Testing import of main from {src_dir}")
    import main
    print("SUCCESS: main.py imported successfully")
    print(f"App instance: {getattr(main, 'app', 'NOT FOUND')}")
    
    # Check if routers are actually included
    for route in main.app.routes:
        if hasattr(route, 'path'):
            print(f"Route found: {route.path}")
            
except Exception as e:
    import traceback
    print("FAILURE: Import error detected")
    traceback.print_exc()
