"""Phase 2D-8: Variant snapshot at /prepare and variant_id mutation guard."""
import pytest

from app.features.campaigns.enums import CampaignStatus
from app.features.campaigns.model import Campaign
from app.features.campaigns.sender_service import CampaignSenderService
from app.features.offers.model import OfferVariant
from tests.api.test_offers_responders_api import _campaign, _offer, _variant

IMG = "https://img.example/a.png"


def _variant_campaign(client, headers, scenario, **variant_extra):
    o = _offer(client, headers)
    v = _variant(client, headers, o["id"], from_name="Variant Name", **variant_extra)
    c = client.post("/campaigns/", json=_campaign(scenario, offer_id=o["id"], variant_id=v["id"], from_name="Camp"),
                    headers=headers).json()
    return o, v, c


def _edit_variant(client, headers, o, v, **fields):
    body = {"name": "V", "content_type": "TEXT", "subject": "S", "body_text": "hi", **fields}
    assert client.put(f"/offers/{o['id']}/variants/{v['id']}", json=body, headers=headers).status_code == 200


def _prepare(client, headers, c):
    return client.post(f"/campaigns/{c['id']}/prepare", headers=headers)


def _send(db, c):
    db.expire_all()
    return CampaignSenderService(db).send_campaign(c["id"])


# ------------------------------------------------------------ snapshot

def test_prepare_stores_snapshot_and_send_uses_it_after_variant_edits(client, headers, scenario, db, smtp):
    o, v, c = _variant_campaign(client, headers, scenario, subject="Orig subject", body_text="Orig body")
    assert _prepare(client, headers, c).status_code == 200
    db.expire_all()
    camp = db.get(Campaign, c["id"])
    assert (camp.prepared_subject, camp.prepared_from_name, camp.prepared_body) == ("Orig subject", "Variant Name", "Orig body")
    assert camp.variant_id == v["id"]  # kept for reference

    _edit_variant(client, headers, o, v, subject="NEW subject", body_text="NEW body", from_name="New Name")
    _send(db, c)

    assert len(smtp.sent) == len(scenario.contacts)
    for msg in smtp.sent:
        assert msg.subject == "Orig subject"
        assert "Variant Name" in msg.from_header and "New Name" not in msg.from_header
        assert "Orig body" in msg.html and "NEW body" not in msg.html
    db.expire_all()
    assert db.get(OfferVariant, v["id"]).subject == "NEW subject"  # the Variant itself stays editable


@pytest.mark.parametrize(
    "ctype,extra,needle",
    [
        ("TEXT", {"body_text": "Plain\nbody"}, "Plain<br>body"),
        ("IMAGE", {"image_url": IMG}, f'<img src="{IMG}" alt="">'),
        ("TEXT_IMAGE", {"body_text": "Cap", "image_url": IMG}, f'Cap<br><br><img src="{IMG}" alt="">'),
        ("HTML", {"body_html": "<p>Hi <a href=\"https://aff.example/z?a=1&b=2\">go</a></p>"}, "<p>Hi "),
    ],
)
def test_each_content_type_prepare_to_send(client, headers, scenario, db, smtp, ctype, extra, needle):
    extra = {"body_text": None, **extra}
    o, v, c = _variant_campaign(client, headers, scenario, content_type=ctype, **extra)
    assert _prepare(client, headers, c).status_code == 200
    _edit_variant(client, headers, o, v, body_text="changed")
    _send(db, c)
    msg = smtp.sent[0]
    assert needle in msg.html and "changed" not in msg.html
    assert "/track/open/" in msg.html and "Unsubscribe" in msg.html


def test_tracking_applies_to_prepared_html(client, headers, scenario, db, smtp):
    o, v, c = _variant_campaign(
        client, headers, scenario, content_type="HTML", body_text=None,
        body_html='<a href="https://aff.example/z?a=1&b=2">go</a>',
    )
    _prepare(client, headers, c)
    db.expire_all()
    assert db.get(Campaign, c["id"]).prepared_body == '<a href="https://aff.example/z?a=1&b=2">go</a>'  # untracked at rest
    _send(db, c)
    html = smtp.sent[0].html
    assert "/track/click?token=" in html and "aff.example" not in html and "/track/open/" in html


def test_campaign_draft_field_edits_do_not_replace_snapshot(client, headers, scenario, db, smtp):
    o, v, c = _variant_campaign(client, headers, scenario, subject="Snap", body_text="Snap body")
    _prepare(client, headers, c)
    r = client.put(f"/campaigns/{c['id']}", json={"subject": "Edited", "body": "Edited body", "from_name": "Zed"}, headers=headers)
    assert r.status_code == 200
    _send(db, c)
    msg = smtp.sent[0]
    assert msg.subject == "Snap" and "Snap body" in msg.html and "Edited body" not in msg.html
    assert "Variant Name" in msg.from_header


