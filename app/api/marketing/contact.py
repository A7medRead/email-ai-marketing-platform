from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.repositories.marketing import contact_repository
from app.schemas.marketing.contact import (
    ContactCreate,
    ContactResponse,
    ContactUpdate,
)
from app.services.marketing import contact_service

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return contact_service.get_contacts(
        db=db,
        user_id=current_user.id,
    )


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
