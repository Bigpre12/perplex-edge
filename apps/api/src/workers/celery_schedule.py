# apps/api/src/workers/celery_schedule.py
from config.sports_config import HIGH_FREQUENCY, MEDIUM_FREQUENCY, LOW_FREQUENCY

CELERYBEAT_SCHEDULE = {
    **{
        f"ingest-{sport}": {
            "task": "workers.ev_engine.run_ev_cycle_task",
            "schedule": 120.0,   # 2 min
            "args": [sport],
        }
        for sport in HIGH_FREQUENCY
    },
    **{
        f"ingest-{sport}": {
            "task": "workers.ev_engine.run_ev_cycle_task",
            "schedule": 300.0,   # 5 min
            "args": [sport],
        }
        for sport in MEDIUM_FREQUENCY
    },
    **{
        f"ingest-{sport}": {
            "task": "workers.ev_engine.run_ev_cycle_task",
            "schedule": 1800.0,  # 30 min
            "args": [sport],
        }
        for sport in LOW_FREQUENCY
    },
}
