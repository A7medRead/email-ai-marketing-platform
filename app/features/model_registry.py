"""Import ORM models so all SQLAlchemy relationships are registered."""

from app.features.email_generation.model import Email
from app.features.templates.model import Template
from app.features.users.model import User
from app.features.contacts.model import Contact
from app.features.contact_lists.model import ContactList
from app.features.contact_lists.association import ContactListContact
from app.features.sender_accounts.model import SenderAccount
from app.features.campaigns.model import Campaign
from app.features.campaigns.delivery_model import EmailDelivery

__all__ = [
    "Campaign",
    "Contact",
    "ContactList",
    "ContactListContact",
    "Email",
    "EmailDelivery",
    "SenderAccount",
    "Template",
    "User",
]
