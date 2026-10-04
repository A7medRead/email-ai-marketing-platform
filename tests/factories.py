from datetime import datetime

from app.core.encryption import encrypt
from app.core.security import hash_password
from app.features.campaigns.delivery_model import EmailDelivery, EmailDeliveryStatus
from app.features.campaigns.enums import CampaignStatus
from app.features.campaigns.model import Campaign
from app.features.contact_lists.model import ContactList
from app.features.contacts.enums import ContactStatus
from app.features.contacts.model import Contact
from app.features.sender_accounts.enums import SenderAccountStatus
from app.features.sender_accounts.model import SenderAccount
from app.features.users.model import User

SMTP_PASSWORD = "abcd efgh ijkl mnop"  # Gmail app passwords are shown with spaces


def make_user(db, email="owner@example.com"):
    user = User(name="Owner", email=email, password=hash_password("pw-123456"))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_sender(
    db, user, email="sender@example.com", status=SenderAccountStatus.VERIFIED, password=SMTP_PASSWORD, **extra
):
    sender = SenderAccount(
        user_id=user.id,
        email=email,
        name="Sender Name",
        provider="gmail",
        encrypted_password=encrypt(password),
        status=status,
        verified=status == SenderAccountStatus.VERIFIED,
        **extra,
    )
    db.add(sender)
    db.commit()
    db.refresh(sender)
    return sender


def make_contact(db, user, email, status=ContactStatus.ACTIVE):
    contact = Contact(user_id=user.id, first_name="Test", email=email, status=status)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def make_list(db, user, contacts, name="List"):
    contact_list = ContactList(user_id=user.id, name=name)
    contact_list.contacts = list(contacts)
    db.add(contact_list)
    db.commit()
    db.refresh(contact_list)
    return contact_list


def make_campaign(
    db,
    user,
    sender,
    contact_list,
    status=CampaignStatus.DRAFT,
    scheduled_at=None,
    body="Hello there",
    subject="Subject line",
    from_name=None,
):
    campaign = Campaign(
        user_id=user.id,
        sender_account_id=sender.id,
        contact_list_id=contact_list.id,
        name="Campaign",
        from_name=from_name,
        subject=subject,
        body=body,
        status=status,
        scheduled_at=scheduled_at,
        total_recipients=len(contact_list.contacts),
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


def make_delivery(db, campaign, contact, sender, status=EmailDeliveryStatus.PENDING):
    delivery = EmailDelivery(
        campaign_id=campaign.id,
        contact_id=contact.id,
        sender_account_id=sender.id if sender else None,
        recipient_email=contact.email,
        status=status,
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return delivery


class Scenario:
    """A user with a verified sender, N active contacts and a DRAFT campaign."""

    def __init__(self, db, n_contacts=3, **campaign_kwargs):
        self.db = db
        self.user = make_user(db)
        self.sender = make_sender(db, self.user)
        self.contacts = [
            make_contact(db, self.user, f"c{i}@example.com") for i in range(n_contacts)
        ]
        self.list = make_list(db, self.user, self.contacts)
        self.campaign = make_campaign(
            db, self.user, self.sender, self.list, **campaign_kwargs
        )
