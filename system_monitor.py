"""
system_monitor.py
─────────────────
Polls CPU, RAM, and disk metrics every MONITOR_POLL_SECONDS.
Logs warnings when thresholds are exceeded.
Runs forever in its own thread.
"""

import logging
import threading
import time
import psutil

from config import (
    CPU_THRESHOLD_PCT,
    RAM_THRESHOLD_PCT,
    DISK_THRESHOLD_PCT,
    MONITOR_POLL_SECONDS,
)
from logger_setup import get_logger

log = get_logger("monitor")


def _fmt(value: float, unit: str = "%") -> str:
    return f"{value:.1f}{unit}"


def poll_once() -> dict:
    """Collect a single snapshot of system health. Returns a plain dict."""
    cpu = psutil.cpu_percent(interval=1)

    mem = psutil.virtual_memory()
    ram_used = mem.percent

    disks = {}
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks[part.mountpoint] = {
                "total_gb": usage.total / 1e9,
                "used_gb":  usage.used  / 1e9,
                "free_gb":  usage.free  / 1e9,
                "percent":  usage.percent,
            }
        except PermissionError:
            pass

    return {"cpu": cpu, "ram": ram_used, "disks": disks}


def _monitor_loop(stop_event: threading.Event) -> None:
    log.info("System monitor started (poll every %ds)", MONITOR_POLL_SECONDS)
    while not stop_event.is_set():
        try:
            snap = poll_once()

            level = logging.WARNING if snap["cpu"] >= CPU_THRESHOLD_PCT else logging.INFO
            log.log(level, "CPU  %s", _fmt(snap["cpu"]))

            level = logging.WARNING if snap["ram"] >= RAM_THRESHOLD_PCT else logging.INFO
            log.log(level, "RAM  %s  (used: %.1f GB / %.1f GB)",
                    _fmt(snap["ram"]),
                    psutil.virtual_memory().used / 1e9,
                    psutil.virtual_memory().total / 1e9)

            for mount, info in snap["disks"].items():
                level = logging.WARNING if info["percent"] >= DISK_THRESHOLD_PCT else logging.DEBUG
                log.log(level, "DISK %-20s  %s  (%.1f GB free)",
                        mount, _fmt(info["percent"]), info["free_gb"])

        except Exception as exc:
            log.error("Monitor poll error: %s", exc)

        stop_event.wait(MONITOR_POLL_SECONDS)

    log.info("System monitor stopped.")


def start_monitor(stop_event: threading.Event) -> threading.Thread:
    t = threading.Thread(target=_monitor_loop, args=(stop_event,), daemon=True, name="SystemMonitor")
    t.start()
    return t
