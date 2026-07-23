from enum import Enum


class CampaignStatus(str, Enum):

    DRAFT = "draft"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"
