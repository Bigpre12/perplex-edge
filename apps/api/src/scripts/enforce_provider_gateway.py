import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[4]
APPS = ROOT / "apps"

FORBIDDEN_PATTERNS = [
    r"https://api\.the-odds-api\.com",
    r"api\.the-odds-api\.com",
    r"bypass_auth\s*=\s*[\"']true[\"']",
    r"next_public_bypass_auth\s*=\s*[\"']true[\"']",
]

ALLOWED_FILES = {
    str((APPS / "api" / "src" / "services" / "odds_api_client.py").resolve()).lower(),
    str((APPS / "api" / "src" / "services" / "external_api_gateway.py").resolve()).lower(),
    str((APPS / "api" / "src" / "services" / "odds_service.py").resolve()).lower(),
    str((APPS / "api" / "src" / "real_sports_api.py").resolve()).lower(),
    str((APPS / "api" / "src" / "routers" / "waterfall.py").resolve()).lower(),
}

IGNORED_SUFFIXES = {".md", ".txt", ".json", ".lock", ".svg", ".pyc"}
IGNORED_PARTS = {"node_modules", ".next", "dist", "build", "agent-transcripts", "__pycache__"}


def main() -> int:
    offenders = []
    for path in APPS.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in IGNORED_SUFFIXES:
            continue
        if any(part in IGNORED_PARTS for part in path.parts):
            continue
        full = str(path.resolve()).lower()
        if "\\apps\\api\\src\\scripts\\" in full and not full.endswith("enforce_provider_gateway.py"):
            continue
        if full in ALLOWED_FILES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pat in FORBIDDEN_PATTERNS:
            if re.search(pat, text):
                offenders.append(str(path))
                break

    if offenders:
        print("Forbidden direct provider references found outside gateway:")
        for f in offenders:
            print(f"- {f}")
        return 1
    print("Provider gateway enforcement passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
