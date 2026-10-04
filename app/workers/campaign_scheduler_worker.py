import fcntl
import logging
import os
import threading

from app.workers.campaign_scheduler import start_scheduler


logging.basicConfig(level=logging.INFO)
lock_path = os.getenv("SCHEDULER_LOCK_FILE", "/scheduler-lock/scheduler.lock")
os.makedirs(os.path.dirname(lock_path), exist_ok=True)
with open(lock_path, "w") as lock_file:
    logging.info("Waiting for the campaign scheduler lock")
    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
    logging.info("Campaign scheduler lock acquired")
    start_scheduler()
    threading.Event().wait()
