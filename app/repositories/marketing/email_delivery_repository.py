from sqlalchemy.orm import Session

from app.models.marketing.email_delivery import EmailDelivery


class EmailDeliveryRepository:

    def __init__(self, db: Session):
        self.db = db


    def create(
        self,
        delivery: EmailDelivery,
    ):
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)

        return delivery


    def get_by_campaign(
        self,
        campaign_id: int,
    ):
        return (
            self.db.query(EmailDelivery)
            .filter(
                EmailDelivery.campaign_id == campaign_id
            )
            .all()
        )


    def get_pending(
        self,
    ):
        return (
            self.db.query(EmailDelivery)
            .filter(
                EmailDelivery.status == "PENDING"
            )
            .all()
        )


    def update_status(
        self,
        delivery: EmailDelivery,
        status,
        error_message=None,
    ):
        delivery.status = status
        delivery.error_message = error_message

        self.db.commit()
        self.db.refresh(delivery)

        return delivery
