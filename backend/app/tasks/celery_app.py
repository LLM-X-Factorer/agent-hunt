"""Celery app + beat schedule.

Issue #13: monthly snapshot task runs on the 1st of each month and refreshes
both the DB snapshot tables and the frontend trends/ JSON exports.

Deployment (one process — beat embedded into worker):
    cd backend && .venv/bin/celery -A app.tasks.celery_app worker --beat -l info

Or as separate processes if you prefer:
    .venv/bin/celery -A app.tasks.celery_app worker -l info
    .venv/bin/celery -A app.tasks.celery_app beat -l info

Lighter-weight alternative without Celery — system cron:
    0 3 1 * * cd /path/to/agent-hunt/backend && .venv/bin/python scripts/snapshot_monthly.py && .venv/bin/python scripts/export_trends.py
"""
from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "agent_hunt",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.snapshots"],
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=60 * 30,  # 30 min hard cap
    task_soft_time_limit=60 * 25,
    beat_schedule={
        "monthly-snapshot": {
            "task": "app.tasks.snapshots.run_monthly_snapshot",
            "schedule": crontab(minute=0, hour=3, day_of_month=1),
        },
    },
)
