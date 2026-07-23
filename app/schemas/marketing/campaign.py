from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.marketing.campaign_enums import CampaignStatus


class CampaignBase(BaseModel):
    name: str
    subject: str
    description: Optional[str] = None
    sender_account_id: Optional[int] = None
    template_id: Optional[int] = None
    contact_list_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    sender_account_id: Optional[int] = None
    template_id: Optional[int] = None
    contact_list_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[CampaignStatus] = None


class CampaignResponse(CampaignBase):
    id: int
    user_id: int
    status: CampaignStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
