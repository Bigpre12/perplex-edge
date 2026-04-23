"""Brain-related environment variables (no imports from brain.engine to avoid cycles)."""
from __future__ import annotations

import os

BRAIN_SKIP_WHEN_FRESH_MINUTES = int(os.getenv("BRAIN_SKIP_WHEN_FRESH_MINUTES", "7"))


def brain_cache_skip_enabled() -> bool:
    return os.getenv("BRAIN_CACHE_SKIP", "true").strip().lower() in ("1", "true", "yes", "on")
