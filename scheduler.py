"""
scheduler.py
────────────
Runs a full backup of all WATCH_DIRS on a fixed interval.
Runs in its own daemon thread so it doesn't block the main loop.
"""

import threading

from config import WATCH_DIRS, SCHEDULED_BACKUP_INTERVAL_SECONDS
from backup_engine import create_backup
from logger_setup import get_logger

log = get_logger("scheduler")


def _scheduler_loop(stop_event: threading.Event) -> None:
    log.info(
        "Scheduled backup every %ds for: %s",
        SCHEDULED_BACKUP_INTERVAL_SECONDS,
        ", ".join(WATCH_DIRS),
    )

    # Wait the full interval before the first scheduled run
    # (watchdog handles any immediate changes at startup)
    triggered = stop_event.wait(SCHEDULED_BACKUP_INTERVAL_SECONDS)
    while not triggered:
        log.info("Scheduled backup triggered.")
        for d in WATCH_DIRS:
            create_backup(d, reason="scheduled")
        triggered = stop_event.wait(SCHEDULED_BACKUP_INTERVAL_SECONDS)

    log.info("Scheduler stopped.")


def start_scheduler(stop_event: threading.Event) -> threading.Thread:
    t = threading.Thread(
        target=_scheduler_loop,
        args=(stop_event,),
        daemon=True,
        name="BackupScheduler",
    )
    t.start()
    return t
