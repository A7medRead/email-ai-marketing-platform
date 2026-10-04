from sqlalchemy.orm import Session

from app.features.campaigns.model import Campaign
from app.features.campaigns.enums import CampaignStatus

from app.features.sender_accounts.model import SenderAccount
from app.features.sender_accounts.enums import SenderAccountStatus

from app.features.contact_lists.model import ContactList
from app.features.contact_lists.association import ContactListContact
from app.features.templates.model import Template

from app.features.campaigns.repository import CampaignRepository

from app.features.campaigns.schemas import (
    CampaignCreate,
    CampaignUpdate,
)


class CampaignService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = CampaignRepository(db)


    def create_campaign(
        self,
        user_id: int,
        data: CampaignCreate,
    ):

        sender_account = (
            self.db.query(SenderAccount)
            .filter(
                SenderAccount.id == data.sender_account_id,
                SenderAccount.user_id == user_id,
            )
            .first()
        )

        if not sender_account:
            raise ValueError(
                "Sender account not found."
            )


        if sender_account.status != SenderAccountStatus.VERIFIED:
            raise ValueError(
                "Sender account is not verified."
            )


        contact_list = (
            self.db.query(ContactList)
            .filter(
                ContactList.id == data.contact_list_id,
                ContactList.user_id == user_id,
            )
            .first()
        )


        if not contact_list:
            raise ValueError(
                "Contact list not found."
            )


        contacts_count = (
            self.db.query(ContactListContact)
            .filter(
                ContactListContact.contact_list_id
                == data.contact_list_id
            )
            .count()
        )


        if contacts_count == 0:
            raise ValueError(
                "Contact list is empty."
            )


        template = None

        if data.template_id:

            template = (
                self.db.query(Template)
                .filter(
                    Template.id == data.template_id,
                    Template.user_id == user_id,
                )
                .first()
            )

            if not template:
                raise ValueError(
                    "Template not found."
                )


        campaign = Campaign(
            user_id=user_id,
            sender_account_id=data.sender_account_id,
            contact_list_id=data.contact_list_id,
            template_id=data.template_id,
            name=data.name,
            from_name=data.from_name,
            subject=template.subject if template else data.subject,
            body=template.body if template else data.body,
            status=CampaignStatus.DRAFT,
            scheduled_at=data.scheduled_at,
            total_recipients=len(contact_list.contacts),
        )


        return self.repository.create(
            campaign
        )


    def get_campaigns(
        self,
        user_id: int,
    ):
        return self.repository.get_all(
            user_id
        )


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
        data: CampaignUpdate,
    ):

        campaign = self.repository.get_by_id(
            campaign_id,
            user_id,
        )

        if not campaign:
            return None


        update_data = data.model_dump(
            exclude_unset=True
        )


        for key, value in update_data.items():
            setattr(
                campaign,
                key,
                value,
            )


        return self.repository.update(
            campaign
        )


    def delete_campaign(
        self,
        campaign_id: int,
        user_id: int,
    ):

        campaign = self.repository.get_by_id(
            campaign_id,
            user_id,
        )

        if not campaign:
            return False


        return self.repository.delete(
            campaign
        )
