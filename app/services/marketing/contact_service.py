from sqlalchemy.orm import Session

from app.models.marketing.contact import Contact
from app.models.marketing.contact_enums import ContactStatus
from app.repositories.marketing import contact_repository
from app.schemas.marketing.contact import (
    ContactCreate,
    ContactUpdate,
)


def create_contact(
    db: Session,
    user_id: int,
    data: ContactCreate,
):
    existing = contact_repository.get_contact_by_email(
        db=db,
        user_id=user_id,
        email=data.email,
    )

    if existing:
        raise ValueError(
            "Contact already exists."
        )

    contact = Contact(
        user_id=user_id,
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        company=data.company,
        status=ContactStatus.ACTIVE,
    )

    return contact_repository.create_contact(
        db=db,
        contact=contact,
    )


def get_contacts(
    db: Session,
    user_id: int,
):
    return contact_repository.get_all_contacts(
        db=db,
        user_id=user_id,
    )


def update_contact(
    db: Session,
    contact: Contact,
    data: ContactUpdate,
):
    update_data = data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            contact,
            key,
            value,
        )

    return contact_repository.update_contact(
        db=db,
        contact=contact,
    )


def delete_contact(
    db: Session,
    contact: Contact,
):
    return contact_repository.delete_contact(
        db=db,
        contact=contact,
    )
