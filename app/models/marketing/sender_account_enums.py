from enum import Enum


class SenderAccountStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    DISABLED = "disabled"
