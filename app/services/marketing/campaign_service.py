from sqlalchemy.orm import Session

from app.models.marketing.campaign import Campaign
from app.models.marketing.campaign_enums import CampaignStatus

from app.models.marketing.sender_account import SenderAccount
from app.models.marketing.sender_account_enums import SenderAccountStatus

from app.models.marketing.contact_list import ContactList
from app.models.marketing.contact_list_contact import ContactListContact

from app.repositories.marketing.campaign_repository import CampaignRepository

from app.schemas.marketing.campaign import (
    CampaignCreate,
    CampaignUpdate,
)

from app.core.exceptions.campaign import (
    ContactListNotFound,
    ContactListEmpty,
)

from app.core.exceptions.sender_account import (
    SenderAccountNotFound,
    SenderAccountNotVerified,
)


class CampaignService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = CampaignRepository(db)


    def create_campaign(
        self,
        user_id: int,
        campaign: CampaignCreate,
    ) -> Campaign:

        if campaign.sender_account_id:

            sender_account = (
                self.db.query(SenderAccount)
                .filter(
                    SenderAccount.id == campaign.sender_account_id,
                    SenderAccount.user_id == user_id,
                )
                .first()
            )

            if not sender_account:
                raise SenderAccountNotFound()


            if sender_account.status != SenderAccountStatus.VERIFIED:
                raise SenderAccountNotVerified()


        if campaign.contact_list_id:

            contact_list = (
                self.db.query(ContactList)
                .filter(
                    ContactList.id == campaign.contact_list_id,
                    ContactList.user_id == user_id,
                )
                .first()
            )

            if not contact_list:
                raise ContactListNotFound()


            contacts_count = (
                self.db.query(ContactListContact)
                .filter(
                    ContactListContact.contact_list_id
                    == campaign.contact_list_id
                )
                .count()
            )


            if contacts_count == 0:
                raise ContactListEmpty()


        new_campaign = Campaign(
            user_id=user_id,
            name=campaign.name,
            subject=campaign.subject,
            description=campaign.description,
            sender_account_id=campaign.sender_account_id,
            template_id=campaign.template_id,
            contact_list_id=campaign.contact_list_id,
            scheduled_at=campaign.scheduled_at,
            status=CampaignStatus.DRAFT,
        )


        return self.repository.create(
            new_campaign
        )


    def get_campaigns(
        self,
        user_id: int,
    ):
        return self.repository.get_all(user_id)


    def get_campaign(
        self,
        campaign_id: int,
        user_id: int,
    ):
        return self.repository.get_by_id(
            campaign_id,
            user_id,
        )


    def update_campaign(
        self,
        campaign_id: int,
        user_id: int,
        campaign: CampaignUpdate,
    ):
        return self.repository.update(
            campaign_id,
            user_id,
            campaign.model_dump(
                exclude_unset=True
            ),
        )


    def delete_campaign(
        self,
        campaign_id: int,
        user_id: int,
    ):
        return self.repository.delete(
            campaign_id,
            user_id,
        )
