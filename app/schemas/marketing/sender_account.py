from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.marketing.sender_account_enums import SenderAccountStatus


class SenderAccountBase(BaseModel):
    email: EmailStr
    display_name: str
    smtp_password: str


class SenderAccountCreate(SenderAccountBase):
    pass


class SenderAccountUpdate(BaseModel):
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    smtp_password: Optional[str] = None
    status: Optional[SenderAccountStatus] = None


class SenderAccountResponse(BaseModel):

    id: int
    user_id: int

    email: EmailStr

    name: str
    provider: str

    status: SenderAccountStatus

    verified: bool

    daily_limit: int
    hourly_limit: int

    daily_sent: int
    hourly_sent: int

    priority: int

    last_error: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


    class Config:
        from_attributes = True


class TestEmailRequest(BaseModel):
    recipient_email: EmailStr