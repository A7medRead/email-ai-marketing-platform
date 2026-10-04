from sqlalchemy.orm import Session

from app.features.sender_accounts.model import SenderAccount
from app.features.sender_accounts.enums import SenderAccountStatus

from app.features.sender_accounts.repository import (
    SenderAccountRepository,
)

from app.features.sender_accounts.schemas import (
    SenderAccountCreate,
    SenderAccountUpdate,
)

from app.infrastructure.email.smtp import (
    verify_gmail_account,
    send_test_email as smtp_send_test_email,
)

from app.core.encryption import encrypt



class SenderAccountService:

    def __init__(self, db: Session):
        self.repository = SenderAccountRepository(db)



    def create_sender_account(
        self,
        user_id: int,
        data: SenderAccountCreate,
    ):

        account = SenderAccount(
            user_id=user_id,
            email=data.email,
            name=data.display_name,
            provider="gmail",

            # مهم: تخزين مشفر
            encrypted_password=encrypt(
                data.smtp_password
            ),

            status=SenderAccountStatus.PENDING,
            verified=False,
            batch_size=data.batch_size,
        )

        return self.repository.create(account)



    def get_sender_accounts(
        self,
        user_id: int,
    ):
        return self.repository.get_all(user_id)



    def get_sender_account(
        self,
        sender_account_id: int,
        user_id: int,
    ):
        return self.repository.get_by_id(
            sender_account_id,
            user_id,
        )



    def update_sender_account(
        self,
        sender_account_id: int,
        user_id: int,
        data: SenderAccountUpdate,
    ):

        update_data = data.model_dump(
            exclude_unset=True
        )


        # batch_size is NOT NULL: an explicit null means "leave unchanged"
        if update_data.get("batch_size") is None:
            update_data.pop("batch_size", None)


        # لو غير الباسورد نشفره قبل الحفظ
        if "smtp_password" in update_data:

            update_data["encrypted_password"] = encrypt(
                update_data.pop("smtp_password")
            )


        return self.repository.update(
            sender_account_id,
            user_id,
            update_data,
        )



    def delete_sender_account(
        self,
        sender_account_id: int,
        user_id: int,
    ):
        return self.repository.delete(
            sender_account_id,
            user_id,
        )



    def verify_sender_account(
        self,
        sender_account_id: int,
        user_id: int,
    ):

        account = self.repository.get_by_id(
            sender_account_id,
            user_id,
        )


        if not account:
            return None



        success, message = verify_gmail_account(
            email=account.email,
            encrypted_password=account.encrypted_password,
        )



        if success:

            account.status = SenderAccountStatus.VERIFIED
            account.verified = True
            account.last_error = None


        else:

            account.status = SenderAccountStatus.FAILED
            account.verified = False
            account.last_error = message



        self.repository.db.commit()
        self.repository.db.refresh(account)


        return account




    def send_test_email(
        self,
        sender_account_id: int,
        user_id: int,
        recipient_email: str,
    ):

        account = self.repository.get_by_id(
            sender_account_id,
            user_id,
        )


        if not account:
            return False



        return smtp_send_test_email(
            sender_email=account.email,
        encrypted_password=account.encrypted_password,
        recipient_email=recipient_email,
)





# ==========================
# Service functions for API
# ==========================


def create_sender_account(
    db: Session,
    user_id: int,
    data: SenderAccountCreate,
):

    service = SenderAccountService(db)

    return service.create_sender_account(
        user_id=user_id,
        data=data,
    )



def verify_sender_account(
    db: Session,
    sender_account_id: int,
    user_id: int,
):

    service = SenderAccountService(db)

    return service.verify_sender_account(
        sender_account_id=sender_account_id,
        user_id=user_id,
    )



def send_test_email(
    db: Session,
    sender_account_id: int,
    user_id: int,
    recipient_email: str,
):

    service = SenderAccountService(db)

    return service.send_test_email(
        sender_account_id=sender_account_id,
        user_id=user_id,
        recipient_email=recipient_email,
    )