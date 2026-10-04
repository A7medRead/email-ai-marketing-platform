from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.features.campaigns.enums import CampaignStatus


class CampaignBase(BaseModel):

    sender_account_id: int
    contact_list_id: int
    template_id: Optional[int] = None
    offer_id: Optional[int] = None
    variant_id: Optional[int] = None

    name: str
    from_name: Optional[str] = None
    subject: str
    body: str
    scheduled_at: Optional[datetime] = None


class CampaignCreate(CampaignBase):
    pass



class CampaignUpdate(BaseModel):

    name: Optional[str] = None
    from_name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    status: Optional[CampaignStatus] = None
    # Manual Variant selection; explicit null clears it (back to legacy behavior).
    variant_id: Optional[int] = None



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
