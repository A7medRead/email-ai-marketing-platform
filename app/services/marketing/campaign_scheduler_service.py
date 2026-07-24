from datetime import datetime

from sqlalchemy.orm import Session

from app.models.marketing.campaign import Campaign
from app.models.marketing.campaign_enums import CampaignStatus

from app.services.marketing.email_delivery_service import EmailDeliveryService
from app.services.marketing.campaign_sender_service import CampaignSenderService


class CampaignSchedulerService:


    def __init__(
        self,
        db: Session,
    ):
        self.db = db


    def run_scheduled_campaigns(
        self,
    ):

        campaigns = (
            self.db.query(Campaign)
            .filter(
                Campaign.scheduled_at <= datetime.utcnow(),
                Campaign.status == CampaignStatus.DRAFT,
            )
            .all()
        )


        results = []


        for campaign in campaigns:

            delivery_service = EmailDeliveryService(
                self.db
            )

            delivery_service.create_campaign_deliveries(
                campaign
            )


            campaign.status = CampaignStatus.RUNNING
            self.db.commit()


            sender = CampaignSenderService(
                self.db
            )

            result = sender.send_campaign(
                campaign.id
            )


            campaign.status = (
                CampaignStatus.COMPLETED
                if result["failed"] == 0
                else CampaignStatus.FAILED
            )


            campaign.sent_count = result["sent"]
            campaign.failed_count = result["failed"]


            self.db.commit()


            results.append(
                {
                    "campaign_id": campaign.id,
                    "result": result,
                }
            )


        return results
