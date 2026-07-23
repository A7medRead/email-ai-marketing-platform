from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String,
        nullable=False,
    )

    username = Column(
        String,
        unique=True,
        nullable=True,
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )

    password = Column(
        String,
        nullable=False,
    )

    avatar = Column(
        String,
        nullable=True,
    )

    phone = Column(
        String,
        nullable=True,
    )

    country = Column(
        String,
        nullable=True,
    )

    city = Column(
        String,
        nullable=True,
    )

    timezone = Column(
        String,
        default="UTC",
    )

    preferred_language = Column(
        String,
        default="English",
    )

    preferred_tone = Column(
        String,
        default="Professional",
    )

    preferred_length = Column(
        String,
        default="Medium",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    last_login = Column(
        DateTime,
        nullable=True,
    )

    emails = relationship(
        "Email",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    templates = relationship(
        "Template",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    sender_accounts = relationship(
        "SenderAccount",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    contacts = relationship(
        "Contact",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    contact_lists = relationship(
        "ContactList",
        back_populates="user",
        cascade="all, delete-orphan",
    )
