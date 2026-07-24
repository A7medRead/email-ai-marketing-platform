from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


NameField = Annotated[
    str,
    Field(
        min_length=2,
        max_length=255,
    ),
]

DescriptionField = Annotated[
    str,
    Field(
        min_length=2,
        max_length=1000,
    ),
]


class ContactListCreate(BaseModel):
    name: NameField
    description: DescriptionField | None = None


class ContactListUpdate(BaseModel):
    name: NameField
    description: DescriptionField | None = None


class ContactListResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    contacts_count: int = 0

    model_config = ConfigDict(
        from_attributes=True,
    )
