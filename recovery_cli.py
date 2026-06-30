#!/usr/bin/env python3
"""
recovery_cli.py — Backup Recovery Tool
───────────────────────────────────────
List available backup versions and restore any archive interactively.

Usage:
    python recovery_cli.py list [<source_dir>]
    python recovery_cli.py restore <archive_path> <restore_to>
    python recovery_cli.py interactive
"""

import argparse
import os
import sys

from backup_engine import list_backups, restore_backup
from logger_setup import get_logger

log = get_logger("recovery")


def cmd_list(source_dir=None):
    backups = list_backups(source_dir)
    if not backups:
        print("No backups found.")
        return

    print(f"\n{'#':<4} {'Archive':<50} {'Size (MB)':<12} {'Created'}")
    print("─" * 90)
    for i, b in enumerate(backups, 1):
        print(f"{i:<4} {b['file']:<50} {b['size_mb']:<12} {b['created']}")
    print()


def cmd_restore(archive_path: str, restore_to: str):
    ok = restore_backup(archive_path, restore_to)
    if ok:
        print(f"✔  Restore complete → {restore_to}")
    else:
        print("✘  Restore failed. Check logs for details.")
        sys.exit(1)


def cmd_interactive():
    print("\n─── Backup Recovery CLI ───────────────────────────────────────")
    backups = list_backups()
    if not backups:
        print("No backups found.")
        return

    print(f"\n{'#':<4} {'Archive':<50} {'Size (MB)':<12} {'Created'}")
    print("─" * 90)
    for i, b in enumerate(backups, 1):
        print(f"{i:<4} {b['file']:<50} {b['size_mb']:<12} {b['created']}")
    print()

    try:
        choice = int(input("Enter backup number to restore (0 to cancel): "))
    except (ValueError, EOFError):
        print("Cancelled.")
        return

    if choice == 0 or choice > len(backups):
        print("Cancelled.")
        return

    selected = backups[choice - 1]
    restore_to = input(f"Restore to directory [{os.path.expanduser('~/restored_backup')}]: ").strip()
    if not restore_to:
        restore_to = os.path.expanduser("~/restored_backup")

    cmd_restore(selected["path"], restore_to)


def main():
    parser = argparse.ArgumentParser(
        description="Backup Recovery Tool for System Backup Daemon",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list", help="List available backups")
    p_list.add_argument("source_dir", nargs="?", help="Filter by source directory")

    p_restore = sub.add_parser("restore", help="Restore a specific archive")
    p_restore.add_argument("archive_path", help="Path to the .zip archive")
    p_restore.add_argument("restore_to",   help="Directory to extract into")

    sub.add_parser("interactive", help="Interactive guided restore")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(getattr(args, "source_dir", None))
    elif args.command == "restore":
        cmd_restore(args.archive_path, args.restore_to)
    elif args.command == "interactive":
        cmd_interactive()
    else:
        parser.print_help()
        print("\nTip: run  python recovery_cli.py interactive  for guided restore.")


if __name__ == "__main__":
    main()
