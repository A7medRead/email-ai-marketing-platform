"""Phase 2B-4: claimed deliveries are sent through the real SMTP path
(CampaignSenderService -> send_campaign_email -> fake transport)."""
from datetime import datetime, timedelta

from app.features.campaigns.delivery_model import EmailDelivery, EmailDeliveryStatus
from app.features.campaigns.dispatcher import MAX_ATTEMPTS
from app.features.campaigns.enums import CampaignStatus
from app.features.campaigns.model import Campaign
from app.features.campaigns.scheduler_service import CampaignSchedulerService
from app.features.campaigns.sender_service import CampaignSenderService
from app.features.contacts.enums import ContactStatus
from app.features.sender_accounts.selection import available_capacity
from tests.factories import make_campaign, make_contact, make_list, make_sender, make_user

S = EmailDeliveryStatus


def queue(db, batch_sizes, pending, campaign_sender_index=0):
    """Senders s0.. (priority order, distinct passwords) and `pending` PENDING deliveries."""
    user = make_user(db)
    senders = [
        make_sender(
            db, user, email=f"s{i}@example.com", password=f"password{i}",
            batch_size=b, priority=i + 1,
        )
        for i, b in enumerate(batch_sizes)
    ]
    contacts = [make_contact(db, user, f"c{i}@example.com") for i in range(pending)]
    campaign = make_campaign(db, user, senders[campaign_sender_index], make_list(db, user, contacts))
    db.add_all(
        EmailDelivery(campaign_id=campaign.id, contact_id=c.id, recipient_email=c.email, status=S.PENDING)
        for c in contacts
    )
    db.commit()
    return user, senders, campaign


def count(db, status):
    db.expire_all()
    return db.query(EmailDelivery).filter_by(status=status).count()


def delivery(db, email):
    db.expire_all()
    return db.query(EmailDelivery).filter_by(recipient_email=email).one()


# ---- multiple senders really send through their own SMTP account ----

def test_each_sender_sends_through_its_own_smtp_account(db, smtp):
    _, (a, b), campaign = queue(db, [2, 2], 4)

    CampaignSenderService(db).send_campaign(campaign.id)

    assert count(db, S.SENT) == 4
    via_a = [m for m in smtp.sent if m.sender == "s0@example.com"]
    via_b = [m for m in smtp.sent if m.sender == "s1@example.com"]
    assert (len(via_a), len(via_b)) == (2, 2)
    # Real credentials per connection, not just the DB column.
    assert sorted(smtp.logins) == [("s0@example.com", "password0")] * 2 + [("s1@example.com", "password1")] * 2
    assert all("s0@example.com" in m.from_header for m in via_a)
    assert all("s1@example.com" in m.from_header for m in via_b)
    # The delivery row agrees with the account that actually sent it.
    for m in smtp.sent:
        d = delivery(db, m.recipient)
        assert db.get(type(a), d.sender_account_id).email == m.sender


def test_claimed_sender_is_used_not_the_campaigns_original_sender(db, smtp):
    # Campaign belongs to s1 (priority 2); the dispatcher assigns s0 (priority 1).
    _, (a, b), campaign = queue(db, [5, 5], 2, campaign_sender_index=1)
    assert campaign.sender_account_id == b.id

    CampaignSenderService(db).send_campaign(campaign.id)

    assert {m.sender for m in smtp.sent} == {"s0@example.com"}
    assert smtp.logins == [("s0@example.com", "password0")] * 2


# ---- capacity enforced by the real flow ----

def test_batch_size_is_enforced_across_dispatcher_runs(db, smtp):
    user, (a,), campaign = queue(db, [2], 5)
    service = CampaignSenderService(db)

    assert service.send_next_batch(campaign) == 2
    assert (count(db, S.SENT), count(db, S.PENDING), count(db, S.SENDING)) == (2, 3, 0)

    assert service.send_next_batch(campaign) == 2
    assert (count(db, S.SENT), count(db, S.PENDING)) == (4, 1)

    assert service.send_next_batch(campaign) == 1
    assert (count(db, S.SENT), count(db, S.PENDING)) == (5, 0)

    assert service.send_next_batch(campaign) == 0
    assert len(smtp.sent) == 5


