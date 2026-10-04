import logging
import os
import time
from pathlib import Path

from app.ops.sqlite_backup import create_backup


logging.basicConfig(level=logging.INFO)
interval = max(1, int(os.getenv("BACKUP_INTERVAL_HOURS", "24"))) * 3600

while True:
    next_interval = interval
    try:
        path = create_backup(
            Path(os.getenv("DATABASE_FILE", "/app/emails.db")),
            Path(os.getenv("BACKUP_DIR", "/backups")),
        )
        if path:
            logging.info("Created verified SQLite backup: %s", path)
    except Exception:
        logging.exception("SQLite backup failed")
        next_interval = min(interval, 3600)
    time.sleep(next_interval)
