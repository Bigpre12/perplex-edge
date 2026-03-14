import sys
import os
print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path}")
try:
    import config
    print("SUCCESS: imported config")
    print(f"Config file: {config.__file__}")
    from config import settings
    print("SUCCESS: imported settings from config")
except Exception as e:
    print(f"FAILED: {e}")
