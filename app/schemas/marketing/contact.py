from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.marketing.contact_enums import ContactStatus


class ContactBase(BaseModel):

    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    company: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None



class ContactCreate(ContactBase):
    pass



class ContactUpdate(BaseModel):

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    status: Optional[ContactStatus] = None



class ContactResponse(ContactBase):

    id: int
    user_id: int
    status: ContactStatus
    created_at: datetime
    updated_at: Optional[datetime] = None


    class Config:
        from_attributes = True


