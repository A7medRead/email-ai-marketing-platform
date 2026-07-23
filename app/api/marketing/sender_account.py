from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

from app.repositories.marketing.sender_account_repository import (
    SenderAccountRepository,
)

from app.schemas.marketing.sender_account import (
    SenderAccountCreate,
    SenderAccountResponse,
    SenderAccountUpdate,
    TestEmailRequest,
)

from app.services.marketing.sender_account_service import (
    SenderAccountService,
)


router = APIRouter(
    prefix="/sender-accounts",
    tags=["Sender Accounts"],
)


@router.post(
    "/",
    response_model=SenderAccountResponse,
)
def create_sender_account(
    data: SenderAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = SenderAccountService(db)

    return service.create_sender_account(
        user_id=current_user.id,
        data=data,
    )


@router.get(
    "/",
    response_model=list[SenderAccountResponse],
)
def get_sender_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = SenderAccountService(db)

    return service.get_sender_accounts(
        current_user.id
    )


@router.put(
    "/{sender_account_id}",
    response_model=SenderAccountResponse,
)
def update_sender_account(
    sender_account_id: int,
    data: SenderAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = SenderAccountService(db)

    account = service.get_sender_account(
        sender_account_id,
        current_user.id,
    )

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Sender account not found.",
        )

    return service.update_sender_account(
        sender_account_id,
        current_user.id,
        data,
    )


@router.delete(
    "/{sender_account_id}",
)
def delete_sender_account(
    sender_account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = SenderAccountService(db)

    result = service.delete_sender_account(
        sender_account_id,
        current_user.id,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Sender account not found.",
        )

    return {
        "message": "Sender account deleted successfully."
    }


@router.post(
    "/{sender_account_id}/verify",
    response_model=SenderAccountResponse,
)
def verify_sender_account(
    sender_account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = SenderAccountService(db)

    result = service.verify_sender_account(
        sender_account_id,
        current_user.id,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Sender account not found.",
        )

    return result


@router.post(
    "/{sender_account_id}/send-test",
)
def send_test_email(
    sender_account_id: int,
    data: TestEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = SenderAccountService(db)

    result = service.send_test_email(
        sender_account_id,
        current_user.id,
        data.recipient_email,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Sender account not found.",
        )

    return {
        "message": result[1] if isinstance(result, tuple) else result
    }