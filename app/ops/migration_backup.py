import logging
from pathlib import Path

from app.ops.sqlite_backup import create_backup


path = create_backup(Path("/app/emails.db"), Path("/backups"))
if path:
    logging.info("Created pre-migration database backup: %s", path)