def test_sender_capacity_is_released_after_each_final_state(db, smtp):
    _, (a,), campaign = queue(db, [2], 2)
    smtp.smtp_5xx("c0@example.com")
    CampaignSenderService(db).send_next_batch(campaign)
    assert (count(db, S.SENT), count(db, S.FAILED)) == (1, 1)
    assert available_capacity(db, a) == 2


# ---- failures ----

def test_temporary_failure_returns_to_pending_with_retry_time_and_frees_capacity(db, smtp):
    _, (a,), campaign = queue(db, [1], 1)
    smtp.smtp_4xx("c0@example.com")
    before = datetime.utcnow()

    CampaignSenderService(db).send_campaign(campaign.id)

    d = delivery(db, "c0@example.com")
    assert d.status == S.PENDING
    assert d.next_attempt_at > before
    assert d.claimed_at is None and d.attempt_count == 1
    assert "try again later" in d.error_message
    assert available_capacity(db, a) == 1
    assert smtp.send_attempts == ["c0@example.com"]  # not retried within the same run


def test_retry_after_backoff_sends_and_counts_once(db, smtp):
    _, _, campaign = queue(db, [5], 1)
    smtp.smtp_4xx("c0@example.com")
    service = CampaignSenderService(db)
    service.send_campaign(campaign.id)

    smtp.recipient_errors.clear()
    d = delivery(db, "c0@example.com")
    d.next_attempt_at = datetime.utcnow() - timedelta(seconds=1)
    db.commit()
    result = service.send_campaign(campaign.id)

    assert result == {"sent": 1, "failed": 0}
    d = delivery(db, "c0@example.com")
    assert (d.status, d.attempt_count, d.error_message) == (S.SENT, 2, None)
    db.expire_all()
    c = db.get(Campaign, campaign.id)
    assert (c.sent_count, c.failed_count, c.status) == (1, 0, CampaignStatus.COMPLETED)


def test_temporary_failures_stop_after_max_attempts(db, smtp):
    _, _, campaign = queue(db, [5], 1)
    smtp.smtp_4xx("c0@example.com")
    service = CampaignSenderService(db)
    for _ in range(MAX_ATTEMPTS):
        d = delivery(db, "c0@example.com")
        d.next_attempt_at = None
        db.commit()
        service.send_campaign(campaign.id)
    assert delivery(db, "c0@example.com").status == S.FAILED
    assert len(smtp.send_attempts) == MAX_ATTEMPTS
    db.expire_all()
    c = db.get(Campaign, campaign.id)
    assert (c.sent_count, c.failed_count, c.status) == (0, 1, CampaignStatus.FAILED)


def test_permanent_failure_becomes_failed_and_frees_capacity(db, smtp):
    _, (a,), campaign = queue(db, [1], 1)
    smtp.smtp_5xx("c0@example.com")

    CampaignSenderService(db).send_campaign(campaign.id)

    d = delivery(db, "c0@example.com")
    assert d.status == S.FAILED and d.next_attempt_at is None and d.claimed_at is None
    assert available_capacity(db, a) == 1
    assert len(smtp.send_attempts) == 1


def test_unsubscribed_contact_is_cancelled_and_never_sent(db, smtp):
    user, (a,), campaign = queue(db, [5], 2)
    db.query(type(make_contact(db, user, "x@example.com"))).filter_by(email="c0@example.com").one().status = (
        ContactStatus.UNSUBSCRIBED
    )
    db.commit()

    CampaignSenderService(db).send_campaign(campaign.id)

    assert delivery(db, "c0@example.com").status == S.CANCELLED
    assert smtp.send_attempts == ["c1@example.com"]
    assert available_capacity(db, a) == 5


# ---- campaign counters ----

