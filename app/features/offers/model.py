from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.features.offers.enums import VariantContentType
from app.infrastructure.database import Base


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # Nullable for backward compatibility: pre-Responder offers are backfilled by migration.
    responder_id = Column(Integer, ForeignKey("responders.id", ondelete="RESTRICT"), nullable=True, index=True)
    name = Column(String(160), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    discount = Column(String(80), nullable=True)
    coupon_code = Column(String(80), nullable=True)
    starts_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    cta_label = Column(String(80), nullable=True)
    cta_url = Column(String(2048), nullable=True)
    affiliate_url = Column(String(2048), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User")
    responder = relationship("Responder", back_populates="offers")
    variants = relationship("OfferVariant", back_populates="offer", cascade="all, delete-orphan")


class OfferVariant(Base):
    __tablename__ = "offer_variants"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey("offers.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(160), nullable=False)
    content_type = Column(
        Enum(VariantContentType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    from_name = Column(String(255), nullable=True)
    subject = Column(String(255), nullable=False)
    body_html = Column(Text, nullable=True)
    body_text = Column(Text, nullable=True)
    image_url = Column(String(2048), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    offer = relationship("Offer", back_populates="variants")
