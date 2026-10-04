from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Enum,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.database import Base
from app.features.campaigns.enums import CampaignStatus


class Campaign(Base):

    __tablename__ = "campaigns"


    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )


    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


    sender_account_id = Column(
        Integer,
        ForeignKey(
            "sender_accounts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )


    contact_list_id = Column(
        Integer,
        ForeignKey(
            "contact_lists.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )


    template_id = Column(
        Integer,
        ForeignKey(
            "templates.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    offer_id = Column(
        Integer,
        ForeignKey("offers.id", ondelete="SET NULL"),
        nullable=True,
    )


    # Manually selected Variant (see MAILPILOT_PRODUCT_DIRECTION 13A.10). A referenced Variant/Offer
    # must never be deleted or silently detached: OfferService refuses with 409 (13A.13A). The
    # SET NULL below is NOT the protection - SQLite foreign keys are not enforced at runtime here.
    variant_id = Column(
        Integer,
        ForeignKey("offer_variants.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )


    from_name = Column(
        String(255),
        nullable=True,
    )


    subject = Column(
        String(255),
        nullable=False,
    )


    body = Column(
        Text,
        nullable=False,
    )



    # Variant snapshot taken at /prepare; NULL for legacy (non-Variant) campaigns.
    # Why: what a prepared campaign sends must not change if the Variant is edited afterwards,
    # and sending must never re-read the live Variant (13A.11).
    prepared_subject = Column(String(255), nullable=True)
    prepared_from_name = Column(String(255), nullable=True)
    prepared_body = Column(Text, nullable=True)

    status = Column(
        Enum(CampaignStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=CampaignStatus.DRAFT,
    )


    scheduled_at = Column(
        DateTime,
        nullable=True,
    )


    total_recipients = Column(
        Integer,
        default=0,
        nullable=False,
    )


    sent_count = Column(
        Integer,
        default=0,
        nullable=False,
    )


    failed_count = Column(
        Integer,
        default=0,
        nullable=False,
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )


    user = relationship(
        "User",
        back_populates="campaigns",
    )


    sender_account = relationship(
        "SenderAccount",
    )


    contact_list = relationship(
        "ContactList",
    )


    template = relationship(
        "Template",
    )

    offer = relationship("Offer")

    variant = relationship("OfferVariant")
