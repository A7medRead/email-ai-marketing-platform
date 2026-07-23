from sqlalchemy.orm import Session

from app.models.marketing.email_delivery import (
    EmailDelivery,
    EmailDeliveryStatus,
)

from app.models.marketing.campaign import Campaign

from app.repositories.marketing.email_delivery_repository import (
    EmailDeliveryRepository,
)


class EmailDeliveryService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

        self.repository = EmailDeliveryRepository(
            db
        )


    def create_campaign_deliveries(
        self,
        campaign: Campaign,
    ):

        deliveries = []


        if not campaign.contact_list:
            return deliveries


        for contact in campaign.contact_list.contacts:

            delivery = EmailDelivery(
                campaign_id=campaign.id,

                contact_id=contact.id,

                sender_account_id=campaign.sender_account_id,

                recipient_email=contact.email,

                status=EmailDeliveryStatus.PENDING,
            )


            self.repository.create(
                delivery
            )


            deliveries.append(
                delivery
            )


        return deliveries


    def get_campaign_deliveries(
        self,
        campaign_id: int,
    ):

        return self.repository.get_by_campaign(
            campaign_id
        )
