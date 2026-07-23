from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.repositories.marketing import (
    contact_list_repository,
    contact_repository,
)
from app.schemas.marketing.contact import ContactResponse
from app.schemas.marketing.contact_list import (
    ContactListCreate,
    ContactListResponse,
    ContactListUpdate,
)
from app.services.marketing import contact_list_service

router = APIRouter(
    prefix="/contact-lists",
    tags=["Contact Lists"],
)


@router.post(
    "/",
    response_model=ContactListResponse,
)
def create_contact_list(
    data: ContactListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return contact_list_service.create_contact_list(
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
    response_model=list[ContactListResponse],
)
def get_contact_lists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return contact_list_service.get_contact_lists(
        db=db,
        user_id=current_user.id,
    )


@router.put(
    "/{contact_list_id}",
    response_model=ContactListResponse,
)
def update_contact_list(
    contact_list_id: int,
    data: ContactListUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact_list = contact_list_repository.get_contact_list_by_id(
        db=db,
        contact_list_id=contact_list_id,
        user_id=current_user.id,
    )

    if not contact_list:
        raise HTTPException(
            status_code=404,
            detail="Contact list not found.",
        )

    try:
        return contact_list_service.update_contact_list(
            db=db,
            contact_list=contact_list,
            data=data,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.delete(
    "/{contact_list_id}",
)
def delete_contact_list(
    contact_list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact_list = contact_list_repository.get_contact_list_by_id(
        db=db,
        contact_list_id=contact_list_id,
        user_id=current_user.id,
    )

    if not contact_list:
        raise HTTPException(
            status_code=404,
            detail="Contact list not found.",
        )

    contact_list_service.delete_contact_list(
        db=db,
        contact_list=contact_list,
    )

    return {
        "message": "Contact list deleted successfully."
    }


@router.post(
    "/{contact_list_id}/contacts/{contact_id}",
    response_model=ContactListResponse,
)
def add_contact_to_list(
    contact_list_id: int,
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact_list = contact_list_repository.get_contact_list_by_id(
        db=db,
        contact_list_id=contact_list_id,
        user_id=current_user.id,
    )

    if not contact_list:
        raise HTTPException(
            status_code=404,
            detail="Contact list not found.",
        )

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

    return contact_list_service.add_contact_to_list(
        db=db,
        contact_list=contact_list,
        contact=contact,
    )


@router.get(
    "/{contact_list_id}/contacts",
    response_model=list[ContactResponse],
)
def get_contacts_in_list(
    contact_list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact_list = contact_list_repository.get_contact_list_by_id(
        db=db,
        contact_list_id=contact_list_id,
        user_id=current_user.id,
    )

    if not contact_list:
        raise HTTPException(
            status_code=404,
            detail="Contact list not found.",
        )

    return contact_list_service.get_contacts_in_list(
        contact_list=contact_list,
    )


@router.delete(
    "/{contact_list_id}/contacts/{contact_id}",
)
def remove_contact_from_list(
    contact_list_id: int,
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact_list = contact_list_repository.get_contact_list_by_id(
        db=db,
        contact_list_id=contact_list_id,
        user_id=current_user.id,
    )

    if not contact_list:
        raise HTTPException(
            status_code=404,
            detail="Contact list not found.",
        )

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

    contact_list_service.remove_contact_from_list(
        db=db,
        contact_list=contact_list,
        contact=contact,
    )

    return {
        "message": "Contact removed from list successfully."
    }
