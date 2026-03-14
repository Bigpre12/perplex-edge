
import sys
import os

# Add src to path
sys.path.append(os.getcwd())

try:
    from app_core.sport_constants import get_sport_id
    print(f"SUCCESS: get_sport_id is {get_sport_id}")
except Exception as e:
    print(f"FAILED: {e}")
