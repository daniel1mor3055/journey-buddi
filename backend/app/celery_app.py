from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "journey_buddi",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.tasks.monitoring.*": {"queue": "monitoring"},
        "app.tasks.briefings.*": {"queue": "briefings"},
        "app.tasks.notifications.*": {"queue": "notifications"},
    },
    beat_schedule={
        "refresh-conditions-hourly": {
            "task": "app.tasks.monitoring.refresh_conditions",
            "schedule": 3600.0,
        },
        "check-and-generate-briefings": {
            "task": "app.tasks.briefings.check_and_generate",
            "schedule": 300.0,
        },
        "check-condition-alerts": {
            "task": "app.tasks.monitoring.check_alerts",
            "schedule": 1800.0,
        },
    },
)

celery_app.autodiscover_tasks(["app.tasks"])
