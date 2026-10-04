"""Regression: the worker-side wrappers around the scheduler service."""
from datetime import datetime, timedelta

from app.features.campaigns.enums import CampaignStatus
from app.features.campaigns.model import Campaign
from app.workers import campaign_scheduler
from tests.factories import Scenario


def test_run_campaign_scheduler_uses_its_own_session_and_sends_due_campaigns(db, session_factory, smtp, monkeypatch):
    monkeypatch.setattr(campaign_scheduler, "SessionLocal", session_factory)
    s = Scenario(db, scheduled_at=datetime.utcnow() - timedelta(minutes=1))

    campaign_scheduler.run_campaign_scheduler()

    assert len(smtp.sent) == 3
    db.expire_all()
    assert db.get(Campaign, s.campaign.id).status == CampaignStatus.COMPLETED


def test_run_campaign_scheduler_closes_its_session(session_factory, smtp, monkeypatch):
    closed = []

    def factory():
        session = session_factory()
        original = session.close
        session.close = lambda: (closed.append(True), original())[1]
        return session

    monkeypatch.setattr(campaign_scheduler, "SessionLocal", factory)
    campaign_scheduler.run_campaign_scheduler()
    assert closed == [True]


def test_start_scheduler_registers_one_minute_interval_job(monkeypatch):
    started = []
    monkeypatch.setattr(campaign_scheduler.scheduler, "start", lambda: started.append(True))
    try:
        campaign_scheduler.start_scheduler()
        job = campaign_scheduler.scheduler.get_job("campaign_scheduler")
        assert job is not None
        assert job.trigger.interval == timedelta(minutes=1)
        assert job.func is campaign_scheduler.run_campaign_scheduler
        assert started == [True]
    finally:
        campaign_scheduler.scheduler.remove_all_jobs()
