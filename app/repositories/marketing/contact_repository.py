from sqlalchemy.orm import Session

from app.models.marketing.contact import Contact


def create_contact(
    db: Session,
    contact: Contact,
):
    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact



def get_contact_by_id(
    db: Session,
    contact_id: int,
    user_id: int,
):
    return (
        db.query(Contact)
        .filter(
            Contact.id == contact_id,
            Contact.user_id == user_id,
        )
        .first()
    )



def get_contact_by_email(
    db: Session,
    user_id: int,
    email: str,
):
    return (
        db.query(Contact)
        .filter(
            Contact.user_id == user_id,
            Contact.email == email,
        )
        .first()
    )



def get_all_contacts(
    db: Session,
    user_id: int,
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
):

    query = (
        db.query(Contact)
        .filter(
            Contact.user_id == user_id
        )
    )


    if search:
        query = query.filter(
            Contact.first_name.ilike(f"%{search}%")
            |
            Contact.last_name.ilike(f"%{search}%")
            |
            Contact.email.ilike(f"%{search}%")
        )


    return (
        query
        .order_by(Contact.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )



def update_contact(
    db: Session,
    contact: Contact,
):

    db.commit()
    db.refresh(contact)

    return contact



def delete_contact(
    db: Session,
    contact: Contact,
):

    db.delete(contact)
    db.commit()

    return True