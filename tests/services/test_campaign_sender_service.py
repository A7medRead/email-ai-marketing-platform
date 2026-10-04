"""Characterization: CampaignSenderService.send_campaign (current inline sending loop)."""
from app.core.encryption import encrypt
from app.features.campaigns.delivery_model import EmailDelivery, EmailDeliveryStatus
from app.features.campaigns.delivery_service import EmailDeliveryService
from app.features.campaigns.enums import CampaignStatus
from app.features.campaigns.model import Campaign
from app.features.campaigns.sender_service import CampaignSenderService
from app.features.contacts.enums import ContactStatus
from app.features.sender_accounts.enums import SenderAccountStatus
from tests.factories import Scenario, make_delivery


def _prepare(db, s):
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)


def _statuses(db, campaign_id):
    rows = db.query(EmailDelivery).filter(EmailDelivery.campaign_id == campaign_id).all()
    return {d.recipient_email: d for d in rows}


def test_send_campaign_marks_successful_delivery_sent(db, smtp):
    s = Scenario(db, n_contacts=2)
    _prepare(db, s)

    result = CampaignSenderService(db).send_campaign(s.campaign.id)

    assert result == {"sent": 2, "failed": 0}
    for d in _statuses(db, s.campaign.id).values():
        assert d.status == EmailDeliveryStatus.SENT
        assert d.sent_at is not None
    assert sorted(smtp.recipients()) == ["c0@example.com", "c1@example.com"]


def test_send_campaign_marks_failed_delivery_failed(db, smtp):
    s = Scenario(db, n_contacts=2)
    _prepare(db, s)
    smtp.smtp_5xx("c1@example.com")

    result = CampaignSenderService(db).send_campaign(s.campaign.id)

    deliveries = _statuses(db, s.campaign.id)
    assert result == {"sent": 1, "failed": 1}
    assert deliveries["c0@example.com"].status == EmailDeliveryStatus.SENT
    assert deliveries["c1@example.com"].status == EmailDeliveryStatus.FAILED
    assert "mailbox unavailable" in deliveries["c1@example.com"].error_message
    assert deliveries["c1@example.com"].sent_at is None


def test_send_campaign_updates_counters_and_completes_when_all_sent(db, smtp):
    s = Scenario(db, n_contacts=3)
    _prepare(db, s)
    CampaignSenderService(db).send_campaign(s.campaign.id)

    db.expire_all()
    c = db.get(Campaign, s.campaign.id)
    assert (c.sent_count, c.failed_count) == (3, 0)
    assert c.status == CampaignStatus.COMPLETED


def test_send_campaign_marks_campaign_failed_if_any_delivery_fails(db, smtp):
    s = Scenario(db, n_contacts=3)
    _prepare(db, s)
    smtp.smtp_5xx("c2@example.com")
    CampaignSenderService(db).send_campaign(s.campaign.id)

    db.expire_all()
    c = db.get(Campaign, s.campaign.id)
    assert (c.sent_count, c.failed_count) == (2, 1)
    assert c.status == CampaignStatus.FAILED


def test_send_campaign_classifies_smtp_errors_temporary_vs_permanent(db, smtp):
    """4xx and timeouts go back to PENDING for retry; 5xx is FAILED."""
    s = Scenario(db, n_contacts=3)
    _prepare(db, s)
    smtp.smtp_4xx("c0@example.com", 451)
    smtp.smtp_5xx("c1@example.com", 550)
    smtp.fail_recipient("c2@example.com", TimeoutError("timed out"))

    CampaignSenderService(db).send_campaign(s.campaign.id)

    d = _statuses(db, s.campaign.id)
    assert d["c0@example.com"].status == EmailDeliveryStatus.PENDING
    assert d["c1@example.com"].status == EmailDeliveryStatus.FAILED
    assert d["c2@example.com"].status == EmailDeliveryStatus.PENDING
    assert all(d[e].next_attempt_at is not None for e in ("c0@example.com", "c2@example.com"))
    assert sorted(smtp.send_attempts) == ["c0@example.com", "c1@example.com", "c2@example.com"]  # one attempt each


