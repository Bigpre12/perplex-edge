"""Celery ingest coordinator intervals (shared by beat schedule and worker)."""
from __future__ import annotations

import os

INGEST_COORDINATOR_TICK_SECONDS = max(60, int(os.getenv("INGEST_COORDINATOR_TICK_SECONDS", "120")))
INGEST_COORDINATOR_MAX_PER_TICK = max(1, int(os.getenv("INGEST_COORDINATOR_MAX_PER_TICK", "3")))
