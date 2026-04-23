# apps/api/src/workers/celery_schedule.py
from core.ingest_coordinator_env import INGEST_COORDINATOR_TICK_SECONDS as _COORD_TICK

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
