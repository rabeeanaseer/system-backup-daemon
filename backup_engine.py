"""
backup_engine.py
────────────────
Creates versioned ZIP archives of a directory.
Prunes old archives once MAX_VERSIONS_PER_DIR is exceeded.
Supports listing and extracting (recovery) of any stored version.
"""

import os
import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from config import BACKUP_DIR, MAX_VERSIONS_PER_DIR
from logger_setup import get_logger

log = get_logger("backup")


def _archive_name(source_dir: str) -> str:
    """Build a timestamped archive filename for a given source directory."""
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.basename(source_dir.rstrip("/\\")))
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{safe}__{ts}.zip"


def _existing_archives(source_dir: str) -> List[Path]:
    """Return all archives for *source_dir*, sorted oldest-first."""
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.basename(source_dir.rstrip("/\\")))
    pattern = re.compile(rf"^{re.escape(safe)}__\d{{8}}_\d{{6}}\.zip$")
    dest = Path(BACKUP_DIR)
    archives = sorted(
        [p for p in dest.iterdir() if p.is_file() and pattern.match(p.name)],
        key=lambda p: p.stat().st_mtime,
    )
    return archives


def create_backup(source_dir: str, reason: str = "manual") -> Optional[str]:
    """
    Compress *source_dir* into a versioned ZIP inside BACKUP_DIR.

    Returns the path of the created archive, or None on failure.
    """
    source_dir = os.path.expanduser(source_dir)
    if not os.path.isdir(source_dir):
        log.warning("Skipping backup — directory does not exist: %s", source_dir)
        return None

    os.makedirs(BACKUP_DIR, exist_ok=True)
    archive_path = os.path.join(BACKUP_DIR, _archive_name(source_dir))

    log.info("Backing up [%s] → %s  (reason: %s)", source_dir, archive_path, reason)

    try:
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            for root, dirs, files in os.walk(source_dir):
                # Skip hidden dirs and our own backup/log folders
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for fname in files:
                    if fname.startswith("."):
                        continue
                    full = os.path.join(root, fname)
                    arcname = os.path.relpath(full, os.path.dirname(source_dir))
                    try:
                        zf.write(full, arcname)
                    except (PermissionError, OSError) as e:
                        log.debug("Skipped file %s: %s", full, e)

        size_mb = os.path.getsize(archive_path) / 1e6
        log.info("Backup complete: %s  (%.2f MB)", archive_path, size_mb)

        _prune_old_archives(source_dir)
        return archive_path

    except Exception as exc:
        log.error("Backup failed for %s: %s", source_dir, exc)
        if os.path.exists(archive_path):
            os.remove(archive_path)
        return None


def _prune_old_archives(source_dir: str) -> None:
    """Delete oldest archives if we exceed MAX_VERSIONS_PER_DIR."""
    archives = _existing_archives(source_dir)
    excess = len(archives) - MAX_VERSIONS_PER_DIR
    for old in archives[:excess]:
        log.info("Pruning old archive: %s", old.name)
        old.unlink()


def list_backups(source_dir: Optional[str] = None) -> List[dict]:
    """
    Return a list of backup metadata dicts.
    If *source_dir* is given, only show backups for that directory.
    """
    dest = Path(BACKUP_DIR)
    if not dest.exists():
        return []

    results = []
    for p in sorted(dest.iterdir(), key=lambda f: f.stat().st_mtime, reverse=True):
        if not p.suffix == ".zip":
            continue
        if source_dir:
            safe = re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.basename(source_dir.rstrip("/\\")))
            if not p.name.startswith(safe + "__"):
                continue
        results.append({
            "file":     p.name,
            "path":     str(p),
            "size_mb":  round(p.stat().st_size / 1e6, 2),
            "created":  datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        })
    return results


def restore_backup(archive_path: str, restore_to: str) -> bool:
    """
    Extract *archive_path* into *restore_to*.

    Returns True on success, False on failure.
    """
    if not os.path.isfile(archive_path):
        log.error("Archive not found: %s", archive_path)
        return False

    restore_to = os.path.expanduser(restore_to)
    os.makedirs(restore_to, exist_ok=True)

    log.info("Restoring %s → %s", archive_path, restore_to)
    try:
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(restore_to)
        log.info("Restore complete → %s", restore_to)
        return True
    except Exception as exc:
        log.error("Restore failed: %s", exc)
        return False
