from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.marketing.email_delivery import (
    EmailDelivery,
    EmailDeliveryStatus,
)


class CampaignAnalyticsService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db


    def get_campaign_analytics(
        self,
        campaign_id: int,
    ):

        deliveries = (
            self.db.query(EmailDelivery)
            .filter(
                EmailDelivery.campaign_id == campaign_id
            )
            .all()
        )


        result = {
            "campaign_id": campaign_id,
            "total": len(deliveries),
            "pending": 0,
            "queued": 0,
            "sent": 0,
            "failed": 0,
            "opened": 0,
            "clicked": 0,
            "bounced": 0,
        }


        for delivery in deliveries:

            if delivery.status == EmailDeliveryStatus.PENDING:
                result["pending"] += 1

            elif delivery.status == EmailDeliveryStatus.QUEUED:
                result["queued"] += 1

            elif delivery.status == EmailDeliveryStatus.FAILED:
                result["failed"] += 1

            elif delivery.status == EmailDeliveryStatus.BOUNCED:
                result["bounced"] += 1


            if delivery.sent_at:
                result["sent"] += 1

            if delivery.opened_at:
                result["opened"] += 1

            if delivery.clicked_at:
                result["clicked"] += 1


        return result