def test_counters_count_each_final_outcome_once(db, smtp):
    _, _, campaign = queue(db, [2], 4)
    smtp.smtp_5xx("c1@example.com")
    service = CampaignSenderService(db)

    service.send_campaign(campaign.id)
    service.send_campaign(campaign.id)  # nothing left; must not double count

    db.expire_all()
    c = db.get(Campaign, campaign.id)
    assert (c.sent_count, c.failed_count, c.status) == (3, 1, CampaignStatus.FAILED)
    assert len(smtp.send_attempts) == 4


def test_campaign_with_all_senders_busy_stays_running(db, smtp):
    _, (a,), campaign = queue(db, [1], 2)
    d = delivery(db, "c1@example.com")
    d.status, d.sender_account_id, d.claimed_at = S.SENDING, a.id, datetime.utcnow()
    db.commit()

    result = CampaignSenderService(db).send_campaign(campaign.id)

    assert result == {"sent": 0, "failed": 0}
    assert smtp.sent == []
    db.expire_all()
    assert db.get(Campaign, campaign.id).status == CampaignStatus.RUNNING


# ---- recovery / worker ----

def test_stale_sending_is_recovered_and_then_sent(db, smtp):
    _, (a,), campaign = queue(db, [1], 1)
    d = delivery(db, "c0@example.com")
    d.status, d.sender_account_id = S.SENDING, a.id
    d.claimed_at, d.attempt_count = datetime.utcnow() - timedelta(hours=2), 1
    db.commit()
    assert available_capacity(db, a) == 0  # a crashed worker is holding the slot

    CampaignSenderService(db).send_campaign(campaign.id)

    d = delivery(db, "c0@example.com")
    assert (d.status, d.attempt_count) == (S.SENT, 2)
    assert smtp.send_attempts == ["c0@example.com"]


def test_scheduler_run_recovers_stale_and_resumes_running_campaign(db, smtp):
    _, (a,), campaign = queue(db, [1], 1)
    campaign.status = CampaignStatus.RUNNING
    db.commit()
    d = delivery(db, "c0@example.com")
    d.status, d.sender_account_id = S.SENDING, a.id
    d.claimed_at, d.attempt_count = datetime.utcnow() - timedelta(hours=2), 1
    db.commit()

    results = CampaignSchedulerService(db).run_scheduled_campaigns()

    assert results == [{"campaign_id": campaign.id, "result": {"sent": 1, "failed": 0}}]
    assert delivery(db, "c0@example.com").status == S.SENT
    db.expire_all()
    assert db.get(Campaign, campaign.id).status == CampaignStatus.COMPLETED


def test_scheduler_run_retries_a_due_temporary_failure(db, smtp):
    _, _, campaign = queue(db, [5], 1)
    campaign.status = CampaignStatus.RUNNING
    db.commit()
    smtp.smtp_4xx("c0@example.com")
    service = CampaignSchedulerService(db)
    service.run_scheduled_campaigns()  # fails temporarily
    assert delivery(db, "c0@example.com").status == S.PENDING

    smtp.recipient_errors.clear()
    d = delivery(db, "c0@example.com")
    d.next_attempt_at = datetime.utcnow() - timedelta(seconds=1)
    db.commit()
    service.run_scheduled_campaigns()

    assert delivery(db, "c0@example.com").status == S.SENT
    db.expire_all()
    c = db.get(Campaign, campaign.id)
    assert (c.sent_count, c.status) == (1, CampaignStatus.COMPLETED)


# ---- API ----

def test_send_endpoint_uses_the_queue_and_assigned_senders(client, db, smtp, make_headers):
    user, _, campaign = queue(db, [2, 2], 4)
    r = client.post(f"/campaigns/{campaign.id}/send", headers=make_headers(user))
    assert r.status_code == 200
    assert sorted(m.sender for m in smtp.sent) == ["s0@example.com"] * 2 + ["s1@example.com"] * 2
    assert count(db, S.SENT) == 4
