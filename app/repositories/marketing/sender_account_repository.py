from sqlalchemy.orm import Session

from app.models.marketing.sender_account import SenderAccount


class SenderAccountRepository:

    def __init__(self, db: Session):
        self.db = db


    def create(
        self,
        sender_account: SenderAccount,
    ):
        self.db.add(sender_account)
        self.db.commit()
        self.db.refresh(sender_account)

        return sender_account


    def get_all(
        self,
        user_id: int,
    ):
        return (
            self.db.query(SenderAccount)
            .filter(
                SenderAccount.user_id == user_id
            )
            .all()
        )


    def get_by_id(
        self,
        sender_account_id: int,
        user_id: int,
    ):
        return (
            self.db.query(SenderAccount)
            .filter(
                SenderAccount.id == sender_account_id,
                SenderAccount.user_id == user_id,
            )
            .first()
        )


    def update(
        self,
        sender_account_id: int,
        user_id: int,
        data: dict,
    ):
        sender_account = self.get_by_id(
            sender_account_id,
            user_id,
        )

        if not sender_account:
            return None


        for key, value in data.items():
            setattr(
                sender_account,
                key,
                value,
            )


        self.db.commit()
        self.db.refresh(sender_account)

        return sender_account


    def delete(
        self,
        sender_account_id: int,
        user_id: int,
    ):
        sender_account = self.get_by_id(
            sender_account_id,
            user_id,
        )

        if not sender_account:
            return False


        self.db.delete(sender_account)
        self.db.commit()

        return True