def test_send_campaign_connection_failure_requeues_every_delivery(db, smtp):
    s = Scenario(db, n_contacts=2)
    _prepare(db, s)
    smtp.fail_connect()

    result = CampaignSenderService(db).send_campaign(s.campaign.id)

    assert result == {"sent": 0, "failed": 0}
    for d in _statuses(db, s.campaign.id).values():
        assert d.status == EmailDeliveryStatus.PENDING
        assert d.error_message.startswith("Gmail SMTP connection failed")


def test_send_campaign_timeout_requeues_every_delivery(db, smtp):
    s = Scenario(db, n_contacts=2)
    _prepare(db, s)
    smtp.fail_timeout()
    assert CampaignSenderService(db).send_campaign(s.campaign.id) == {"sent": 0, "failed": 0}
    assert {d.status for d in _statuses(db, s.campaign.id).values()} == {EmailDeliveryStatus.PENDING}


def test_send_campaign_authentication_failure_fails_every_delivery(db, smtp):
    s = Scenario(db, n_contacts=2)
    _prepare(db, s)
    smtp.fail_auth()

    result = CampaignSenderService(db).send_campaign(s.campaign.id)

    assert result == {"sent": 0, "failed": 2}
    msg = _statuses(db, s.campaign.id)["c0@example.com"].error_message
    assert "Username and Password not accepted" in msg
    # Every delivery re-authenticates: one connection + login attempt per recipient.
    assert smtp.send_attempts == []


def test_send_campaign_opens_one_smtp_connection_per_email(db, smtp):
    s = Scenario(db, n_contacts=3)
    _prepare(db, s)
    CampaignSenderService(db).send_campaign(s.campaign.id)
    assert len(smtp.connections) == 3
    assert len(smtp.logins) == 3
    assert all(host == "smtp.gmail.com" and port == 587 for host, port in smtp.connections)


def test_send_campaign_strips_spaces_from_gmail_app_password(db, smtp):
    s = Scenario(db, n_contacts=1)
    _prepare(db, s)
    CampaignSenderService(db).send_campaign(s.campaign.id)
    assert smtp.logins == [("sender@example.com", "abcdefghijklmnop")]


def test_send_campaign_uses_from_name_override_else_sender_name(db, smtp):
    s = Scenario(db, n_contacts=1)
    _prepare(db, s)
    CampaignSenderService(db).send_campaign(s.campaign.id)
    assert "Sender Name" in smtp.sent[0].from_header

    s.campaign.from_name = "Brand Team"
    s.campaign.status = CampaignStatus.PREPARED
    db.commit()
    d = db.query(EmailDelivery).first()
    d.status = EmailDeliveryStatus.PENDING
    db.commit()
    CampaignSenderService(db).send_campaign(s.campaign.id)
    assert "Brand Team" in smtp.sent[1].from_header


def test_send_campaign_message_has_subject_and_sender(db, smtp):
    s = Scenario(db, n_contacts=1, subject="Big Sale")
    _prepare(db, s)
    CampaignSenderService(db).send_campaign(s.campaign.id)
    m = smtp.sent[0]
    assert m.subject == "Big Sale"
    assert m.sender == "sender@example.com"
    assert m.recipient == "c0@example.com"


def test_send_campaign_missing_campaign_returns_message(db, smtp):
    assert CampaignSenderService(db).send_campaign(9999) == {
        "sent": 0, "failed": 0, "message": "Campaign not found",
    }


def test_send_campaign_on_completed_campaign_is_a_noop(db, smtp):
    s = Scenario(db, status=CampaignStatus.COMPLETED)
    _prepare(db, s)
    result = CampaignSenderService(db).send_campaign(s.campaign.id)
    assert result["message"] == "Campaign already completed"
    assert smtp.sent == []


def test_send_campaign_without_prepared_deliveries_completes_with_zero_sent(db, smtp):
    """Quirk: sending an un-prepared campaign 'succeeds' as COMPLETED with nothing sent."""
    s = Scenario(db)
    result = CampaignSenderService(db).send_campaign(s.campaign.id)
    assert result == {"sent": 0, "failed": 0}
    db.expire_all()
    assert db.get(Campaign, s.campaign.id).status == CampaignStatus.COMPLETED
    assert smtp.sent == []


