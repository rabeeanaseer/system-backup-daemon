# System Monitor & Automated Backup Daemon

A background Python daemon that continuously monitors system health and automatically backs up directories when changes are detected.

---

## Features

| Feature | Details |
|---|---|
| **CPU / RAM / Disk monitoring** | Polls every 5 s, logs warnings at configurable thresholds |
| **Filesystem watchdog** | Detects file create / modify / delete / move in watched dirs |
| **Auto-backup on change** | Debounced — waits 10 s after last event before zipping |
| **Scheduled backups** | Full backup of all watched dirs every hour |
| **Versioned archives** | Timestamped ZIPs; keeps latest N, prunes oldest automatically |
| **Backup recovery** | CLI tool to list and restore any saved version |
| **Rotating logs** | Separate log files per component, 10 MB max, 5 rotations |

---

## File Layout

```
02-system-backup-daemon/
├── daemon.py          ← main entry point (start here)
├── config.py          ← all tuneable settings
├── system_monitor.py  ← CPU / RAM / disk polling
├── watchdog_handler.py← filesystem event watcher
├── backup_engine.py   ← ZIP creation, versioning, pruning
├── scheduler.py       ← timed full-backup loop
├── recovery_cli.py    ← restore tool
├── logger_setup.py    ← shared rotating logger
├── requirements.txt
├── backups/           ← generated archives (git-ignored)
└── logs/              ← generated log files (git-ignored)
```

---

## Setup

```bash
cd 02-system-backup-daemon

# Install dependencies
pip install -r requirements.txt
```

---

## Run the Daemon

```bash
python daemon.py
```

Press **Ctrl-C** to stop cleanly. Logs appear both in the terminal and in `logs/`.

---

## Configuration (`config.py`)

```python
# Directories to watch and back up
WATCH_DIRS = ["~/Documents", "~/Desktop"]

# Where archives are stored
BACKUP_DIR = "./backups"

# Alert thresholds
CPU_THRESHOLD_PCT   = 85.0
RAM_THRESHOLD_PCT   = 80.0
DISK_THRESHOLD_PCT  = 90.0

# Seconds to wait after last fs event before triggering a backup
WATCHDOG_DEBOUNCE_SECONDS = 10

# How many versions to keep per watched directory
MAX_VERSIONS_PER_DIR = 10

# Scheduled backup interval (seconds)
SCHEDULED_BACKUP_INTERVAL_SECONDS = 3600   # 1 hour

# System monitor poll rate
MONITOR_POLL_SECONDS = 5
```

---

## Backup Recovery

**List all saved backups:**
```bash
python recovery_cli.py list
```

**List backups for one directory:**
```bash
python recovery_cli.py list ~/Documents
```

**Restore a specific archive:**
```bash
python recovery_cli.py restore backups/Documents__20260621_143000.zip ~/restored
```

**Interactive guided restore:**
```bash
python recovery_cli.py interactive
```

---

## Run as a Background Service (Linux)

Create `/etc/systemd/system/backup-daemon.service`:

```ini
[Unit]
Description=System Monitor & Backup Daemon
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/02-system-backup-daemon
ExecStart=/usr/bin/python3 daemon.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable backup-daemon
sudo systemctl start backup-daemon
sudo systemctl status backup-daemon
```

---

## Run as a Background Service (macOS launchd)

Create `~/Library/LaunchAgents/com.backup.daemon.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.backup.daemon</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/path/to/02-system-backup-daemon/daemon.py</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>WorkingDirectory</key>
  <string>/path/to/02-system-backup-daemon</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.backup.daemon.plist
```

---

## Dependencies

- `psutil` — system metrics (CPU, RAM, disk)
- `watchdog` — cross-platform filesystem events
- `zipfile`, `logging`, `threading` — Python standard library
