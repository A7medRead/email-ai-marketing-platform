"""Characterization: EmailDeliveryService.create_campaign_deliveries (campaign preparation)."""
from app.features.campaigns.delivery_model import EmailDeliveryStatus
from app.features.campaigns.delivery_service import EmailDeliveryService
from app.features.contacts.enums import ContactStatus
from tests.factories import Scenario, make_contact, make_list, make_campaign


def test_prepare_campaign_creates_pending_deliveries(db):
    s = Scenario(db, n_contacts=3)
    deliveries = EmailDeliveryService(db).create_campaign_deliveries(s.campaign)

    assert len(deliveries) == 3
    assert {d.recipient_email for d in deliveries} == {c.email for c in s.contacts}
    assert all(d.status == EmailDeliveryStatus.PENDING for d in deliveries)
    assert all(d.sent_at is None and d.error_message is None for d in deliveries)


def test_prepare_campaign_copies_campaign_sender_to_deliveries(db):
    s = Scenario(db)
    deliveries = EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    assert {d.sender_account_id for d in deliveries} == {s.sender.id}


def test_prepare_campaign_links_each_delivery_to_its_contact(db):
    s = Scenario(db)
    deliveries = EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    by_contact = {d.contact_id: d for d in deliveries}
    for contact in s.contacts:
        assert by_contact[contact.id].recipient_email == contact.email


def test_prepare_campaign_is_idempotent(db):
    s = Scenario(db)
    service = EmailDeliveryService(db)
    first = service.create_campaign_deliveries(s.campaign)
    second = service.create_campaign_deliveries(s.campaign)

    assert {d.id for d in first} == {d.id for d in second}
    assert len(service.get_campaign_deliveries(s.campaign.id)["items"]) == 3


def test_prepare_campaign_skips_contacts_that_are_not_active(db):
    s = Scenario(db, n_contacts=1)
    extra = [
        make_contact(db, s.user, "unsub@example.com", ContactStatus.UNSUBSCRIBED),
        make_contact(db, s.user, "bounced@example.com", ContactStatus.BOUNCED),
        make_contact(db, s.user, "blocked@example.com", ContactStatus.BLOCKED),
    ]
    contact_list = make_list(db, s.user, s.contacts + extra, name="Mixed")
    campaign = make_campaign(db, s.user, s.sender, contact_list)

    deliveries = EmailDeliveryService(db).create_campaign_deliveries(campaign)

    assert [d.recipient_email for d in deliveries] == ["c0@example.com"]


def test_prepare_campaign_with_only_inactive_contacts_creates_nothing(db):
    s = Scenario(db, n_contacts=0)
    c = make_contact(db, s.user, "unsub@example.com", ContactStatus.UNSUBSCRIBED)
    campaign = make_campaign(db, s.user, s.sender, make_list(db, s.user, [c], "L2"))
    assert EmailDeliveryService(db).create_campaign_deliveries(campaign) == []