def test_send_campaign_only_processes_pending_deliveries(db, smtp):
    s = Scenario(db, n_contacts=2)
    _prepare(db, s)
    first = db.query(EmailDelivery).order_by(EmailDelivery.id).first()
    first.status = EmailDeliveryStatus.SENT
    db.commit()

    CampaignSenderService(db).send_campaign(s.campaign.id)

    assert smtp.recipients() == ["c1@example.com"]


def test_send_campaign_unsubscribed_contact_is_cancelled_and_not_counted_as_failed(db, smtp):
    s = Scenario(db, n_contacts=2)
    _prepare(db, s)
    s.contacts[1].status = ContactStatus.UNSUBSCRIBED
    db.commit()

    result = CampaignSenderService(db).send_campaign(s.campaign.id)

    deliveries = _statuses(db, s.campaign.id)
    gone = deliveries["c1@example.com"]
    assert gone.status == EmailDeliveryStatus.CANCELLED
    assert gone.error_message == "Contact is no longer subscribed."
    assert "c1@example.com" not in smtp.recipients()
    # CANCELLED is not a failure, so the campaign still ends COMPLETED.
    assert result == {"sent": 1, "failed": 0}
    db.expire_all()
    c = db.get(Campaign, s.campaign.id)
    assert c.failed_count == 0
    assert c.status == CampaignStatus.COMPLETED


def test_send_campaign_blocked_and_bounced_contacts_are_cancelled(db, smtp):
    s = Scenario(db, n_contacts=2)
    _prepare(db, s)
    s.contacts[0].status = ContactStatus.BLOCKED
    s.contacts[1].status = ContactStatus.BOUNCED
    db.commit()
    CampaignSenderService(db).send_campaign(s.campaign.id)
    assert smtp.sent == []
    assert {d.status for d in _statuses(db, s.campaign.id).values()} == {EmailDeliveryStatus.CANCELLED}


def test_send_campaign_delivery_without_sender_is_claimed_by_an_eligible_sender(db, smtp):
    """Sender is chosen at claim time, not taken from the delivery/campaign."""
    s = Scenario(db, n_contacts=1)
    make_delivery(db, s.campaign, s.contacts[0], sender=None)

    result = CampaignSenderService(db).send_campaign(s.campaign.id)

    assert result == {"sent": 1, "failed": 0}
    assert db.query(EmailDelivery).one().sender_account_id == s.sender.id


def test_send_campaign_without_any_eligible_sender_leaves_deliveries_pending(db, smtp):
    s = Scenario(db, n_contacts=1)
    s.sender.status = SenderAccountStatus.PENDING
    db.commit()
    _prepare(db, s)

    assert CampaignSenderService(db).send_campaign(s.campaign.id) == {"sent": 0, "failed": 0}
    assert db.query(EmailDelivery).one().status == EmailDeliveryStatus.PENDING
    assert smtp.connections == []


def test_send_campaign_with_undecryptable_credentials_fails_delivery(db, smtp):
    s = Scenario(db, n_contacts=1)
    s.sender.encrypted_password = "not-a-fernet-token"
    db.commit()
    _prepare(db, s)

    result = CampaignSenderService(db).send_campaign(s.campaign.id)

    assert result == {"sent": 0, "failed": 1}
    d = db.query(EmailDelivery).one()
    assert d.status == EmailDeliveryStatus.FAILED
    assert d.error_message.startswith("Gmail SMTP connection failed")
    assert smtp.connections == []


def test_send_campaign_with_empty_stored_password_fails_on_auth(db, smtp):
    s = Scenario(db, n_contacts=1)
    s.sender.encrypted_password = encrypt("")
    db.commit()
    _prepare(db, s)
    smtp.fail_auth()
    assert CampaignSenderService(db).send_campaign(s.campaign.id) == {"sent": 0, "failed": 1}


def test_send_campaign_never_stores_the_smtp_password_in_delivery_errors(db, smtp):
    s = Scenario(db, n_contacts=1)
    _prepare(db, s)
    smtp.fail_auth()
    CampaignSenderService(db).send_campaign(s.campaign.id)
    d = db.query(EmailDelivery).one()
    assert "abcdefghijklmnop" not in d.error_message
    assert "abcd efgh" not in d.error_message
