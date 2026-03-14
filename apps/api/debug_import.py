import sys
import os
import traceback

# Mimic run_api.py sys.path logic
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

print(f"PYTHONPATH: {sys.path}")
print(f"CWD: {os.getcwd()}")

try:
    print("Attempting to import dependencies...")
    import dependencies
    print("Successfully imported dependencies")
    print(f"dependencies file: {dependencies.__file__}")
except Exception:
    print("FAILED to import dependencies")
    traceback.print_exc()

try:
    print("\nAttempting to import utils.auth_supabase...")
    import utils.auth_supabase
    print("Successfully imported utils.auth_supabase")
    print(f"utils.auth_supabase file: {utils.auth_supabase.__file__}")
    print(f"Names in utils.auth_supabase: {dir(utils.auth_supabase)}")
except Exception:
    print("FAILED to import utils.auth_supabase")
    traceback.print_exc()
