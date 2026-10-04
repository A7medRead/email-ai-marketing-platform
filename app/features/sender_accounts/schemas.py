from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.features.sender_accounts.enums import SenderAccountStatus
from app.features.sender_accounts.model import DEFAULT_BATCH_SIZE

MAX_BATCH_SIZE = 500


class SenderAccountBase(BaseModel):
    email: EmailStr
    display_name: str
    smtp_password: str


class SenderAccountCreate(SenderAccountBase):
    batch_size: int = Field(default=DEFAULT_BATCH_SIZE, ge=1, le=MAX_BATCH_SIZE)


class SenderAccountUpdate(BaseModel):
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    smtp_password: Optional[str] = None
    status: Optional[SenderAccountStatus] = None
    batch_size: Optional[int] = Field(default=None, ge=1, le=MAX_BATCH_SIZE)


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

    batch_size: int

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