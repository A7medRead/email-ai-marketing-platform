"""Phase 2C-2: sender-level failures take the sender out of rotation."""
import smtplib

import pytest

from app.features.campaigns.delivery_model import EmailDelivery, EmailDeliveryStatus
from app.features.campaigns.delivery_service import EmailDeliveryService
from app.features.campaigns.dispatcher import is_sender_failure
from app.features.campaigns.sender_service import CampaignSenderService
from app.features.sender_accounts.enums import SenderAccountStatus
from app.features.sender_accounts.selection import get_available_senders
from app.features.sender_accounts.service import SenderAccountService
from tests.factories import Scenario, make_sender


def _run(db, s):
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    CampaignSenderService(db).send_campaign(s.campaign.id)
    db.expire_all()
    return {d.recipient_email: d for d in db.query(EmailDelivery).all()}


def test_auth_failure_fails_delivery_and_sender(db, smtp):
    s = Scenario(db, n_contacts=1)
    smtp.fail_auth()

    d = _run(db, s)["c0@example.com"]

    assert d.status == EmailDeliveryStatus.FAILED
    assert s.sender.status == SenderAccountStatus.FAILED
    assert s.sender.verified is False
    assert "535" in s.sender.last_error
    assert get_available_senders(db, s.user.id) == []


def test_recipient_550_keeps_sender_verified(db, smtp):
    s = Scenario(db, n_contacts=1)
    smtp.smtp_5xx("c0@example.com")

    d = _run(db, s)["c0@example.com"]

    assert d.status == EmailDeliveryStatus.FAILED
    assert s.sender.status == SenderAccountStatus.VERIFIED
    assert get_available_senders(db, s.user.id) == [s.sender]


def test_timeout_keeps_delivery_pending_and_sender_eligible(db, smtp):
    s = Scenario(db, n_contacts=1)
    smtp.fail_timeout()

    d = _run(db, s)["c0@example.com"]

    assert d.status == EmailDeliveryStatus.PENDING
    assert s.sender.status == SenderAccountStatus.VERIFIED


def test_unknown_error_does_not_disable_sender(db, smtp):
    s = Scenario(db, n_contacts=1)
    smtp.fail_recipient("c0@example.com", RuntimeError("something odd"))

    d = _run(db, s)["c0@example.com"]

    assert d.status == EmailDeliveryStatus.FAILED  # existing: unknown = permanent
    assert s.sender.status == SenderAccountStatus.VERIFIED


def test_explicit_sending_quota_disables_sender(db, smtp):
    s = Scenario(db, n_contacts=1)
    smtp.fail_recipient(
        "c0@example.com",
        smtplib.SMTPResponseException(550, b"5.4.5 Daily user sending quota exceeded"),
    )

    _run(db, s)

    assert s.sender.status == SenderAccountStatus.FAILED


def test_other_sender_takes_over_after_auth_failure(db, smtp):
    s = Scenario(db, n_contacts=1)
    sender_b = make_sender(db, s.user, email="b@example.com", priority=2)
    smtp.fail_auth()
    _run(db, s)
    assert [x.id for x in get_available_senders(db, s.user.id)] == [sender_b.id]

    smtp.login_error = None  # B's credentials work
    db.query(EmailDelivery).update({"status": EmailDeliveryStatus.PENDING})
    db.commit()
    CampaignSenderService(db).send_campaign(s.campaign.id)
    db.expire_all()

    d = db.query(EmailDelivery).one()
    assert d.status == EmailDeliveryStatus.SENT
    assert d.sender_account_id == sender_b.id
    assert sender_b.status == SenderAccountStatus.VERIFIED


def test_failed_sender_recovers_through_existing_verification(db, smtp):
    s = Scenario(db, n_contacts=1)
    smtp.fail_auth()
    _run(db, s)
    assert s.sender.status == SenderAccountStatus.FAILED

    smtp.login_error = None
    SenderAccountService(db).verify_sender_account(s.sender.id, s.user.id)

    db.expire_all()
    assert s.sender.status == SenderAccountStatus.VERIFIED
    assert get_available_senders(db, s.user.id) == [s.sender]


@pytest.mark.parametrize(
    "message, expected",
    [
        ("Gmail SMTP connection failed: (535, b'5.7.8 Username and Password not accepted')", True),
        ("Gmail SMTP connection failed: (534, b'authentication required')", True),
        ("Gmail SMTP connection failed: (550, b'account has been suspended')", True),
        ("(550, b'5.4.5 Daily user sending quota exceeded')", True),
        ("(421, b'sending limit exceeded for this account')", True),
        ("{'x@y.com': (550, b'mailbox unavailable')}", False),
        ("{'x@y.com': (552, b'mailbox over quota')}", False),
        ("{'x@y.com': (550, b'recipient account disabled')}", False),
        ("(421, b'try again later')", False),
        ("(429, b'too many requests')", False),
        ("Gmail SMTP connection failed: timed out", False),
        ("something odd", False),
        (None, False),
    ],
)
def test_is_sender_failure_only_for_clear_cases(message, expected):
    assert is_sender_failure(message) is expected
