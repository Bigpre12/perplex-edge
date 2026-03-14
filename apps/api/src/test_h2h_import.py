import sys
import os

sys.path.append('.')

print("Testing services.h2h_service...", end=' ')
try:
    from services.h2h_service import h2h_service
    print("✅ OK")
except Exception as e:
    import traceback
    print(f"❌ FAILED: {e}")
    traceback.print_exc()
