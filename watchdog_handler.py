"""
watchdog_handler.py
───────────────────
Uses the `watchdog` library to watch directories for filesystem changes.
Debounces rapid events so a single large operation doesn't fire dozens of backups.
"""

import os
import threading
from typing import Dict

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers.polling import PollingObserver

from config import WATCH_DIRS, WATCHDOG_DEBOUNCE_SECONDS
from backup_engine import create_backup
from logger_setup import get_logger

log = get_logger("watchdog")


class _DebounceHandler(FileSystemEventHandler):
    """Fires a backup at most once per WATCHDOG_DEBOUNCE_SECONDS after the last event."""

    def __init__(self, watch_dir: str) -> None:
        super().__init__()
        self.watch_dir = watch_dir
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()

    def _schedule_backup(self, event_path: str) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(
                WATCHDOG_DEBOUNCE_SECONDS,
                self._run_backup,
                args=(event_path,),
            )
            self._timer.daemon = True
            self._timer.start()

    def _run_backup(self, event_path: str) -> None:
        log.info("Filesystem change detected in %s — triggering backup", self.watch_dir)
        create_backup(self.watch_dir, reason=f"watchdog:{event_path}")

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            log.debug("CREATED  %s", event.src_path)
            self._schedule_backup(event.src_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            log.debug("MODIFIED %s", event.src_path)
            self._schedule_backup(event.src_path)

    def on_deleted(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            log.debug("DELETED  %s", event.src_path)
            self._schedule_backup(event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        log.debug("MOVED    %s → %s", event.src_path, event.dest_path)
        self._schedule_backup(event.src_path)


class WatchdogService:
    """Manages an Observer and per-directory debounce handlers."""

    def __init__(self) -> None:
        self._observer = PollingObserver()
        self._handlers: Dict[str, _DebounceHandler] = {}

    def start(self) -> None:
        for watch_dir in WATCH_DIRS:
            expanded = os.path.expanduser(watch_dir)
            if not os.path.isdir(expanded):
                log.warning("Watch directory does not exist (skipped): %s", expanded)
                continue
            handler = _DebounceHandler(watch_dir)
            self._handlers[watch_dir] = handler
            self._observer.schedule(handler, expanded, recursive=True)
            log.info("Watching directory: %s", expanded)

        self._observer.start()
        log.info("Watchdog observer started.")

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()
        log.info("Watchdog observer stopped.")
