import json
import os
import sys

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from main import app


SNAPSHOT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "openapi",
    "openapi.snapshot.json",
)


def main() -> int:
    current = app.openapi()
    if not os.path.exists(SNAPSHOT_PATH):
        os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)
        with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, sort_keys=True)
        print("OpenAPI snapshot created.")
        return 0

    with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
        expected = json.load(f)

    if current != expected or _failed_router_imports:
        if _failed_router_imports:
            print("\n❌ HARD FAILURE: Routers failed to import. OpenAPI schema is incomplete.")
            for name, err in _failed_router_imports:
                print(f"  - {name}: {err}")
        
        if current != expected:
            print("OpenAPI snapshot drift detected. Regenerate snapshot intentionally.")
            
            # Dump current for CI artifact upload
            with open("openapi.json", "w", encoding="utf-8") as f:
                json.dump(current, f, indent=2, sort_keys=True)
                
            import difflib
            current_str = json.dumps(current, indent=2, sort_keys=True)
            expected_str = json.dumps(expected, indent=2, sort_keys=True)
            
            diff = difflib.unified_diff(
                expected_str.splitlines(keepends=True),
                current_str.splitlines(keepends=True),
                fromfile="expected",
                tofile="current",
            )
            print("".join(diff))
            
        if _failed_router_imports:
            raise RuntimeError(f"CI Blocked: {len(_failed_router_imports)} routers failed to import.")
            
        return 1
    
    print("OpenAPI snapshot check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

