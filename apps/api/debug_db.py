# apps/api/debug_db.py
import os
import sys

# Simulation of what config does
# Assuming config is at apps/api/src/config/__init__.py
fake_file = os.path.abspath(os.path.join(os.getcwd(), "src", "config", "__init__.py"))
dirname = os.path.dirname(fake_file)
db_url_default = os.path.abspath(os.path.join(dirname, "..", "..", "src", "data", "perplex_local.db"))

print(f"DEBUG: dirname(__file__): {dirname}")
print(f"DEBUG: Combined path: {db_url_default}")

# Real config import test
sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from config import settings
print(f"DEBUG: settings.DATABASE_URL: {settings.DATABASE_URL}")
