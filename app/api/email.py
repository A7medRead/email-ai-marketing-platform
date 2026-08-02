from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User

from app.schemas.email_schema import (
    EmailRequest,
    EditEmailRequest,
    EmailResponse,
    EmailHistoryResponse,
    EmailHistoryListResponse,
    SendEmailRequest,
)

from app.services.claude_service import (
    generate_email,
    create_email_content,
    edit_email_content,
)

from app.services.email_sender import send_email
from app.models.marketing.sender_account import SenderAccount
from app.core.encryption import decrypt

from app.repositories.email_repository import (
    get_all_emails,
    get_total_emails,
    get_email_by_id,
    delete_email_by_id,
    update_email,
)

router = APIRouter(
    prefix="/email",
    tags=["Email"],
)


@router.post(
    "/generate",
    response_model=EmailResponse,
)
def create_email(
    request: EmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return generate_email(
        db=db,
        user_id=current_user.id,
        data=request,
    )


@router.post(
    "/edit",
    response_model=EmailResponse,
)
def edit_email_endpoint(
    request: EditEmailRequest,
    current_user: User = Depends(get_current_user),
):
    return edit_email_content(request)




@router.get(
    "/history",
    response_model=EmailHistoryListResponse,
)
def email_history(
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit

    emails = get_all_emails(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    total = get_total_emails(
        db=db,
        user_id=current_user.id,
    )

    pages = (total + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
        "items": emails,
    }


@router.get(
    "/{email_id}",
    response_model=EmailHistoryResponse,
)
def get_email(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = get_email_by_id(db, email_id)

    if email is None or email.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    return email


@router.put(
    "/{email_id}",
    response_model=EmailHistoryResponse,
)
def update_email_endpoint(
    email_id: int,
    request: EmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = get_email_by_id(db, email_id)

    if email is None or email.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    result = create_email_content(request, action=request.action)

    updated_email = update_email(
        db=db,
        email=email,
        purpose=request.purpose,
        description=request.description,
        tone=request.tone,
        language=request.language,
        subject=result["subject"],
        body=result["body"],
    )

    return updated_email


@router.delete("/{email_id}")
def delete_email(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = get_email_by_id(db, email_id)

    if email is None or email.user_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    delete_email_by_id(
        db=db,
        email_id=email_id,
    )

    return {
        "message": "Email deleted successfully",
    }


# ==========================
# Send Email
# ==========================

from fastapi import Form, UploadFile, File
from app.services.marketing.sender_account_service import send_test_email

@router.post("/send")
async def send_email_endpoint(
    sender_account_id: int = Form(...),
    to_email: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    attachment: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    account = (
        db.query(SenderAccount)
        .filter(
            SenderAccount.id == sender_account_id,
            SenderAccount.user_id == current_user.id,
        )
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Sender account not found",
        )


    await send_email(
        to_email=to_email,
        subject=subject,
        body=body,
        attachment=attachment,
        sender_email=account.email,
        sender_password=decrypt(account.encrypted_password),
    )


    return {
        "message": "Email sent successfully"
    }