def test_repeated_prepare_and_send_do_not_rebuild_snapshot(client, headers, scenario, db, smtp):
    o, v, c = _variant_campaign(client, headers, scenario, subject="Snap", body_text="Snap body")
    _prepare(client, headers, c)
    _edit_variant(client, headers, o, v, subject="Later", body_text="Later body")
    assert _prepare(client, headers, c).json()["message"] == "Campaign already prepared"
    assert client.post(f"/campaigns/{c['id']}/send", headers=headers).status_code == 200
    client.post(f"/campaigns/{c['id']}/send", headers=headers)
    db.expire_all()
    camp = db.get(Campaign, c["id"])
    assert (camp.prepared_subject, camp.prepared_body) == ("Snap", "Snap body")
    assert {m.subject for m in smtp.sent} == {"Snap"}


def test_effective_from_name_falls_back_to_campaign_then_none(client, headers, scenario, db):
    o = _offer(client, headers)
    v = _variant(client, headers, o["id"])  # no variant from_name
    c = client.post("/campaigns/", json=_campaign(scenario, offer_id=o["id"], variant_id=v["id"], from_name="Camp"), headers=headers).json()
    _prepare(client, headers, c)
    db.expire_all()
    assert db.get(Campaign, c["id"]).prepared_from_name == "Camp"


def test_prepare_rejects_invalid_variant_without_deliveries(client, headers, scenario, db):
    o, v, c = _variant_campaign(client, headers, scenario)
    db.query(OfferVariant).filter_by(id=v["id"]).update({"body_text": None})  # corrupt the stored variant
    db.commit()
    r = _prepare(client, headers, c)
    assert r.status_code == 400
    db.expire_all()
    camp = db.get(Campaign, c["id"])
    assert camp.status == CampaignStatus.DRAFT and camp.prepared_body is None
    assert client.get(f"/campaigns/{c['id']}/deliveries", headers=headers).json().get("total", 0) == 0


# ------------------------------------------------------------ variant_id mutation

def test_draft_campaign_can_change_variant(client, headers, scenario):
    o, v, c = _variant_campaign(client, headers, scenario)
    v2 = _variant(client, headers, o["id"], name="V2")
    r = client.put(f"/campaigns/{c['id']}", json={"variant_id": v2["id"]}, headers=headers)
    assert r.status_code == 200 and r.json()["variant_id"] == v2["id"]


@pytest.mark.parametrize(
    "status",
    [CampaignStatus.PREPARED, CampaignStatus.RUNNING, CampaignStatus.COMPLETED, CampaignStatus.FAILED],
)
def test_non_draft_campaign_cannot_change_or_clear_variant(client, headers, scenario, db, status):
    o, v, c = _variant_campaign(client, headers, scenario)
    v2 = _variant(client, headers, o["id"], name="V2")
    db.query(Campaign).filter_by(id=c["id"]).update({"status": status})
    db.commit()
    for payload in ({"variant_id": v2["id"]}, {"variant_id": None}):
        r = client.put(f"/campaigns/{c['id']}", json=payload, headers=headers)
        assert r.status_code == 400 and "draft" in r.json()["detail"]
    db.expire_all()
    assert db.get(Campaign, c["id"]).variant_id == v["id"]
    # resending the same value, or editing other fields, is not a change
    assert client.put(f"/campaigns/{c['id']}", json={"variant_id": v["id"], "name": "N"}, headers=headers).status_code == 200


def test_prepared_campaign_variant_and_snapshot_unchanged_after_rejected_change(client, headers, scenario, db):
    o, v, c = _variant_campaign(client, headers, scenario, subject="Snap", body_text="Snap body")
    v2 = _variant(client, headers, o["id"], name="V2", subject="Other")
    _prepare(client, headers, c)
    assert client.put(f"/campaigns/{c['id']}", json={"variant_id": v2["id"]}, headers=headers).status_code == 400
    db.expire_all()
    camp = db.get(Campaign, c["id"])
    assert camp.variant_id == v["id"] and camp.prepared_subject == "Snap" and camp.status == CampaignStatus.PREPARED


def test_draft_with_existing_snapshot_cannot_change_variant(client, headers, scenario, db):
    # A status forced back to draft must not allow detaching the Variant from its snapshot.
    o, v, c = _variant_campaign(client, headers, scenario)
    v2 = _variant(client, headers, o["id"], name="V2")
    _prepare(client, headers, c)
    assert client.put(f"/campaigns/{c['id']}", json={"status": "draft"}, headers=headers).status_code == 200
    assert client.put(f"/campaigns/{c['id']}", json={"variant_id": v2["id"]}, headers=headers).status_code == 400


# ------------------------------------------------------------ legacy

def test_legacy_campaign_has_no_snapshot_and_keeps_promotion_block(client, headers, scenario, db, smtp):
    o = _offer(client, headers, cta_url="https://cta.example/c")
    c = client.post("/campaigns/", json=_campaign(scenario, offer_id=o["id"]), headers=headers).json()
    assert "<section>" in c["body"]
    _prepare(client, headers, c)
    db.expire_all()
    camp = db.get(Campaign, c["id"])
    assert camp.prepared_body is None and camp.prepared_subject is None and camp.variant_id is None
    client.put(f"/campaigns/{c['id']}", json={"subject": "Changed later"}, headers=headers)
    _send(db, c)
    assert smtp.sent[0].subject == "Changed later" and "<section>" in smtp.sent[0].html
