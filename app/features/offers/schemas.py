from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.features.offers.enums import VariantContentType


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
    affiliate_url: HttpUrl | None = None

    @model_validator(mode="after")
    def dates_are_ordered(self):
        if self.starts_at and self.expires_at and self.expires_at <= self.starts_at:
            raise ValueError("Offer expiry must be after its start date.")
        return self


class OfferCreate(OfferFields):
    responder_id: int | None = None


class OfferUpdate(BaseModel):
    responder_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=160)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=10000)
    discount: str | None = Field(default=None, max_length=80)
    coupon_code: str | None = Field(default=None, max_length=80)
    starts_at: datetime | None = None
    expires_at: datetime | None = None
    cta_label: str | None = Field(default=None, max_length=80)
    cta_url: HttpUrl | None = None
    affiliate_url: HttpUrl | None = None

    @model_validator(mode="after")
    def dates_are_ordered(self):
        if self.starts_at and self.expires_at and self.expires_at <= self.starts_at:
            raise ValueError("Offer expiry must be after its start date.")
        return self


class OfferResponse(OfferFields):
    model_config = ConfigDict(from_attributes=True)

    id: int
    responder_id: int | None = None
    created_at: datetime
    updated_at: datetime


class OfferVariantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    content_type: VariantContentType
    from_name: str | None = Field(default=None, max_length=255)
    subject: str = Field(min_length=1, max_length=255)
    body_html: str | None = None
    body_text: str | None = None
    image_url: HttpUrl | None = None
    is_active: bool = True

    @model_validator(mode="after")
    def content_matches_type(self):
        required = {
            VariantContentType.TEXT: ("body_text",),
            VariantContentType.IMAGE: ("image_url",),
            VariantContentType.HTML: ("body_html",),
        }
        # Whitespace-only text/HTML is not content.
        has = {
            "body_text": bool(self.body_text and self.body_text.strip()),
            "body_html": bool(self.body_html and self.body_html.strip()),
            "image_url": bool(self.image_url),
        }
        if self.content_type == VariantContentType.TEXT_IMAGE:
            # Text only, image only, or both; but not empty.
            if not (has["body_text"] or has["image_url"]):
                raise ValueError("TEXT_IMAGE variants require body_text or image_url.")
            return self
        missing = [f for f in required[self.content_type] if not has[f]]
        if missing:
            raise ValueError(f"{self.content_type.value} variants require: {', '.join(missing)}.")
        return self


class OfferVariantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    offer_id: int
    name: str
    content_type: VariantContentType
    from_name: str | None = None
    subject: str
    body_html: str | None = None
    body_text: str | None = None
    image_url: str | None = None
    is_active: bool
    created_at: datetime
