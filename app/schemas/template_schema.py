from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


NameField = Annotated[
    str,
    Field(
        min_length=3,
        max_length=100,
    ),
]

PurposeField = Annotated[
    str,
    Field(
        min_length=5,
        max_length=255,
    ),
]

DescriptionField = Annotated[
    str,
    Field(
        min_length=5,
        max_length=1000,
    ),
]

ToneField = Annotated[
    str,
    Field(
        min_length=3,
        max_length=50,
    ),
]

LanguageField = Annotated[
    str,
    Field(
        min_length=2,
        max_length=50,
    ),
]


class TemplateCreate(BaseModel):
    name: NameField
    purpose: PurposeField
    description: DescriptionField
    tone: ToneField
    language: LanguageField


class TemplateUpdate(BaseModel):
    name: NameField
    purpose: PurposeField
    description: DescriptionField
    tone: ToneField
    language: LanguageField


class TemplateResponse(BaseModel):
    id: int
    name: str
    purpose: str
    description: str
    tone: str
    language: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)