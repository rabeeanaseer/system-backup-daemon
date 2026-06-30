#!/usr/bin/env python3
"""
status_cli.py — Live System & Backup Status Dashboard
──────────────────────────────────────────────────────
Prints a live-refreshing terminal dashboard showing:

  • Real-time CPU / RAM / Disk health
  • Last backup time and size per watched directory
  • Total archive count and disk usage for backups
  • Recent log entries

Usage:
    python status_cli.py           # single snapshot
    python status_cli.py --watch   # refresh every 5 s (Ctrl-C to exit)
    python status_cli.py --watch --interval 2
"""

import argparse
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import psutil

from config import WATCH_DIRS, BACKUP_DIR, LOG_DIR, MONITOR_POLL_SECONDS
from backup_engine import list_backups

# ── ANSI colour helpers ──────────────────────────────────────────────────────
_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_DIM    = "\033[2m"
_GREEN  = "\033[32m"
_YELLOW = "\033[33m"
_RED    = "\033[31m"
_CYAN   = "\033[36m"
_WHITE  = "\033[97m"


def _colour(text: str, *codes: str) -> str:
    return "".join(codes) + text + _RESET


def _bar(percent: float, width: int = 20) -> str:
    filled = int(percent / 100 * width)
    bar = "█" * filled + "░" * (width - filled)
    if percent >= 90:
        colour = _RED
    elif percent >= 75:
        colour = _YELLOW
    else:
        colour = _GREEN
    return _colour(bar, colour)


def _pct_colour(value: float) -> str:
    if value >= 90:
        return _colour(f"{value:5.1f}%", _RED, _BOLD)
    elif value >= 75:
        return _colour(f"{value:5.1f}%", _YELLOW)
    return _colour(f"{value:5.1f}%", _GREEN)


# ── System snapshot ──────────────────────────────────────────────────────────

def _system_section() -> str:
    cpu  = psutil.cpu_percent(interval=0.5)
    mem  = psutil.virtual_memory()
    swap = psutil.swap_memory()

    lines = [
        _colour("  SYSTEM HEALTH", _BOLD, _CYAN),
        "",
        f"  CPU   {_bar(cpu)}  {_pct_colour(cpu)}  ({psutil.cpu_count()} cores)",
        f"  RAM   {_bar(mem.percent)}  {_pct_colour(mem.percent)}"
        f"  ({mem.used/1e9:.1f} GB / {mem.total/1e9:.1f} GB)",
        f"  SWAP  {_bar(swap.percent)}  {_pct_colour(swap.percent)}"
        f"  ({swap.used/1e9:.1f} GB / {swap.total/1e9:.1f} GB)",
        "",
        _colour("  DISK PARTITIONS", _BOLD, _CYAN),
        "",
    ]

    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        mount = part.mountpoint[:28].ljust(28)
        lines.append(
            f"  {_colour(mount, _DIM)}  {_bar(usage.percent)}  "
            f"{_pct_colour(usage.percent)}  "
            f"({usage.free/1e9:.1f} GB free)"
        )

    return "\n".join(lines)


# ── Backup status ─────────────────────────────────────────────────────────────

def _backup_section() -> str:
    lines = [
        "",
        _colour("  BACKUP STATUS", _BOLD, _CYAN),
        "",
    ]

    all_backups = list_backups()
    total_size  = sum(b["size_mb"] for b in all_backups)
    total_count = len(all_backups)

    lines.append(
        f"  Archive dir    {_colour(BACKUP_DIR, _DIM)}"
    )
    lines.append(
        f"  Total archives {_colour(str(total_count), _WHITE, _BOLD)}  "
        f"({total_size:.1f} MB on disk)"
    )
    lines.append("")

    for watch_dir in WATCH_DIRS:
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.basename(watch_dir.rstrip("/\\")))
        dir_backups = [b for b in all_backups if b["file"].startswith(safe + "__")]

        label  = watch_dir.ljust(35)
        exists = os.path.isdir(os.path.expanduser(watch_dir))
        status = _colour("✔ watching", _GREEN) if exists else _colour("✘ missing", _RED)

        if dir_backups:
            last   = dir_backups[0]
            detail = (
                f"last: {_colour(last['created'], _WHITE)}  "
                f"({last['size_mb']} MB)  "
                f"{len(dir_backups)} version(s)"
            )
        else:
            detail = _colour("no backups yet", _DIM)

        lines.append(f"  {_colour(label, _DIM)}  {status}  {detail}")

    return "\n".join(lines)


# ── Recent log tail ───────────────────────────────────────────────────────────

def _log_section(n: int = 6) -> str:
    daemon_log = Path(LOG_DIR) / "daemon.log"
    lines = [
        "",
        _colour("  RECENT LOG  ", _BOLD, _CYAN) + _colour(f"(daemon.log, last {n} lines)", _DIM),
        "",
    ]

    if not daemon_log.exists():
        lines.append(_colour("  No log file yet — daemon hasn't run.", _DIM))
        return "\n".join(lines)

    try:
        with open(daemon_log, "rb") as f:
            # Efficiently grab last ~4 KB
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 4096))
            tail = f.read().decode(errors="replace").splitlines()[-n:]
        for line in tail:
            lines.append("  " + _colour(line, _DIM))
    except OSError:
        lines.append(_colour("  Could not read log.", _RED))

    return "\n".join(lines)


# ── Full dashboard ─────────────────────────────────────────────────────────────

BORDER = _colour("─" * 64, _DIM)

def print_dashboard() -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print()
    print(BORDER)
    print(_colour(f"  ◉ System Monitor & Backup Daemon", _BOLD, _WHITE) +
          _colour(f"          {now}", _DIM))
    print(BORDER)
    print(_system_section())
    print(_backup_section())
    print(_log_section())
    print()
    print(BORDER)


def main() -> None:
    parser = argparse.ArgumentParser(description="Live system & backup status dashboard")
    parser.add_argument("--watch",    action="store_true", help="Refresh continuously")
    parser.add_argument("--interval", type=float, default=5.0,
                        help="Refresh interval in seconds (default: 5)")
    args = parser.parse_args()

    if not args.watch:
        print_dashboard()
        return

    try:
        while True:
            # Clear screen on each refresh
            print("\033[2J\033[H", end="")
            print_dashboard()
            print(_colour(f"  Refreshing every {args.interval}s — Ctrl-C to exit", _DIM))
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n  Exited.")


if __name__ == "__main__":
    main()
