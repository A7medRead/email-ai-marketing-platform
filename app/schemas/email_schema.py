from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EmailRequest(BaseModel):
    purpose: str
    description: str
    tone: str
    language: str


class EmailResponse(BaseModel):
    subject: str
    body: str


class EmailHistoryResponse(BaseModel):
    id: int
    purpose: str
    description: str
    tone: str
    language: str
    subject: str
    body: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    
from typing import List

class EmailHistoryListResponse(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
    items: List[EmailHistoryResponse]


from pydantic import EmailStr


class SendEmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    body: str