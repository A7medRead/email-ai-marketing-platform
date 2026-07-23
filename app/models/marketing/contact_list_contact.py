from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
)

from app.database.database import Base


class ContactListContact(Base):
    __tablename__ = "contact_list_contacts"

    contact_list_id = Column(
        Integer,
        ForeignKey(
            "contact_lists.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    contact_id = Column(
        Integer,
        ForeignKey(
            "contacts.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
