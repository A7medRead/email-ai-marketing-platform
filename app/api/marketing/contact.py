from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

import csv
import io

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.models.marketing.contact import Contact
from app.models.marketing.contact_list import ContactList
from app.repositories.marketing import contact_repository
from app.repositories.marketing import contact_list_repository
from app.schemas.marketing.contact import (
    ContactCreate,
    ContactResponse,
    ContactUpdate,
)
from app.services.marketing import contact_service
from app.services.marketing import contact_list_service

router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"],
)


@router.post(
    "/",
    response_model=ContactResponse,
)
def create_contact(
    data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return contact_service.create_contact(
            db=db,
            user_id=current_user.id,
            data=data,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get(
    "/",
    response_model=list[ContactResponse],
)
def get_contacts(
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    status: str | None = None,
    company: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return contact_service.get_contacts(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit,
        search=search,
        status=status,
        company=company,
    )



@router.get("/export")
def export_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    contacts = contact_service.get_contacts(
        db=db,
        user_id=current_user.id,
    )


    output = io.StringIO()

    writer = csv.writer(output)


    writer.writerow([
        "first_name",
        "last_name",
        "email",
        "company",
        "phone",
        "position",
    ])


    for contact in contacts:

        writer.writerow([
            contact.first_name,
            contact.last_name or "",
            contact.email,
            contact.company or "",
            contact.phone or "",
            contact.position or "",
        ])


    from fastapi.responses import StreamingResponse


    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=contacts.csv"
        },
    )



@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = contact_repository.get_contact_by_id(
        db=db,
        contact_id=contact_id,
        user_id=current_user.id,
    )

    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found.",
        )

    return contact

@router.put(
    "/{contact_id}",
    response_model=ContactResponse,
)
def update_contact(
    contact_id: int,
    data: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = contact_repository.get_contact_by_id(
        db=db,
        contact_id=contact_id,
        user_id=current_user.id,
    )

    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found.",
        )

    try:
        return contact_service.update_contact(
            db=db,
            contact=contact,
            data=data,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.delete(
    "/{contact_id}",
)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = contact_repository.get_contact_by_id(
        db=db,
        contact_id=contact_id,
        user_id=current_user.id,
    )

    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found.",
        )

    contact_service.delete_contact(
        db=db,
        contact=contact,
    )

    return {
        "message": "Contact deleted successfully."
    }




@router.post(
    "/bulk-delete",
)
def bulk_delete_contacts(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    ids = data.get("ids", [])

    if not ids:
        raise HTTPException(
            status_code=400,
            detail="No contacts selected.",
        )


    contacts = contact_repository.get_contacts_by_ids(
        db=db,
        user_id=current_user.id,
        ids=ids,
    )


    contact_service.bulk_delete_contacts(
        db=db,
        contacts=contacts,
    )


    return {
        "deleted": len(contacts)
    }


@router.post("/import")
def import_contacts(
    file: UploadFile = File(...),
    contact_list_id: int | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    content = file.file.read().decode("utf-8")

    reader = csv.DictReader(
        io.StringIO(content)
    )

    imported = 0
    skipped = 0


    for row in reader:

        email = row.get("email")

        if not email:
            skipped += 1
            continue


        exists = contact_repository.get_contact_by_email(
            db=db,
            user_id=current_user.id,
            email=email,
        )


        if exists:
            skipped += 1
            continue


        contact = Contact(
            user_id=current_user.id,
            first_name=row.get("first_name") or "",
            last_name=row.get("last_name"),
            email=email,
            company=row.get("company"),
            phone=row.get("phone"),
            position=row.get("position"),
        )


        db.add(contact)
        db.flush()


        if contact_list_id:

            contact_list = contact_list_repository.get_contact_list_by_id(
                db=db,
                contact_list_id=contact_list_id,
                user_id=current_user.id,
            )

            if contact_list:

                contact_list_service.add_contact_to_list(
                    db=db,
                    contact_list=contact_list,
                    contact=contact,
                )


        imported += 1


    db.commit()


    return {
        "imported": imported,
        "skipped": skipped,
    }


