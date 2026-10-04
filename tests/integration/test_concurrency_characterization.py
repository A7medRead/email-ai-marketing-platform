"""Overlapping send runs (second worker / repeated POST /send).

The atomic PENDING -> SENDING claim means a delivery that is in flight in one
run is invisible to any other run: each recipient is mailed exactly once.
A hook fires inside the first SMTP send and runs a second, independent
`send_campaign` (separate DB session on the same SQLite file).
"""
from app.features.campaigns.delivery_model import EmailDelivery, EmailDeliveryStatus
from app.features.campaigns.delivery_service import EmailDeliveryService
from app.features.campaigns.sender_service import CampaignSenderService
from tests.factories import Scenario


def test_overlapping_send_runs_mail_each_recipient_exactly_once(db, session_factory, smtp):
    s = Scenario(db, n_contacts=3)
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    observed = {}
    state = {"nested": False}

    def second_worker(recipient):
        if state["nested"]:
            return
        state["nested"] = True
        other = session_factory()
        try:
            # Mid-send the delivery is claimed: SENDING, invisible to other runs.
            observed["status_during_send"] = (
                other.query(EmailDelivery).filter_by(recipient_email=recipient).one().status
            )
            CampaignSenderService(other).send_campaign(s.campaign.id)
        finally:
            other.close()

    smtp.on_sendmail = second_worker
    CampaignSenderService(db).send_campaign(s.campaign.id)

    assert observed["status_during_send"] == EmailDeliveryStatus.SENDING
    for email in ("c0@example.com", "c1@example.com", "c2@example.com"):
        assert smtp.send_attempts.count(email) == 1
    assert len(smtp.sent) == 3


def test_delivery_has_sending_state_and_claim_retry_columns():
    from app.features.campaigns.delivery_model import EmailDelivery as D
    assert [s.value for s in EmailDeliveryStatus] == [
        "pending", "queued", "sending", "sent", "failed", "opened", "clicked", "bounced", "cancelled",
    ]
    assert hasattr(D, "claimed_at") and hasattr(D, "attempt_count") and hasattr(D, "next_attempt_at")


def test_failed_delivery_during_overlap_is_attempted_once(db, session_factory, smtp):
    """The claim also covers failures: only one run attempts the delivery."""
    s = Scenario(db, n_contacts=1)
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    smtp.smtp_5xx("c0@example.com")
    fired = {"done": False}

    def second_worker(_):
        if fired["done"]:
            return
        fired["done"] = True
        other = session_factory()
        try:
            CampaignSenderService(other).send_campaign(s.campaign.id)
        finally:
            other.close()

    smtp.on_sendmail = second_worker
    CampaignSenderService(db).send_campaign(s.campaign.id)
    assert smtp.send_attempts.count("c0@example.com") == 1
    db.expire_all()
    assert db.query(EmailDelivery).one().status == EmailDeliveryStatus.FAILED
