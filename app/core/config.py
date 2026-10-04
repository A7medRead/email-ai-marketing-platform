import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

# AI
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = os.getenv("MODEL")

# Authentication
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
)

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is missing from .env")

# Encryption
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# Tracking
TRACKING_URL = os.getenv("TRACKING_URL", "http://127.0.0.1:8000")

# Transactional mail used for account recovery.
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
FRONTEND_URL = os.getenv("FRONTEND_URL", TRACKING_URL).rstrip("/")
