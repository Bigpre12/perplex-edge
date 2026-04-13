# apps/api/src/workers/celery_schedule.py
from core.sports_config import (
    HIGH_FREQUENCY, MEDIUM_FREQUENCY, LOW_FREQUENCY,
    HIGH_FREQUENCY_SPORTS, MEDIUM_FREQUENCY_SPORTS, LOW_FREQUENCY_SPORTS
)

CELERYBEAT_SCHEDULE = {
    **{
        f"ingest-{sport}": {
            "task": "workers.ev_engine.run_ev_cycle_task",
            "schedule": float(HIGH_FREQUENCY),
            "args": [sport],
        }
        for sport in HIGH_FREQUENCY_SPORTS
    },
    **{
        f"ingest-{sport}": {
            "task": "workers.ev_engine.run_ev_cycle_task",
            "schedule": float(MEDIUM_FREQUENCY),
            "args": [sport],
        }
        for sport in MEDIUM_FREQUENCY_SPORTS
    },
    **{
        f"ingest-{sport}": {
            "task": "workers.ev_engine.run_ev_cycle_task",
            "schedule": float(LOW_FREQUENCY),
            "args": [sport],
        }
        for sport in LOW_FREQUENCY_SPORTS
    },
}
