import sys
import traceback

try:
    sys.path.append('.')
    import db.session
    print("db.session imported successfully")
except Exception as e:
    print("Error importing db.session:")
    traceback.print_exc()
