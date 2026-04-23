# apps/api/src/workers/celery_schedule.py
import os

# Coordinator polls this often; per-sport spacing is enforced inside the task via quota scaling.
_COORD_TICK = max(60, int(os.getenv("INGEST_COORDINATOR_TICK_SECONDS", "120")))

CELERYBEAT_SCHEDULE = {
    "ingest-coordinator": {
        "task": "workers.ingest_coordinator.ingest_coordinator_task",
        "schedule": float(_COORD_TICK),
    },
    "arb-cleanup": {
        "task": "workers.arb_cleanup.arb_cleanup_task",
        "schedule": 1800.0,
    },
}
