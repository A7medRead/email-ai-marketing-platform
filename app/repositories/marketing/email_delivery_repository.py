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


    def search_by_campaign(
        self,
        campaign_id: int,
        search: str | None = None,
        status: str | None = None,
        page: int = 1,
        limit: int = 25,
    ):
        query = (
            self.db.query(EmailDelivery)
            .filter(
                EmailDelivery.campaign_id == campaign_id
            )
        )

        if search:
            query = query.filter(
                EmailDelivery.recipient_email.ilike(
                    f"%{search}%"
                )
            )

        if status:
            query = query.filter(
                EmailDelivery.status == status
            )

        total = query.count()

        offset = (page - 1) * limit

        items = (
            query
            .order_by(EmailDelivery.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "items": items,
            "total": total,
        }


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
