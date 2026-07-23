from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
)

from sqlalchemy.orm import relationship

from app.database.database import Base

from enum import Enum as PyEnum


class EmailDeliveryStatus(str, PyEnum):
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"



class EmailDelivery(Base):

    __tablename__ = "email_deliveries"


    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )


    campaign_id = Column(
        Integer,
        ForeignKey(
            "campaigns.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


    contact_id = Column(
        Integer,
        ForeignKey(
            "contacts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


    sender_account_id = Column(
        Integer,
        ForeignKey(
            "sender_accounts.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )


    recipient_email = Column(
        String(255),
        nullable=False,
    )


    status = Column(
        Enum(EmailDeliveryStatus),
        nullable=False,
        default=EmailDeliveryStatus.PENDING,
    )


    error_message = Column(
        String(500),
        nullable=True,
    )


    sent_at = Column(
        DateTime,
        nullable=True,
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


    campaign = relationship(
        "Campaign",
    )


    contact = relationship(
        "Contact",
    )


    sender_account = relationship(
        "SenderAccount",
    )
