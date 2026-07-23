from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base
from app.models.marketing.campaign_enums import CampaignStatus


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sender_account_id = Column(
        Integer,
        ForeignKey("sender_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )

    template_id = Column(
        Integer,
        ForeignKey("templates.id", ondelete="SET NULL"),
        nullable=True,
    )

    contact_list_id = Column(
        Integer,
        ForeignKey("contact_lists.id", ondelete="SET NULL"),
        nullable=True,
    )

    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    status = Column(
        Enum(CampaignStatus),
        nullable=False,
        default=CampaignStatus.DRAFT,
    )

    scheduled_at = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User")
    sender_account = relationship("SenderAccount")
    template = relationship("Template")
    contact_list = relationship("ContactList")
