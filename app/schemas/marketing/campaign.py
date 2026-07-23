from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.marketing.campaign_enums import CampaignStatus


class CampaignBase(BaseModel):

    sender_account_id: int
    contact_list_id: int

    name: str
    subject: str
    body: str
    scheduled_at: Optional[datetime] = None


class CampaignCreate(CampaignBase):
    pass



class CampaignUpdate(BaseModel):

    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    status: Optional[CampaignStatus] = None



class CampaignResponse(CampaignBase):

    id: int

    status: CampaignStatus

    total_recipients: int
    sent_count: int
    failed_count: int

    scheduled_at: Optional[datetime] = None

    created_at: datetime
    updated_at: Optional[datetime] = None


    class Config:
        from_attributes = True
