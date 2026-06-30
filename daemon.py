#!/usr/bin/env python3
"""
daemon.py — System Monitor & Automated Backup Daemon
─────────────────────────────────────────────────────
Entry point.  Starts all services:

  1. SystemMonitor  — polls CPU / RAM / Disk, logs warnings on threshold breach
  2. WatchdogService — watches WATCH_DIRS for filesystem changes, triggers backups
  3. BackupScheduler — full backup of all WATCH_DIRS on a fixed interval

Press Ctrl-C to stop gracefully.
"""

import signal
import sys
import threading

from logger_setup import get_logger
from system_monitor import start_monitor
from watchdog_handler import WatchdogService
from scheduler import start_scheduler
from config import WATCH_DIRS, BACKUP_DIR, LOG_DIR

log = get_logger("daemon")

BANNER = r"""
  ╔══════════════════════════════════════════════════════╗
  ║   System Monitor & Automated Backup Daemon  v1.0    ║
  ╚══════════════════════════════════════════════════════╝
"""


def main() -> None:
    print(BANNER)
    log.info("Starting daemon …")
    log.info("Backup directory : %s", BACKUP_DIR)
    log.info("Log directory    : %s", LOG_DIR)
    log.info("Watching         : %s", WATCH_DIRS)

    stop_event = threading.Event()

    # ── 1. System monitor ────────────────────────────────────────────────────
    monitor_thread = start_monitor(stop_event)

    # ── 2. Watchdog ──────────────────────────────────────────────────────────
    watchdog = WatchdogService()
    watchdog.start()

    # ── 3. Backup scheduler ──────────────────────────────────────────────────
    scheduler_thread = start_scheduler(stop_event)

    # ── Graceful shutdown ────────────────────────────────────────────────────
    def _shutdown(signum, frame):
        log.info("Shutdown signal received (%s). Stopping …", signum)
        stop_event.set()
        watchdog.stop()
        monitor_thread.join(timeout=5)
        scheduler_thread.join(timeout=5)
        log.info("Daemon stopped cleanly. Goodbye.")
        sys.exit(0)

    signal.signal(signal.SIGINT,  _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    log.info("Daemon running. Press Ctrl-C to stop.")

    # Keep the main thread alive
    try:
        while True:
            stop_event.wait(timeout=1)
    except KeyboardInterrupt:
        _shutdown(signal.SIGINT, None)


if __name__ == "__main__":
    main()
