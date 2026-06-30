import os

# ─── Directories to watch & back up ─────────────────────────────────────────
WATCH_DIRS = [
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Desktop"),
]

# Where versioned archives are stored
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "backups")

# Where logs are written
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")

# ─── Monitoring thresholds ────────────────────────────────────────────────────
CPU_THRESHOLD_PCT    = 85.0   # alert when CPU exceeds this %
RAM_THRESHOLD_PCT    = 80.0   # alert when RAM exceeds this %
DISK_THRESHOLD_PCT   = 90.0   # alert when any disk partition exceeds this %

# ─── Backup behaviour ────────────────────────────────────────────────────────
# Seconds to wait after the last filesystem event before triggering a backup
# (debounce — prevents a storm of backups during a big file operation)
WATCHDOG_DEBOUNCE_SECONDS = 10

# How many versioned archives to keep per watched directory (oldest pruned first)
MAX_VERSIONS_PER_DIR = 10

# ─── Scheduled backup ────────────────────────────────────────────────────────
# Run a full scheduled backup every N seconds (3600 = hourly)
SCHEDULED_BACKUP_INTERVAL_SECONDS = 3600

# ─── Monitoring poll interval ────────────────────────────────────────────────
MONITOR_POLL_SECONDS = 5
