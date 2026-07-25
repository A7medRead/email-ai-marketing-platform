from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    name = Column(
        String,
        nullable=False,
    )

    purpose = Column(
        String,
        nullable=False,
    )

    description = Column(
        String,
        nullable=False,
    )

    tone = Column(
        String,
        nullable=False,
    )

    language = Column(
        String,
        nullable=False,
    )


    subject = Column(
        String,
        nullable=False,
    )


    body = Column(
        String,
        nullable=False,
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    user = relationship(
        "User",
        back_populates="templates",
    )