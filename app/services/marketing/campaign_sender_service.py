from datetime import datetime

from sqlalchemy.orm import Session

from app.models.marketing.email_delivery import (
    EmailDeliveryStatus,
)

from app.models.marketing.sender_account import (
    SenderAccount,
)

from app.repositories.marketing.email_delivery_repository import (
    EmailDeliveryRepository,
)

from app.services.marketing.smtp_service import (
    send_test_email,
)



class CampaignSenderService:


    def __init__(
        self,
        db: Session,
    ):

        self.db = db

        self.delivery_repository = EmailDeliveryRepository(
            db
        )



    def send_campaign(
        self,
        campaign_id: int,
    ):

        deliveries = (
            self.delivery_repository.get_by_campaign(
                campaign_id
            )
        )


        results = {
            "sent": 0,
            "failed": 0,
        }


        for delivery in deliveries:


            if delivery.status != EmailDeliveryStatus.PENDING:
                continue



            sender_account = (
                self.db.query(SenderAccount)
                .filter(
                    SenderAccount.id
                    == delivery.sender_account_id
                )
                .first()
            )


            if not sender_account:

                self.delivery_repository.update_status(
                    delivery,
                    EmailDeliveryStatus.FAILED,
                    "Sender account not found.",
                )

                results["failed"] += 1

                continue



            success, message = send_test_email(
                sender_email=sender_account.email,
                encrypted_password=sender_account.encrypted_password,
                recipient_email=delivery.recipient_email,
            )



            if success:

                delivery.status = EmailDeliveryStatus.SENT
                delivery.sent_at = datetime.utcnow()

                results["sent"] += 1


            else:

                delivery.status = EmailDeliveryStatus.FAILED
                delivery.error_message = message

                results["failed"] += 1



            self.db.commit()



        return results
