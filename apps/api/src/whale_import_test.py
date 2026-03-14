import sys
import traceback
sys.path.insert(0, '.')
errors = []

test_imports = [
    ("services.whale_service", "detect_whale_signals"),
    ("services.whale_service", "whale_service"),
    ("routers.whale", "router"),
    ("routers.live", "router"),
    ("routers.ev_calculator", "router"),
    ("routers.hit_rate", "router"),
    ("routers.brain_router", "router"),
    ("services.brain_advanced_service", "BrainAdvancedService"),
]

for mod, attr in test_imports:
    try:
        m = __import__(mod, fromlist=[attr])
        obj = getattr(m, attr, None)
        status = "OK" if obj else "MISSING ATTR"
        print(f"  [{status}] {mod}.{attr}")
    except Exception as e:
        print(f"  [FAIL] {mod}.{attr} -> {type(e).__name__}: {e}")
        errors.append((mod, attr, str(e)))

if errors:
    print(f"\n{len(errors)} import(s) FAILED:")
    for mod, attr, err in errors:
        print(f"  - {mod}.{attr}: {err}")
    with open('import_errors.txt', 'w') as f:
        for mod, attr, err in errors:
            f.write(f"{mod}.{attr}: {err}\n")
else:
    print("\nAll imports passed!")
