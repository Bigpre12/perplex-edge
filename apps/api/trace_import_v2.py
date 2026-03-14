import sys
import os

# Ensure src is in the path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

try:
    print("DEBUG: Attempting to import database...")
    import database
    print(f"DEBUG: database module: {database}")
    print(f"DEBUG: Dir of database: {dir(database)}")
    print(f"DEBUG: get_db in database: {'get_db' in dir(database)}")
    
    print("DEBUG: Attempting to import models...")
    import models
    print("DEBUG: Success importing models")
    
    print("DEBUG: Attempting to import from database import get_db...")
    from database import get_db
    print(f"DEBUG: get_db: {get_db}")

except Exception as e:
    import traceback
    traceback.print_exc()
