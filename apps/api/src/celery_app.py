# apps/api/src/celery_app.py
from celery import Celery
from config import settings

celery_app = Celery(
    "lucrix_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["workers.ev_engine"] # Register tasks here
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule_filename="celerybeat-schedule",
)

# Load the tiered schedule from the config
from workers.celery_schedule import CELERYBEAT_SCHEDULE
celery_app.conf.beat_schedule = CELERYBEAT_SCHEDULE
