import sys
import os

# Ensure src is in the path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

try:
    print("Importing database...")
    import database
    print(f"database.get_db: {getattr(database, 'get_db', 'MISSING')}")
    
    print("Importing models...")
    import models
    print("Success")
except ImportError as e:
    import traceback
    traceback.print_exc()
except Exception as e:
    import traceback
    traceback.print_exc()
