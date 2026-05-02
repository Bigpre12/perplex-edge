"""
Celery beat schedule for Perplex-Edge ingest jobs.

Canonical definition lives in ``workers.celery_schedule`` (imported by ``celery_app``).
APScheduler tiered jobs are configured in ``core.ingest_scheduler_config``.
"""
from workers.celery_schedule import CELERYBEAT_SCHEDULE

__all__ = ["CELERYBEAT_SCHEDULE"]
