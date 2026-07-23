from sqlalchemy.orm import Session

from app.models.marketing.contact import Contact
from app.models.marketing.contact_list import ContactList


def create_contact_list(
    db: Session,
    user_id: int,
    name: str,
    description: str | None,
):
    contact_list = ContactList(
        user_id=user_id,
        name=name,
        description=description,
    )

    db.add(contact_list)
    db.commit()
    db.refresh(contact_list)

    return contact_list


def get_contact_list_by_id(
    db: Session,
    contact_list_id: int,
    user_id: int,
):
    return (
        db.query(ContactList)
        .filter(
            ContactList.id == contact_list_id,
            ContactList.user_id == user_id,
        )
        .first()
    )


def get_contact_list_by_name(
    db: Session,
    user_id: int,
    name: str,
):
    return (
        db.query(ContactList)
        .filter(
            ContactList.user_id == user_id,
            ContactList.name == name,
        )
        .first()
    )


def get_all_contact_lists(
    db: Session,
    user_id: int,
):
    return (
        db.query(ContactList)
        .filter(ContactList.user_id == user_id)
        .order_by(ContactList.id.desc())
        .all()
    )


def update_contact_list(
    db: Session,
    contact_list: ContactList,
):
    db.commit()
    db.refresh(contact_list)
    return contact_list


def delete_contact_list(
    db: Session,
    contact_list: ContactList,
):
    db.delete(contact_list)
    db.commit()


def add_contact_to_list(
    db: Session,
    contact_list: ContactList,
    contact: Contact,
):
    if contact not in contact_list.contacts:
        contact_list.contacts.append(contact)
        db.commit()
        db.refresh(contact_list)

    return contact_list


def remove_contact_from_list(
    db: Session,
    contact_list: ContactList,
    contact: Contact,
):
    if contact in contact_list.contacts:
        contact_list.contacts.remove(contact)
        db.commit()
        db.refresh(contact_list)

    return contact_list


def get_contacts_in_list(
    contact_list: ContactList,
):
    return contact_list.contacts
