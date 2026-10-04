"""Characterization of the campaign state transitions that exist today."""
from app.features.campaigns.delivery_service import EmailDeliveryService
from app.features.campaigns.enums import CampaignStatus
from app.features.campaigns.sender_service import CampaignSenderService
from tests.factories import Scenario


def test_campaign_status_values_that_exist_today():
    assert [s.value for s in CampaignStatus] == ["draft", "prepared", "running", "completed", "failed"]


def test_new_campaign_is_draft(db):
    assert Scenario(db).campaign.status == CampaignStatus.DRAFT


def test_draft_to_prepared_via_prepare_endpoint(client, headers, scenario, db):
    client.post(f"/campaigns/{scenario.campaign.id}/prepare", headers=headers)
    db.expire_all()
    assert scenario.campaign.status == CampaignStatus.PREPARED


def test_completed_campaign_can_be_set_back_to_prepared_by_prepare(client, db, make_headers):
    s = Scenario(db, status=CampaignStatus.COMPLETED)
    client.post(f"/campaigns/{s.campaign.id}/prepare", headers=make_headers(s.user))
    db.expire_all()
    assert s.campaign.status == CampaignStatus.PREPARED  # no transition guard


def test_prepared_to_running_to_completed(client, db, make_headers, smtp):
    s = Scenario(db)
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    s.campaign.status = CampaignStatus.PREPARED
    db.commit()
    client.post(f"/campaigns/{s.campaign.id}/send", headers=make_headers(s.user))
    db.expire_all()
    assert s.campaign.status == CampaignStatus.COMPLETED
    assert len(smtp.sent) == 3


def test_running_to_failed_when_a_delivery_fails(db, smtp):
    s = Scenario(db, n_contacts=1)
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    smtp.fail_auth()  # permanent
    CampaignSenderService(db).send_campaign(s.campaign.id)
    db.expire_all()
    assert s.campaign.status == CampaignStatus.FAILED


def test_campaign_stays_running_while_a_retry_is_waiting(db, smtp):
    s = Scenario(db, n_contacts=1)
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    smtp.fail_connect()  # temporary
    CampaignSenderService(db).send_campaign(s.campaign.id)
    db.expire_all()
    assert s.campaign.status == CampaignStatus.RUNNING


def test_campaign_update_endpoint_allows_arbitrary_status_changes(client, db, make_headers):
    """PUT /campaigns/{id} can set any status directly (no transition rules)."""
    s = Scenario(db)
    r = client.put(f"/campaigns/{s.campaign.id}", json={"status": "running"}, headers=make_headers(s.user))
    assert r.status_code == 200 and r.json()["status"] == "running"
