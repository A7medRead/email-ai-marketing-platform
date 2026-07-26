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
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    status: str | None = None,
    company: str | None = None,
):
    return contact_repository.get_all_contacts(
        db=db,
        user_id=user_id,
        page=page,
        limit=limit,
        search=search,
        status=status,
        company=company,
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


def bulk_delete_contacts(
    db: Session,
    contacts: list[Contact],
):

    for contact in contacts:
        db.delete(contact)

    db.commit()

    return {
        "deleted": len(contacts)
    }

