from __future__ import annotations

import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def create_backup(source: Path, destination_dir: Path, keep: int = 14) -> Path | None:
    if not source.exists():
        return None

    destination_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = destination_dir / f"emails-{stamp}.sqlite3"
    fd, temporary_path = tempfile.mkstemp(
        prefix=".emails-backup-", suffix=".sqlite3", dir=destination_dir
    )
    os.close(fd)
    try:
        with sqlite3.connect(f"file:{source.resolve()}?mode=ro", uri=True) as db:
            with sqlite3.connect(temporary_path) as backup:
                db.backup(backup)
        with sqlite3.connect(temporary_path) as backup:
            result = backup.execute("PRAGMA integrity_check").fetchone()
        if not result or result[0] != "ok":
            raise RuntimeError(f"SQLite backup integrity check failed: {result}")
        os.replace(temporary_path, destination)
    except Exception:
        Path(temporary_path).unlink(missing_ok=True)
        raise

    old_backups = sorted(destination_dir.glob("emails-*.sqlite3"), reverse=True)
    for old_backup in old_backups[keep:]:
        old_backup.unlink()
    return destination
