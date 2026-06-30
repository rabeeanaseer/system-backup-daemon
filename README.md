# 🛡️ System Monitor & Automated Backup Daemon

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=for-the-badge)
![Architecture](https://img.shields.io/badge/Architecture-Modular-orange?style=for-the-badge)

### 🚀 Intelligent Python daemon for real-time system monitoring, automated versioned backups, filesystem event detection, scheduled backup orchestration, and CLI-based recovery.

</div>

---

## 🎥 Live Demonstration

> 📹 **Watch the daemon running in real time**



https://github.com/user-attachments/assets/6986d54f-aaba-4fb1-b68c-f6034a9a60f9



---

# 📖 Overview

This project is a production-style Python daemon that continuously monitors system resources while watching selected directories for filesystem activity. Whenever changes occur, it intelligently creates versioned ZIP backups, maintains backup history, and provides a command-line recovery interface.

The application demonstrates practical software engineering concepts including:

- Event-driven programming
- Background services
- Concurrent execution
- Filesystem monitoring
- Automated scheduling
- Logging
- Configuration management
- Fault-tolerant automation

---

# ✨ Features

| Feature | Description |
|----------|-------------|
| 📊 System Monitoring | Real-time CPU, RAM and Disk monitoring |
| 👀 Filesystem Watchdog | Detects file creation, deletion, modification and rename events |
| ⚡ Event-driven Backups | Automatically creates backups after filesystem changes |
| ⏱ Scheduled Backups | Performs periodic full backups |
| 📦 Versioned Archives | Timestamped ZIP archives with automatic pruning |
| ♻️ Backup Recovery | Restore previous backups through CLI |
| 📝 Rotating Logs | Persistent structured logging with automatic rotation |
| ⚙️ Configurable | Easily customize thresholds, directories and schedules |

---

# 🏗 Architecture

```
                +------------------+
                |    daemon.py     |
                +---------+--------+
                          |
          +---------------+---------------+
          |                               |
          |                               |
+---------v---------+           +---------v---------+
| System Monitor    |           | Watchdog Handler  |
| CPU • RAM • Disk  |           | Filesystem Events |
+---------+---------+           +---------+---------+
          |                               |
          |                               |
          +---------------+---------------+
                          |
                  +-------v--------+
                  | Backup Engine  |
                  | ZIP Versioning |
                  +-------+--------+
                          |
               +----------v----------+
               | Backup Storage      |
               +----------+----------+
                          |
                +---------v---------+
                | Recovery CLI      |
                +-------------------+
```

---

# 📂 Project Structure

```
system-backup-daemon/
│
├── daemon.py
├── backup_engine.py
├── watchdog_handler.py
├── system_monitor.py
├── scheduler.py
├── recovery_cli.py
├── logger_setup.py
├── config.py
├── requirements.txt
│
├── backups/
└── logs/
```

---

# ⚙️ Installation

```bash
git clone https://github.com/USERNAME/system-backup-daemon.git

cd system-backup-daemon

pip install -r requirements.txt
```

---

# ▶️ Running

```bash
python daemon.py
```

The daemon starts monitoring immediately.

---

# ⚙️ Configuration

Modify **config.py**

```python
WATCH_DIRS = [
    "~/Documents",
    "~/Desktop"
]

BACKUP_DIR = "./backups"

CPU_THRESHOLD_PCT = 85
RAM_THRESHOLD_PCT = 80
DISK_THRESHOLD_PCT = 90

MAX_VERSIONS_PER_DIR = 10
```

---

# 🔄 Backup Recovery

List backups

```bash
python recovery_cli.py list
```

Restore

```bash
python recovery_cli.py restore backup.zip ~/restore
```

Interactive mode

```bash
python recovery_cli.py interactive
```

---

# 📊 Technologies

- Python
- psutil
- watchdog
- threading
- logging
- zipfile
- pathlib
- argparse

---

# 💡 Engineering Concepts Demonstrated

- Modular Software Architecture
- Event-Driven Programming
- Background Daemons
- Concurrent Processing
- Filesystem Monitoring
- Logging & Observability
- Configuration Management
- CLI Development
- Automated Scheduling
- Fault Tolerance

---

# 🚀 Future Improvements

- Email notifications
- Cloud backup support
- Incremental backups
- Web dashboard
- Backup encryption
- Docker deployment
- GUI interface

---

# 📜 License

MIT License
