"""Regression: scheduled-campaign path (CampaignSchedulerService)."""
from datetime import datetime, timedelta

from app.features.campaigns.delivery_model import EmailDelivery, EmailDeliveryStatus
from app.features.campaigns.enums import CampaignStatus
from app.features.campaigns.model import Campaign
from app.features.campaigns.scheduler_service import CampaignSchedulerService
from tests.factories import Scenario

PAST = lambda: datetime.utcnow() - timedelta(minutes=5)
FUTURE = lambda: datetime.utcnow() + timedelta(hours=1)


def test_scheduler_detects_due_draft_campaign_prepares_and_sends_it(db, smtp):
    s = Scenario(db, n_contacts=2, scheduled_at=PAST())

    results = CampaignSchedulerService(db).run_scheduled_campaigns()

    assert results == [{"campaign_id": s.campaign.id, "result": {"sent": 2, "failed": 0}}]
    assert sorted(smtp.recipients()) == ["c0@example.com", "c1@example.com"]
    db.expire_all()
    c = db.get(Campaign, s.campaign.id)
    assert (c.status, c.sent_count, c.failed_count) == (CampaignStatus.COMPLETED, 2, 0)
    assert {d.status for d in db.query(EmailDelivery).all()} == {EmailDeliveryStatus.SENT}


def test_scheduler_creates_deliveries_with_campaign_sender(db, smtp):
    s = Scenario(db, scheduled_at=PAST())
    CampaignSchedulerService(db).run_scheduled_campaigns()
    assert {d.sender_account_id for d in db.query(EmailDelivery).all()} == {s.sender.id}


def test_scheduler_marks_campaign_failed_when_a_send_fails(db, smtp):
    s = Scenario(db, n_contacts=2, scheduled_at=PAST())
    smtp.smtp_5xx("c0@example.com")
    CampaignSchedulerService(db).run_scheduled_campaigns()
    db.expire_all()
    c = db.get(Campaign, s.campaign.id)
    assert (c.status, c.sent_count, c.failed_count) == (CampaignStatus.FAILED, 1, 1)


def test_scheduler_ignores_future_campaigns(db, smtp):
    s = Scenario(db, scheduled_at=FUTURE())
    assert CampaignSchedulerService(db).run_scheduled_campaigns() == []
    assert smtp.sent == []
    db.expire_all()
    assert db.get(Campaign, s.campaign.id).status == CampaignStatus.DRAFT


def test_scheduler_ignores_draft_campaigns_without_schedule(db, smtp):
    Scenario(db, scheduled_at=None)
    assert CampaignSchedulerService(db).run_scheduled_campaigns() == []


def test_scheduler_only_picks_draft_so_prepared_scheduled_campaigns_are_never_sent(db, smtp):
    """Known gap: a campaign the user has already 'prepared' is skipped by the scheduler."""
    s = Scenario(db, scheduled_at=PAST(), status=CampaignStatus.PREPARED)
    assert CampaignSchedulerService(db).run_scheduled_campaigns() == []
    assert smtp.sent == []


def test_scheduler_ignores_running_and_completed_campaigns(db, smtp):
    Scenario(db, scheduled_at=PAST(), status=CampaignStatus.RUNNING)
    assert CampaignSchedulerService(db).run_scheduled_campaigns() == []


def test_scheduler_second_run_does_not_resend(db, smtp):
    Scenario(db, scheduled_at=PAST())
    service = CampaignSchedulerService(db)
    service.run_scheduled_campaigns()
    assert service.run_scheduled_campaigns() == []
    assert len(smtp.sent) == 3


def test_scheduler_processes_multiple_due_campaigns_sequentially(db, smtp):
    from tests.factories import make_campaign
    s = Scenario(db, n_contacts=1, scheduled_at=PAST())
    make_campaign(db, s.user, s.sender, s.list, scheduled_at=PAST())
    results = CampaignSchedulerService(db).run_scheduled_campaigns()
    assert len(results) == 2
    assert smtp.recipients() == ["c0@example.com", "c0@example.com"]  # same contact, two campaigns


def test_scheduler_endpoint_processes_the_callers_own_due_campaigns(client, db, smtp, make_headers):
    s = Scenario(db, scheduled_at=PAST())
    r = client.post("/campaigns/scheduler/run", headers=make_headers(s.user))
    assert r.status_code == 200
    assert r.json() == [{"campaign_id": s.campaign.id, "result": {"sent": 3, "failed": 0}}]
    db.expire_all()
    assert db.get(Campaign, s.campaign.id).status == CampaignStatus.COMPLETED


def test_scheduler_endpoint_does_not_process_another_users_campaigns(client, db, smtp, other_user, make_headers):
    s = Scenario(db, scheduled_at=PAST())  # owned by s.user, not other_user
    r = client.post("/campaigns/scheduler/run", headers=make_headers(other_user))
    assert r.status_code == 200
    assert r.json() == []
    assert smtp.sent == []
    db.expire_all()
    assert db.get(Campaign, s.campaign.id).status == CampaignStatus.DRAFT


def test_scheduler_service_user_filter_leaves_other_users_campaigns_due(db, smtp, other_user):
    s = Scenario(db, scheduled_at=PAST())
    assert CampaignSchedulerService(db).run_scheduled_campaigns(user_id=other_user.id) == []
    assert len(CampaignSchedulerService(db).run_scheduled_campaigns()) == 1  # worker path: all users
