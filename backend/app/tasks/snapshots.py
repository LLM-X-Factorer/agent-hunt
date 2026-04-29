"""Monthly snapshot Celery task.

Wraps the existing scripts/snapshot_monthly.py + scripts/export_trends.py
async pipelines so they run on the beat schedule defined in celery_app.
"""
import asyncio
import logging
import sys
from pathlib import Path

# scripts/ uses sys.path injection at import time; replicate it here so we can
# reuse snapshot() and export_trends.main() instead of duplicating logic.
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from scripts.export_trends import main as export_trends_main
from scripts.snapshot_monthly import snapshot

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.snapshots.run_monthly_snapshot")
def run_monthly_snapshot() -> dict:
    """Compute snapshot rows for all months in data, then export trends JSON."""
    logger.info("monthly snapshot: computing rows")
    asyncio.run(snapshot())
    logger.info("monthly snapshot: exporting trends JSON")
    asyncio.run(export_trends_main())
    return {"status": "ok"}
