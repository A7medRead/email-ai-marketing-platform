from enum import Enum


class CampaignStatus(str, Enum):

    DRAFT = "draft"
    PREPARED = "prepared"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"
