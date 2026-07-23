from enum import Enum


class ContactStatus(str, Enum):
    ACTIVE = "active"
    UNSUBSCRIBED = "unsubscribed"
    BOUNCED = "bounced"
    BLOCKED = "blocked"
