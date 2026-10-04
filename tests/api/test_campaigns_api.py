"""Characterization: /campaigns endpoints used by the sending flow."""
from app.features.campaigns.delivery_model import EmailDelivery, EmailDeliveryStatus
from app.features.campaigns.delivery_service import EmailDeliveryService
from app.features.campaigns.enums import CampaignStatus
from app.features.campaigns.model import Campaign
from app.features.contacts.enums import ContactStatus
from app.features.sender_accounts.enums import SenderAccountStatus
from tests.factories import make_contact, make_list, make_sender


def _payload(s, **over):
    data = {
        "sender_account_id": s.sender.id,
        "contact_list_id": s.list.id,
        "name": "Spring",
        "subject": "Hello",
        "body": "Body text",
    }
    data.update(over)
    return data


def _prepare(s):
    """Create deliveries via the service (the /prepare endpoint does not; see its tests below)."""
    return EmailDeliveryService(s.db).create_campaign_deliveries(s.campaign)


def _deliveries(db, campaign_id):
    db.expire_all()
    return db.query(EmailDelivery).filter_by(campaign_id=campaign_id).order_by(EmailDelivery.id).all()


# ---------------------------------------------------------------- create

def test_create_campaign_starts_as_draft_with_total_recipients(client, headers, scenario):
    r = client.post("/campaigns/", json=_payload(scenario), headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "draft"
    assert (body["total_recipients"], body["sent_count"], body["failed_count"]) == (3, 0, 0)
    assert body["sender_account_id"] == scenario.sender.id


def test_create_campaign_total_recipients_counts_inactive_contacts_too(client, headers, scenario, db):
    """Quirk: total_recipients = all list members, though only ACTIVE ones get deliveries."""
    unsub = make_contact(db, scenario.user, "u@example.com", ContactStatus.UNSUBSCRIBED)
    lst = make_list(db, scenario.user, scenario.contacts + [unsub], name="L2")
    r = client.post("/campaigns/", json=_payload(scenario, contact_list_id=lst.id), headers=headers)
    cid = r.json()["id"]
    assert r.json()["total_recipients"] == 4
    EmailDeliveryService(db).create_campaign_deliveries(db.get(Campaign, cid))
    assert len(_deliveries(db, cid)) == 3


def test_create_campaign_requires_verified_sender(client, headers, scenario, db):
    pending = make_sender(db, scenario.user, "p@example.com", SenderAccountStatus.PENDING)
    r = client.post("/campaigns/", json=_payload(scenario, sender_account_id=pending.id), headers=headers)
    assert r.status_code == 400 and r.json()["detail"] == "Sender account is not verified."


def test_create_campaign_rejects_unknown_sender_list_and_empty_list(client, headers, scenario, db):
    assert client.post("/campaigns/", json=_payload(scenario, sender_account_id=999), headers=headers).json()["detail"] == "Sender account not found."
    assert client.post("/campaigns/", json=_payload(scenario, contact_list_id=999), headers=headers).json()["detail"] == "Contact list not found."
    empty = make_list(db, scenario.user, [], name="Empty")
    r = client.post("/campaigns/", json=_payload(scenario, contact_list_id=empty.id), headers=headers)
    assert r.status_code == 400 and r.json()["detail"] == "Contact list is empty."


def test_create_campaign_cannot_use_another_users_sender(client, scenario, other_user, make_headers):
    r = client.post("/campaigns/", json=_payload(scenario), headers=make_headers(other_user))
    assert r.status_code == 400 and r.json()["detail"] == "Sender account not found."


def test_get_campaign_is_scoped_to_owner(client, headers, scenario, other_user, make_headers):
    cid = scenario.campaign.id
    assert client.get(f"/campaigns/{cid}", headers=headers).status_code == 200
    assert client.get(f"/campaigns/{cid}", headers=make_headers(other_user)).status_code == 404


# ---------------------------------------------------------------- prepare endpoint

def test_prepare_endpoint_sets_prepared_status(client, headers, scenario, db):
    client.post(f"/campaigns/{scenario.campaign.id}/prepare", headers=headers)
    db.expire_all()
    assert db.get(Campaign, scenario.campaign.id).status == CampaignStatus.PREPARED


def test_prepare_endpoint_creates_deliveries_and_reports_count(client, headers, scenario, db):
    r = client.post(f"/campaigns/{scenario.campaign.id}/prepare", headers=headers)
    assert r.status_code == 200
    assert r.json() == {"message": "Campaign prepared", "deliveries_created": 3}
    ds = _deliveries(db, scenario.campaign.id)
    assert len(ds) == 3
    assert {d.status for d in ds} == {EmailDeliveryStatus.PENDING}
    assert {d.sender_account_id for d in ds} == {scenario.sender.id}


def test_prepare_endpoint_is_idempotent(client, headers, scenario, db):
    url = f"/campaigns/{scenario.campaign.id}/prepare"
    client.post(url, headers=headers)
    r = client.post(url, headers=headers)
    assert r.json() == {"message": "Campaign already prepared", "deliveries_created": 0}
    assert len(_deliveries(db, scenario.campaign.id)) == 3


def test_prepare_then_send_via_api_sends_every_recipient(client, headers, scenario, db, smtp):
    cid = scenario.campaign.id
    client.post(f"/campaigns/{cid}/prepare", headers=headers)
    client.post(f"/campaigns/{cid}/send", headers=headers)
    assert sorted(smtp.recipients()) == ["c0@example.com", "c1@example.com", "c2@example.com"]
    db.expire_all()
    c = db.get(Campaign, cid)
    assert (c.status, c.sent_count, c.failed_count) == (CampaignStatus.COMPLETED, 3, 0)


def test_prepare_unknown_campaign_is_404(client, headers):
    assert client.post("/campaigns/999/prepare", headers=headers).status_code == 404


def test_prepare_foreign_campaign_is_404(client, scenario, other_user, make_headers):
    assert client.post(f"/campaigns/{scenario.campaign.id}/prepare", headers=make_headers(other_user)).status_code == 404


# ---------------------------------------------------------------- send

def test_send_endpoint_response_shape(client, headers, scenario):
    cid = scenario.campaign.id
    _prepare(scenario)
    r = client.post(f"/campaigns/{cid}/send", headers=headers)
    assert r.status_code == 200
    assert r.json() == {"message": "Campaign sending started", "campaign_id": cid}


def test_send_endpoint_sends_prepared_deliveries_via_background_task(client, headers, scenario, db, smtp):
    """TestClient executes BackgroundTasks before returning, so the end state is deterministic."""
    cid = scenario.campaign.id
    _prepare(scenario)
    client.post(f"/campaigns/{cid}/send", headers=headers)

    assert {d.status for d in _deliveries(db, cid)} == {EmailDeliveryStatus.SENT}
    assert sorted(smtp.recipients()) == ["c0@example.com", "c1@example.com", "c2@example.com"]
    c = db.get(Campaign, cid)
    assert (c.sent_count, c.failed_count, c.status) == (3, 0, CampaignStatus.COMPLETED)


def test_send_endpoint_with_failures_ends_campaign_failed(client, headers, scenario, db, smtp):
    cid = scenario.campaign.id
    _prepare(scenario)
    smtp.smtp_5xx("c1@example.com")
    client.post(f"/campaigns/{cid}/send", headers=headers)

    db.expire_all()
    c = db.get(Campaign, cid)
    assert (c.sent_count, c.failed_count, c.status) == (2, 1, CampaignStatus.FAILED)


def test_send_endpoint_does_not_prepare_so_unprepared_campaign_sends_nothing(client, headers, scenario, db, smtp):
    cid = scenario.campaign.id
    r = client.post(f"/campaigns/{cid}/send", headers=headers)
    assert r.status_code == 200
    assert smtp.sent == []
    db.expire_all()
    assert db.get(Campaign, cid).status == CampaignStatus.COMPLETED  # quirk


def test_send_endpoint_unknown_or_foreign_campaign_is_404(client, headers, scenario, other_user, make_headers):
    assert client.post("/campaigns/999/send", headers=headers).status_code == 404
    assert client.post(f"/campaigns/{scenario.campaign.id}/send", headers=make_headers(other_user)).status_code == 404


def test_send_endpoint_marks_running_before_background_work(client, headers, scenario, db, monkeypatch):
    """The endpoint itself sets RUNNING; the background task is what finishes the campaign."""
    from app.features.campaigns import api as campaigns_api

    class NoopSender:
        def __init__(self, db): ...
        def send_campaign(self, campaign_id): return {}

    monkeypatch.setattr(campaigns_api, "CampaignSenderService", NoopSender)
    cid = scenario.campaign.id
    client.post(f"/campaigns/{cid}/send", headers=headers)
    db.expire_all()
    assert db.get(Campaign, cid).status == CampaignStatus.RUNNING


def test_second_send_does_not_resend_or_change_counters(client, headers, scenario, db, smtp):
    """/send on a COMPLETED campaign flips it to RUNNING first; nothing is re-sent and the
    counters (recounted from delivery states) stay correct."""
    cid = scenario.campaign.id
    _prepare(scenario)
    client.post(f"/campaigns/{cid}/send", headers=headers)
    assert len(smtp.sent) == 3

    client.post(f"/campaigns/{cid}/send", headers=headers)

    assert len(smtp.sent) == 3  # no duplicate mail
    db.expire_all()
    c = db.get(Campaign, cid)
    assert (c.sent_count, c.failed_count, c.status) == (3, 0, CampaignStatus.COMPLETED)


# ---------------------------------------------------------------- retry

def _exhaust_retries(db, cid):
    """A temporary failure waits as PENDING; simulate its retries running out -> FAILED."""
    for d in _deliveries(db, cid):
        if d.status == EmailDeliveryStatus.PENDING and d.error_message:
            d.status = EmailDeliveryStatus.FAILED
    db.commit()


def _prepare_send_with_failures(client, headers, s, smtp, failing=("c1@example.com",), permanent=False, db=None):
    """By default the failures are temporary (4xx), the only kind /retry requeues."""
    cid = s.campaign.id
    _prepare(s)
    for email in failing:
        (smtp.smtp_5xx if permanent else smtp.smtp_4xx)(email)
    client.post(f"/campaigns/{cid}/send", headers=headers)
    if db is not None:
        _exhaust_retries(db, cid)
    return cid


def test_retry_does_not_reenable_a_failed_sender(client, headers, scenario, db, smtp):
    cid = scenario.campaign.id
    _prepare(scenario)
    smtp.fail_auth()
    client.post(f"/campaigns/{cid}/send", headers=headers)
    db.expire_all()
    assert scenario.sender.status == SenderAccountStatus.FAILED

    client.post(f"/campaigns/{cid}/retry", headers=headers)

    db.expire_all()
    assert scenario.sender.status == SenderAccountStatus.FAILED


def test_retry_resets_failed_deliveries_to_pending(client, headers, scenario, db, smtp):
    cid = _prepare_send_with_failures(client, headers, scenario, smtp, db=db)
    r = client.post(f"/campaigns/{cid}/retry", headers=headers)

    assert r.json() == {"message": "Campaign ready for retry", "retry_count": 1}
    by_email = {d.recipient_email: d for d in _deliveries(db, cid)}
    assert by_email["c1@example.com"].status == EmailDeliveryStatus.PENDING
    assert by_email["c1@example.com"].error_message is None
    assert by_email["c1@example.com"].sent_at is None
    # successful deliveries are untouched
    assert by_email["c0@example.com"].status == EmailDeliveryStatus.SENT
    assert by_email["c0@example.com"].sent_at is not None


def test_retry_resets_campaign_to_prepared_and_zeroes_counters(client, headers, scenario, db, smtp):
    cid = _prepare_send_with_failures(client, headers, scenario, smtp, db=db)
    client.post(f"/campaigns/{cid}/retry", headers=headers)
    db.expire_all()
    c = db.get(Campaign, cid)
    assert (c.status, c.sent_count, c.failed_count) == (CampaignStatus.PREPARED, 0, 0)


def test_retry_does_not_send_anything_by_itself(client, headers, scenario, db, smtp):
    cid = _prepare_send_with_failures(client, headers, scenario, smtp, db=db)
    before = len(smtp.sent)
    client.post(f"/campaigns/{cid}/retry", headers=headers)
    assert len(smtp.sent) == before


def test_retry_then_send_delivers_only_the_previously_failed_recipient(client, headers, scenario, db, smtp):
    cid = _prepare_send_with_failures(client, headers, scenario, smtp, db=db)
    smtp.recipient_errors.clear()
    client.post(f"/campaigns/{cid}/retry", headers=headers)
    client.post(f"/campaigns/{cid}/send", headers=headers)

    assert sorted(smtp.recipients()) == ["c0@example.com", "c1@example.com", "c2@example.com"]
    assert smtp.recipients().count("c0@example.com") == 1
    db.expire_all()
    c = db.get(Campaign, cid)
    assert (c.sent_count, c.failed_count, c.status) == (3, 0, CampaignStatus.COMPLETED)


def test_retry_requeues_only_temporary_failures(db, client, headers, scenario, smtp):
    cid = scenario.campaign.id
    _prepare(scenario)
    smtp.smtp_4xx("c0@example.com")
    smtp.smtp_5xx("c1@example.com")
    client.post(f"/campaigns/{cid}/send", headers=headers)
    _exhaust_retries(db, cid)

    r = client.post(f"/campaigns/{cid}/retry", headers=headers)

    assert r.json()["retry_count"] == 1
    by_email = {d.recipient_email: d for d in _deliveries(db, cid)}
    assert by_email["c0@example.com"].status == EmailDeliveryStatus.PENDING
    assert by_email["c1@example.com"].status == EmailDeliveryStatus.FAILED
    assert by_email["c1@example.com"].error_message  # permanent failure keeps its error


def test_retry_resets_retry_metadata(db, client, headers, scenario, smtp):
    cid = _prepare_send_with_failures(client, headers, scenario, smtp, db=db)
    d = next(d for d in _deliveries(db, cid) if d.status == EmailDeliveryStatus.FAILED)
    d.attempt_count = 3
    db.commit()
    client.post(f"/campaigns/{cid}/retry", headers=headers)
    d = db.get(EmailDelivery, d.id)
    db.refresh(d)
    assert (d.attempt_count, d.claimed_at, d.next_attempt_at) == (0, None, None)


def test_retry_with_no_failed_deliveries_still_resets_campaign(client, headers, scenario, db, smtp):
    cid = scenario.campaign.id
    _prepare(scenario)
    client.post(f"/campaigns/{cid}/send", headers=headers)  # all succeed
    r = client.post(f"/campaigns/{cid}/retry", headers=headers)
    assert r.json() == {"message": "Campaign reset for retry", "retry_count": 0}
    db.expire_all()
    c = db.get(Campaign, cid)
    assert (c.status, c.sent_count, c.failed_count) == (CampaignStatus.PREPARED, 0, 0)
    # delivery rows remain SENT, so a follow-up /send would send nothing
    assert {d.status for d in _deliveries(db, cid)} == {EmailDeliveryStatus.SENT}


def test_retry_unknown_campaign_is_404(client, headers):
    assert client.post("/campaigns/999/retry", headers=headers).status_code == 404


# ---------------------------------------------------------------- deliveries listing / analytics

def test_deliveries_listing_shape_and_pagination(client, headers, scenario, smtp):
    cid = scenario.campaign.id
    _prepare(scenario)
    client.post(f"/campaigns/{cid}/send", headers=headers)

    body = client.get(f"/campaigns/{cid}/deliveries?limit=2", headers=headers).json()
    assert (body["total"], body["pages"], body["page"], body["has_next"], body["has_previous"]) == (3, 2, 1, True, False)
    assert len(body["items"]) == 2
    assert set(body["items"][0]) == {"id", "recipient_email", "status", "sent_at", "opened_at", "clicked_at", "error_message"}
    assert body["items"][0]["status"] == "sent"
    ids = [i["id"] for i in body["items"]]
    assert ids == sorted(ids, reverse=True)


def test_deliveries_listing_filters_by_status_and_search(client, headers, scenario, smtp):
    cid = scenario.campaign.id
    _prepare(scenario)
    smtp.smtp_5xx("c1@example.com")
    client.post(f"/campaigns/{cid}/send", headers=headers)

    failed = client.get(f"/campaigns/{cid}/deliveries?status=FAILED", headers=headers).json()
    assert [i["recipient_email"] for i in failed["items"]] == ["c1@example.com"]
    found = client.get(f"/campaigns/{cid}/deliveries?search=c2", headers=headers).json()
    assert [i["recipient_email"] for i in found["items"]] == ["c2@example.com"]


def test_deliveries_listing_scoped_to_owner(client, scenario, other_user, make_headers):
    r = client.get(f"/campaigns/{scenario.campaign.id}/deliveries", headers=make_headers(other_user))
    assert r.status_code == 404


def test_campaign_analytics_counts(client, headers, scenario, smtp):
    cid = scenario.campaign.id
    _prepare(scenario)
    smtp.smtp_5xx("c1@example.com")
    client.post(f"/campaigns/{cid}/send", headers=headers)
    a = client.get(f"/campaigns/{cid}/analytics", headers=headers).json()
    assert (a["total"], a["sent"], a["failed"], a["pending"], a["queued"]) == (3, 2, 1, 0, 0)
