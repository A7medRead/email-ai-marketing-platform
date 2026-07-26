from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

import csv
import io

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.marketing.sender_account import SenderAccount

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


@router.get("/export")
def export_sender_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    import csv
    import io

    from fastapi.responses import StreamingResponse


    accounts = (
        db.query(SenderAccount)
        .filter(
            SenderAccount.user_id == current_user.id
        )
        .all()
    )


    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "email",
        "name",
        "provider",
        "status",
        "verified",
    ])


    for account in accounts:

        writer.writerow([
            account.email,
            account.name,
            account.provider,
            account.status.value,
            account.verified,
        ])


    output.seek(0)


    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=sender_accounts.csv"
        },
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
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    query = (
        db.query(SenderAccount)
        .filter(
            SenderAccount.user_id == current_user.id
        )
    )


    if search:
        query = query.filter(
            SenderAccount.email.ilike(f"%{search}%")
            |
            SenderAccount.name.ilike(f"%{search}%")
            |
            SenderAccount.provider.ilike(f"%{search}%")
        )


    if status:
        query = query.filter(
            SenderAccount.status == status
        )


    return (
        query
        .order_by(SenderAccount.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
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

@router.post("/import")
def import_sender_accounts(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    from app.core.encryption import encrypt
    from app.models.marketing.sender_account import SenderAccount
    from app.models.marketing.sender_account_enums import SenderAccountStatus


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


        exists = (
            db.query(SenderAccount)
            .filter(
                SenderAccount.user_id == current_user.id,
                SenderAccount.email == email,
            )
            .first()
        )


        if exists:
            skipped += 1
            continue


        account = SenderAccount(
            user_id=current_user.id,
            email=email,
            name=row.get("name") or email,
            provider=row.get("provider") or "gmail",
            encrypted_password=encrypt(
                row.get("password") or ""
            ),
            status=SenderAccountStatus.PENDING,
            verified=False,
        )


        db.add(account)

        imported += 1


    db.commit()


    return {
        "imported": imported,
        "skipped": skipped,
    }