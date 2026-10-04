from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResponderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)


class ResponderUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=160)


class ResponderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
