from cryptography.fernet import Fernet

from app.core.config import ENCRYPTION_KEY


if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY is missing from .env")


cipher = Fernet(ENCRYPTION_KEY.encode())


def encrypt(text: str) -> str:
    return cipher.encrypt(text.encode()).decode()


def decrypt(text: str) -> str:
    return cipher.decrypt(text.encode()).decode()