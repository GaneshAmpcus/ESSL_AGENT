"""
scheduler.py
Configures APScheduler to fire run_sync_cycle() on a fixed interval.

Key settings:
  coalesce=True     — if a run is missed, only fire once (not many times)
  max_instances=1   — never run two sync cycles simultaneously
  misfire_grace_time — tolerate slight scheduling delays without firing twice
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

import config
from sync import run_sync_cycle
from logger import get_logger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED

log = get_logger(__name__)


def build_scheduler() -> BlockingScheduler:
    scheduler = BlockingScheduler(timezone="UTC")

    scheduler.add_job(
        func               = run_sync_cycle,
        trigger            = IntervalTrigger(seconds=config.SYNC_INTERVAL_SECONDS),
        id                 = "essl_sync",
        name               = "ESSL → HRMS punch sync",
        coalesce           = True,
        max_instances      = 1,
        misfire_grace_time = 60,
    )

    # ADD THESE:
    def _on_error(event):
        log.critical("Scheduler job error: %s", event.exception, exc_info=True)

    def _on_missed(event):
        log.warning("Scheduler job missed — previous cycle took too long")

    scheduler.add_listener(_on_error, EVENT_JOB_ERROR)
    scheduler.add_listener(_on_missed, EVENT_JOB_MISSED)

    log.info(
        "Scheduler configured — interval: %ds (%dm)",
        config.SYNC_INTERVAL_SECONDS,
        config.SYNC_INTERVAL_SECONDS // 60,
    )
    return scheduler
