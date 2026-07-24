from sqlalchemy.orm import Session

from app.models.marketing.contact import Contact
from app.models.marketing.contact_list import ContactList
from app.repositories.marketing import contact_list_repository
from app.schemas.marketing.contact_list import (
    ContactListCreate,
    ContactListUpdate,
)


def create_contact_list(
    db: Session,
    user_id: int,
    data: ContactListCreate,
):
    existing = contact_list_repository.get_contact_list_by_name(
        db=db,
        user_id=user_id,
        name=data.name,
    )

    if existing:
        raise ValueError("Contact list name already exists.")

    return contact_list_repository.create_contact_list(
        db=db,
        user_id=user_id,
        name=data.name,
        description=data.description,
    )


def get_contact_lists(
    db: Session,
    user_id: int,
):

    lists = contact_list_repository.get_all_contact_lists(
        db=db,
        user_id=user_id,
    )

    return [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "created_at": item.created_at,
            "contacts_count": len(item.contacts),
        }
        for item in lists
    ]


def update_contact_list(
    db: Session,
    contact_list: ContactList,
    data: ContactListUpdate,
):
    existing = contact_list_repository.get_contact_list_by_name(
        db=db,
        user_id=contact_list.user_id,
        name=data.name,
    )

    if existing and existing.id != contact_list.id:
        raise ValueError("Contact list name already exists.")

    contact_list.name = data.name
    contact_list.description = data.description

    return contact_list_repository.update_contact_list(
        db=db,
        contact_list=contact_list,
    )


def delete_contact_list(
    db: Session,
    contact_list: ContactList,
):
    contact_list_repository.delete_contact_list(
        db=db,
        contact_list=contact_list,
    )


def add_contact_to_list(
    db: Session,
    contact_list: ContactList,
    contact: Contact,
):
    return contact_list_repository.add_contact_to_list(
        db=db,
        contact_list=contact_list,
        contact=contact,
    )


def remove_contact_from_list(
    db: Session,
    contact_list: ContactList,
    contact: Contact,
):
    return contact_list_repository.remove_contact_from_list(
        db=db,
        contact_list=contact_list,
        contact=contact,
    )


def get_contacts_in_list(
    contact_list: ContactList,
):
    return contact_list_repository.get_contacts_in_list(
        contact_list=contact_list,
    )
