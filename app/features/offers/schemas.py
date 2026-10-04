from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class OfferFields(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=10000)
    discount: str | None = Field(default=None, max_length=80)
    coupon_code: str | None = Field(default=None, max_length=80)
    starts_at: datetime | None = None
    expires_at: datetime | None = None
    cta_label: str | None = Field(default=None, max_length=80)
    cta_url: HttpUrl | None = None

    @model_validator(mode="after")
    def dates_are_ordered(self):
        if self.starts_at and self.expires_at and self.expires_at <= self.starts_at:
            raise ValueError("Offer expiry must be after its start date.")
        return self


class OfferCreate(OfferFields):
    pass


class OfferUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=10000)
    discount: str | None = Field(default=None, max_length=80)
    coupon_code: str | None = Field(default=None, max_length=80)
    starts_at: datetime | None = None
    expires_at: datetime | None = None
    cta_label: str | None = Field(default=None, max_length=80)
    cta_url: HttpUrl | None = None

    @model_validator(mode="after")
    def dates_are_ordered(self):
        if self.starts_at and self.expires_at and self.expires_at <= self.starts_at:
            raise ValueError("Offer expiry must be after its start date.")
        return self


class OfferResponse(OfferFields):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
