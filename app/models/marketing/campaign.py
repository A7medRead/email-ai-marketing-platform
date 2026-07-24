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

from app.database.database import Base
from app.models.marketing.campaign_enums import CampaignStatus


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


    name = Column(
        String(255),
        nullable=False,
    )


    subject = Column(
        String(255),
        nullable=False,
    )


    body = Column(
        Text,
        nullable=False,
    )



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
