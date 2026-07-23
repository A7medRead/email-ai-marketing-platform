from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base
from app.models.marketing.contact_enums import ContactStatus


class Contact(Base):

    __tablename__ = "contacts"


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


    first_name = Column(
        String(100),
        nullable=False,
    )


    last_name = Column(
        String(100),
        nullable=True,
    )


    email = Column(
        String(255),
        nullable=False,
        index=True,
    )


    phone = Column(
        String(50),
        nullable=True,
    )


    company = Column(
        String(255),
        nullable=True,
    )


    position = Column(
        String(255),
        nullable=True,
    )


    status = Column(
        Enum(ContactStatus),
        nullable=False,
        default=ContactStatus.ACTIVE,
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


    user = relationship(
        "User",
        back_populates="contacts",
    )


    lists = relationship(
        "ContactList",
        secondary="contact_list_contacts",
        back_populates="contacts",
    )
