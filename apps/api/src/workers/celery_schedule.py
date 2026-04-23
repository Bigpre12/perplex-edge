# apps/api/src/workers/celery_schedule.py
from core.sports_config import ALL_SPORTS, ingest_interval_seconds_for_sport

CELERYBEAT_SCHEDULE = {
    f"ingest-{sport}": {
        "task": "workers.ev_engine.run_ev_cycle_task",
        "schedule": ingest_interval_seconds_for_sport(sport),
        "args": [sport],
    }
    for sport in ALL_SPORTS
}
