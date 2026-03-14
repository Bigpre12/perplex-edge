
import sys
import os

# Add current dir to path
sys.path.append(os.getcwd())

try:
    from real_data_connector import real_data_connector
    print("SUCCESS: Imported real_data_connector")
except ImportError as e:
    print(f"FAILED: real_data_connector import error: {e}")
except Exception as e:
    print(f"FAILED: real_data_connector error: {e}")

try:
    from real_sports_api import RealSportsAPI
    print("SUCCESS: Imported RealSportsAPI")
except ImportError as e:
    print(f"FAILED: RealSportsAPI import error: {e}")
except Exception as e:
    print(f"FAILED: RealSportsAPI error: {e}")
