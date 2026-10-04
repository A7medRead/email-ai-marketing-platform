from datetime import datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.features.campaigns.model import Campaign
from app.features.campaigns.enums import CampaignStatus

from app.features.campaigns.delivery_model import EmailDelivery, EmailDeliveryStatus
from app.features.campaigns.delivery_service import EmailDeliveryService
from app.features.campaigns.dispatcher import recover_stale_deliveries
from app.features.campaigns.sender_service import CampaignSenderService


class CampaignSchedulerService:


    def __init__(
        self,
        db: Session,
    ):
        self.db = db


    def run_scheduled_campaigns(
        self,
        user_id: int | None = None,
    ):

        # Release deliveries whose worker died mid-send.
        recover_stale_deliveries(self.db)

        has_pending = (
            self.db.query(EmailDelivery.id)
            .filter(
                EmailDelivery.campaign_id == Campaign.id,
                EmailDelivery.status == EmailDeliveryStatus.PENDING,
            )
            .exists()
        )

        # Due DRAFT campaigns start; RUNNING ones with PENDING deliveries
        # (retries that have become due, recovered deliveries) are resumed.
        query = self.db.query(Campaign).filter(
            or_(
                and_(
                    Campaign.scheduled_at <= datetime.utcnow(),
                    Campaign.status == CampaignStatus.DRAFT,
                ),
                and_(
                    Campaign.status == CampaignStatus.RUNNING,
                    has_pending,
                ),
            )
        )

        if user_id is not None:
            query = query.filter(Campaign.user_id == user_id)

        campaigns = query.all()


        results = []


        for campaign in campaigns:

            if campaign.status == CampaignStatus.DRAFT:

                try:
                    EmailDeliveryService(
                        self.db
                    ).create_campaign_deliveries(
                        campaign
                    )
                except ValueError as e:
                    # Invalid Variant: starting would fail every send, and there is no placeholder
                    # fallback (13A.13A), so the campaign is marked FAILED instead of sending the
                    # wrong content. One bad campaign must not stop the others in this run.
                    self.db.rollback()
                    campaign.status = CampaignStatus.FAILED
                    self.db.commit()
                    results.append(
                        {
                            "campaign_id": campaign.id,
                            "result": {"error": str(e)},
                        }
                    )
                    continue


            campaign.status = CampaignStatus.RUNNING
            self.db.commit()


            sender = CampaignSenderService(
                self.db
            )

            result = sender.send_campaign(
                campaign.id
            )


            results.append(
                {
                    "campaign_id": campaign.id,
                    "result": result,
                }
            )


        return results
