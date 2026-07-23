from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base
from app.models.marketing.sender_account_enums import SenderAccountStatus


class SenderAccount(Base):

    __tablename__ = "sender_accounts"


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


    email = Column(
        String(255),
        nullable=False,
        index=True,
    )


    name = Column(
        String(255),
        nullable=False,
    )


    provider = Column(
        String(50),
        nullable=False,
        default="gmail",
    )


    encrypted_password = Column(
        String(500),
        nullable=False,
    )


    status = Column(
        Enum(SenderAccountStatus),
        nullable=False,
        default=SenderAccountStatus.PENDING,
    )


    verified = Column(
        Boolean,
        default=False,
        nullable=False,
    )


    daily_limit = Column(
        Integer,
        default=500,
        nullable=False,
    )


    hourly_limit = Column(
        Integer,
        default=100,
        nullable=False,
    )


    daily_sent = Column(
        Integer,
        default=0,
        nullable=False,
    )


    hourly_sent = Column(
        Integer,
        default=0,
        nullable=False,
    )


    priority = Column(
        Integer,
        default=1,
        nullable=False,
    )


    last_error = Column(
        String(500),
        nullable=True,
    )


    last_tested_at = Column(
        DateTime,
        nullable=True,
    )


    last_used_at = Column(
        DateTime,
        nullable=True,
    )


    created_at = Column(
        DateTime,
        server_default=func.now(),
    )


    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )


    user = relationship(
        "User",
        back_populates="sender_accounts",
    )

campaigns = relationship(
    "Campaign",
    back_populates="sender_account",
)
