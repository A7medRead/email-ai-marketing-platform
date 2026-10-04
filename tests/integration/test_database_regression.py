"""Regression: relationships, stored status values and commit persistence."""
from sqlalchemy import text

from app.features.campaigns.delivery_model import EmailDelivery, EmailDeliveryStatus
from app.features.campaigns.enums import CampaignStatus
from app.features.campaigns.model import Campaign
from app.features.campaigns.delivery_service import EmailDeliveryService
from app.features.campaigns.sender_service import CampaignSenderService
from app.features.contacts.enums import ContactStatus
from app.features.sender_accounts.enums import SenderAccountStatus
from tests.factories import Scenario, make_delivery


def test_delivery_relationships_resolve_campaign_contact_and_sender(db):
    s = Scenario(db, n_contacts=1)
    d = make_delivery(db, s.campaign, s.contacts[0], s.sender)
    db.expire_all()
    d = db.get(EmailDelivery, d.id)
    assert d.campaign.id == s.campaign.id
    assert d.contact.email == "c0@example.com"
    assert d.sender_account.email == "sender@example.com"


def test_campaign_relationships_resolve_sender_list_and_user(db):
    s = Scenario(db)
    c = db.get(Campaign, s.campaign.id)
    assert c.sender_account.id == s.sender.id
    assert len(c.contact_list.contacts) == 3
    assert c.user.id == s.user.id


def test_deliveries_are_found_by_campaign_via_repository(db):
    s = Scenario(db, n_contacts=2)
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    assert len(EmailDeliveryService(db).repository.get_by_campaign(s.campaign.id)) == 2


def test_state_persists_across_sessions_after_commit(db, session_factory, smtp):
    s = Scenario(db, n_contacts=1)
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    CampaignSenderService(db).send_campaign(s.campaign.id)

    fresh = session_factory()
    try:
        d = fresh.query(EmailDelivery).one()
        assert d.status == EmailDeliveryStatus.SENT and d.sent_at is not None
        assert fresh.get(Campaign, s.campaign.id).status == CampaignStatus.COMPLETED
    finally:
        fresh.close()


def test_status_values_stored_in_sqlite(db, smtp):
    """Delivery/sender/contact enums are persisted by NAME (upper-case); campaigns by VALUE (lower-case)."""
    s = Scenario(db, n_contacts=1)
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    CampaignSenderService(db).send_campaign(s.campaign.id)

    q = lambda sql: db.execute(text(sql)).scalar()
    assert q("select status from email_deliveries") == "SENT"
    assert q("select status from campaigns") == "completed"
    assert q("select status from sender_accounts") == "VERIFIED"
    assert q("select status from contacts") == "ACTIVE"


def test_enum_values_in_use():
    assert [s.value for s in SenderAccountStatus] == ["pending", "verified", "failed", "disabled"]
    assert [s.value for s in ContactStatus] == ["active", "unsubscribed", "bounced", "blocked"]


def test_deleting_campaign_cascades_to_deliveries_through_orm_only(db):
    """With SQLite foreign keys off (production default) DB-level cascades do not run;
    the ORM delete of a Campaign does not remove its deliveries (no ORM cascade on the relationship)."""
    s = Scenario(db, n_contacts=1)
    make_delivery(db, s.campaign, s.contacts[0], s.sender)
    db.delete(s.campaign)
    db.commit()
    assert db.query(EmailDelivery).count() == 1  # orphaned: characterizes missing enforcement


def test_sender_defaults_for_unused_limit_columns(db):
    s = Scenario(db)
    a = s.sender
    assert (a.daily_limit, a.hourly_limit, a.daily_sent, a.hourly_sent, a.priority) == (500, 100, 0, 0, 1)


def test_sending_never_updates_sender_usage_counters(db, smtp):
    """The limit/usage columns exist but are not read or written by the current sender."""
    s = Scenario(db, n_contacts=3)
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    CampaignSenderService(db).send_campaign(s.campaign.id)
    db.expire_all()
    assert (s.sender.daily_sent, s.sender.hourly_sent, s.sender.last_used_at) == (0, 0, None)


def test_sending_ignores_sender_daily_limit(db, smtp):
    s = Scenario(db, n_contacts=3)
    s.sender.daily_limit = 1
    s.sender.hourly_limit = 1
    db.commit()
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    assert CampaignSenderService(db).send_campaign(s.campaign.id) == {"sent": 3, "failed": 0}


def test_disabled_sender_sends_nothing_and_delivery_stays_pending(db, smtp):
    """Sender status is enforced at claim time: a disabled sender takes no work."""
    s = Scenario(db, n_contacts=1)
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    s.sender.status = SenderAccountStatus.DISABLED
    db.commit()
    assert CampaignSenderService(db).send_campaign(s.campaign.id) == {"sent": 0, "failed": 0}
    assert smtp.sent == []
    assert db.query(EmailDelivery).one().status == EmailDeliveryStatus.PENDING
