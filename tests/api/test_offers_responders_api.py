"""Phase 2D-3: Responder / Offer / Variant CRUD and Campaign Variant selection (API level)."""
import pytest

from app.features.campaigns.model import Campaign
from app.features.offers.model import Offer, OfferVariant
from app.features.responders.model import Responder
from tests.factories import make_user

OFFER = {"name": "N", "title": "T", "description": "D"}


def _responder(client, headers, name="R"):
    r = client.post("/responders/", json={"name": name}, headers=headers)
    assert r.status_code == 201
    return r.json()


def _offer(client, headers, responder_id=None, **extra):
    r = client.post("/offers/", json={**OFFER, "responder_id": responder_id, **extra}, headers=headers)
    assert r.status_code == 201
    return r.json()


def _variant(client, headers, parent_offer, **extra):
    body = {"name": "V", "content_type": "TEXT", "subject": "S", "body_text": "hi", **extra}
    r = client.post(f"/offers/{parent_offer}/variants", json=body, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


@pytest.fixture
def other_headers(other_user, make_headers):
    return make_headers(other_user)


# ---------------------------------------------------------------- responders

def test_responder_crud(client, headers, db, scenario):
    r = client.post("/responders/", json={"name": "Main", "user_id": 999}, headers=headers)
    assert r.status_code == 201
    rid = r.json()["id"]
    assert set(r.json()) == {"id", "name", "created_at"}
    assert db.get(Responder, rid).user_id == scenario.user.id  # never from the client

    assert [x["id"] for x in client.get("/responders/", headers=headers).json()] == [rid]
    assert client.get(f"/responders/{rid}", headers=headers).json()["name"] == "Main"

    r = client.put(f"/responders/{rid}", json={"name": "Renamed", "user_id": 999}, headers=headers)
    assert r.status_code == 200 and r.json()["name"] == "Renamed"
    assert db.get(Responder, rid).user_id == scenario.user.id

    assert client.delete(f"/responders/{rid}", headers=headers).status_code == 200
    assert client.get(f"/responders/{rid}", headers=headers).status_code == 404


def test_responder_name_required(client, headers):
    assert client.post("/responders/", json={}, headers=headers).status_code == 422
    assert client.post("/responders/", json={"name": ""}, headers=headers).status_code == 422


def test_responder_delete_blocked_when_it_has_offers(client, headers, db):
    rid = _responder(client, headers)["id"]
    offer = _offer(client, headers, rid)
    v = _variant(client, headers, offer["id"])
    r = client.delete(f"/responders/{rid}", headers=headers)
    assert r.status_code == 409
    assert db.get(Responder, rid) and db.get(Offer, offer["id"]) and db.get(OfferVariant, v["id"])


def test_responder_cross_user_denied(client, headers, other_headers):
    theirs = _responder(client, other_headers)["id"]
    assert client.get(f"/responders/{theirs}", headers=headers).status_code == 404
    assert client.put(f"/responders/{theirs}", json={"name": "x"}, headers=headers).status_code == 404
    assert client.delete(f"/responders/{theirs}", headers=headers).status_code == 404
    assert client.get("/responders/", headers=headers).json() == []
    assert client.get(f"/responders/{theirs}", headers=other_headers).json()["name"] == "R"


def test_responders_require_auth(client):
    assert client.get("/responders/").status_code in (401, 403)


# ---------------------------------------------------------------- offers

def test_offer_create_with_owned_responder_and_urls(client, headers):
    rid = _responder(client, headers)["id"]
    o = _offer(client, headers, rid, cta_url="https://cta.example/x", affiliate_url="https://aff.example/y")
    assert o["responder_id"] == rid
    assert o["cta_url"].startswith("https://cta.example/") and o["affiliate_url"].startswith("https://aff.example/")


def test_offer_create_with_other_users_responder_rejected(client, headers, other_headers, db):
    theirs = _responder(client, other_headers)["id"]
    r = client.post("/offers/", json={**OFFER, "responder_id": theirs}, headers=headers)
    assert r.status_code == 404
    assert db.query(Offer).count() == 0


def test_offer_list_get_only_own(client, headers, other_headers):
    mine = _offer(client, headers)
    theirs = _offer(client, other_headers)
    assert [o["id"] for o in client.get("/offers/", headers=headers).json()] == [mine["id"]]
    assert client.get(f"/offers/{mine['id']}", headers=headers).json()["id"] == mine["id"]
    assert client.get(f"/offers/{theirs['id']}", headers=headers).status_code == 404


def test_offer_list_responder_filter_is_ownership_safe(client, headers, other_headers):
    r1, r2 = _responder(client, headers, "a")["id"], _responder(client, headers, "b")["id"]
    o1 = _offer(client, headers, r1)
    _offer(client, headers, r2)
    theirs = _responder(client, other_headers)["id"]
    _offer(client, other_headers, theirs)
    assert [o["id"] for o in client.get(f"/offers/?responder_id={r1}", headers=headers).json()] == [o1["id"]]
    assert client.get(f"/offers/?responder_id={theirs}", headers=headers).json() == []


def test_offer_update_fields_and_responder_ownership(client, headers, other_headers):
    own2 = _responder(client, headers, "second")["id"]
    theirs = _responder(client, other_headers)["id"]
    o = _offer(client, headers, cta_url="https://cta.example/keep")
    r = client.put(f"/offers/{o['id']}", json={"affiliate_url": "https://aff.example/new", "title": "T2"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["title"] == "T2" and r.json()["affiliate_url"].startswith("https://aff.example/new")
    assert r.json()["cta_url"].startswith("https://cta.example/keep")  # untouched
    assert client.put(f"/offers/{o['id']}", json={"responder_id": own2}, headers=headers).json()["responder_id"] == own2
    assert client.put(f"/offers/{o['id']}", json={"responder_id": theirs}, headers=headers).status_code == 404


def test_offer_cross_user_update_delete_denied(client, headers, other_headers, db):
    theirs = _offer(client, other_headers)
    assert client.put(f"/offers/{theirs['id']}", json={"name": "x"}, headers=headers).status_code == 404
    assert client.delete(f"/offers/{theirs['id']}", headers=headers).status_code == 404
    assert db.get(Offer, theirs["id"]) is not None


def _snapshot(db, campaign_ids):
    db.expire_all()
    return {
        cid: (c.offer_id, c.variant_id, c.subject, c.body, c.from_name)
        for cid in campaign_ids
        for c in [db.get(Campaign, cid)]
    }


def _camp(client, headers, scenario, **over):
    r = client.post("/campaigns/", json=_campaign(scenario, **over), headers=headers)
    assert r.status_code in (200, 201), r.text
    return r.json()["id"]


def test_offer_delete_unreferenced_succeeds_and_removes_variants(client, headers, db):
    o = _offer(client, headers)
    v = _variant(client, headers, o["id"])
    assert client.delete(f"/offers/{o['id']}", headers=headers).status_code == 200
    db.expire_all()
    assert db.get(Offer, o["id"]) is None and db.get(OfferVariant, v["id"]) is None


@pytest.mark.parametrize("n", [1, 3])
def test_offer_delete_blocked_when_referenced(client, headers, scenario, db, n):
    o = _offer(client, headers)
    v = _variant(client, headers, o["id"])
    ids = [_camp(client, headers, scenario, offer_id=o["id"], variant_id=v["id"] if i == 0 else None) for i in range(n)]
    before = _snapshot(db, ids)
    assert client.delete(f"/offers/{o['id']}", headers=headers).status_code == 409
    db.expire_all()
    assert db.get(Offer, o["id"]) is not None and db.get(OfferVariant, v["id"]) is not None
    assert _snapshot(db, ids) == before


def _referenced_offer_of_other_user(client, other_headers, other_user, db):
    from tests.factories import make_campaign, make_list, make_sender

    o = _offer(client, other_headers)
    v = _variant(client, other_headers, o["id"])
    sender = make_sender(db, other_user, email="other-sender@example.com")
    camp = make_campaign(db, other_user, sender, make_list(db, other_user, []))
    camp.offer_id, camp.variant_id = o["id"], v["id"]
    db.commit()
    return o, v, camp


def test_offer_and_variant_delete_do_not_leak_other_users_references(client, headers, other_headers, other_user, db):
    ref_o, ref_v, camp = _referenced_offer_of_other_user(client, other_headers, other_user, db)
    free_o = _offer(client, other_headers)
    # referenced and unreferenced foreign offers are indistinguishable: both 404, never 409
    assert client.delete(f"/offers/{ref_o['id']}", headers=headers).status_code == 404
    assert client.delete(f"/offers/{free_o['id']}", headers=headers).status_code == 404
    assert client.delete("/offers/999999", headers=headers).status_code == 404
    assert client.delete(f"/offers/{ref_o['id']}/variants/{ref_v['id']}", headers=headers).status_code == 404
    db.expire_all()
    assert db.get(Offer, ref_o["id"]) is not None and db.get(OfferVariant, ref_v["id"]) is not None
    assert (db.get(Campaign, camp.id).offer_id, db.get(Campaign, camp.id).variant_id) == (ref_o["id"], ref_v["id"])


# ---------------------------------------------------------------- variants

@pytest.mark.parametrize(
    "extra",
    [
        {"content_type": "TEXT", "body_text": "t"},
        {"content_type": "IMAGE", "body_text": None, "image_url": "https://img.example/a.png"},
        {"content_type": "HTML", "body_text": None, "body_html": "<p>x</p>"},
        {"content_type": "TEXT_IMAGE", "body_text": "t", "image_url": "https://img.example/a.png"},
        {"content_type": "TEXT_IMAGE", "body_text": "t"},
        {"content_type": "TEXT_IMAGE", "body_text": None, "image_url": "https://img.example/a.png"},
    ],
)
def test_variant_valid_content_types(client, headers, extra):
    o = _offer(client, headers)
    v = _variant(client, headers, o["id"], **extra)
    assert v["offer_id"] == o["id"] and v["content_type"] == extra["content_type"] and v["is_active"] is True


@pytest.mark.parametrize(
    "extra",
    [
        {"content_type": "TEXT", "body_text": None},
        {"content_type": "IMAGE", "body_text": None},
        {"content_type": "HTML", "body_text": None},
        {"content_type": "TEXT_IMAGE", "body_text": None},
    ],
)
def test_variant_invalid_content_rejected(client, headers, extra, db):
    o = _offer(client, headers)
    body = {"name": "V", "subject": "S", **extra}
    assert client.post(f"/offers/{o['id']}/variants", json=body, headers=headers).status_code == 422
    assert db.query(OfferVariant).count() == 0


def test_variant_crud(client, headers):
    o = _offer(client, headers)
    oid = o["id"]
    v = _variant(client, headers, oid, offer_id=12345)  # body offer_id is ignored
    assert v["offer_id"] == oid
    vid = v["id"]
    assert [x["id"] for x in client.get(f"/offers/{oid}/variants", headers=headers).json()] == [vid]
    assert client.get(f"/offers/{oid}/variants/{vid}", headers=headers).json()["subject"] == "S"

    upd = {"name": "V2", "content_type": "HTML", "subject": "S2", "body_html": "<b>x</b>", "is_active": False}
    r = client.put(f"/offers/{oid}/variants/{vid}", json=upd, headers=headers)
    assert r.status_code == 200 and r.json()["content_type"] == "HTML" and r.json()["is_active"] is False
    bad = {**upd, "body_html": None}
    assert client.put(f"/offers/{oid}/variants/{vid}", json=bad, headers=headers).status_code == 422

    assert client.delete(f"/offers/{oid}/variants/{vid}", headers=headers).status_code == 200
    assert client.get(f"/offers/{oid}/variants/{vid}", headers=headers).status_code == 404


def test_variant_wrong_offer_in_path_is_not_found(client, headers):
    a, b = _offer(client, headers), _offer(client, headers)
    v = _variant(client, headers, a["id"])
    assert client.get(f"/offers/{b['id']}/variants/{v['id']}", headers=headers).status_code == 404
    assert client.delete(f"/offers/{b['id']}/variants/{v['id']}", headers=headers).status_code == 404


def test_variant_cross_user_denied(client, headers, other_headers, db):
    o = _offer(client, other_headers)
    v = _variant(client, other_headers, o["id"])
    base = f"/offers/{o['id']}/variants"
    body = {"name": "V", "content_type": "TEXT", "subject": "S", "body_text": "hi"}
    assert client.get(base, headers=headers).status_code == 404
    assert client.post(base, json=body, headers=headers).status_code == 404
    assert client.get(f"{base}/{v['id']}", headers=headers).status_code == 404
    assert client.put(f"{base}/{v['id']}", json={**body, "name": "hacked"}, headers=headers).status_code == 404
    assert client.delete(f"{base}/{v['id']}", headers=headers).status_code == 404
    assert db.query(OfferVariant).count() == 1 and db.get(OfferVariant, v["id"]).name == "V"


def test_variant_delete_unreferenced_succeeds(client, headers, db):
    o = _offer(client, headers)
    v = _variant(client, headers, o["id"])
    assert client.delete(f"/offers/{o['id']}/variants/{v['id']}", headers=headers).status_code == 200
    db.expire_all()
    assert db.get(OfferVariant, v["id"]) is None and db.get(Offer, o["id"]) is not None


@pytest.mark.parametrize("n", [1, 3])
def test_variant_delete_blocked_when_referenced(client, headers, scenario, db, n):
    o = _offer(client, headers)
    v = _variant(client, headers, o["id"])
    ids = [_camp(client, headers, scenario, offer_id=o["id"], variant_id=v["id"]) for _ in range(n)]
    before = _snapshot(db, ids)
    assert client.delete(f"/offers/{o['id']}/variants/{v['id']}", headers=headers).status_code == 409
    db.expire_all()
    assert db.get(OfferVariant, v["id"]) is not None
    assert _snapshot(db, ids) == before
    assert all(row[1] == v["id"] for row in before.values())


# ---------------------------------------------------------------- campaign variant selection

def _campaign(s, **over):
    data = {"sender_account_id": s.sender.id, "contact_list_id": s.list.id, "name": "C", "subject": "Hi", "body": "Body"}
    data.update(over)
    return data


def _legacy_campaign(client, headers, scenario, offer_id):
    r = client.post("/campaigns/", json=_campaign(scenario, offer_id=offer_id), headers=headers)
    assert r.status_code == 200
    return r.json()


def test_campaign_select_update_and_clear_variant(client, headers, scenario):
    o = _offer(client, headers)
    v1, v2 = _variant(client, headers, o["id"]), _variant(client, headers, o["id"], name="V2")
    c = _legacy_campaign(client, headers, scenario, o["id"])
    body_before = c["body"]
    assert "<section>" in body_before and c["variant_id"] is None

    r = client.put(f"/campaigns/{c['id']}", json={"variant_id": v1["id"]}, headers=headers)
    assert r.status_code == 200 and r.json()["variant_id"] == v1["id"]
    assert (r.json()["body"], r.json()["subject"], r.json()["name"]) == (body_before, "Hi", "C")  # content intact

    assert client.put(f"/campaigns/{c['id']}", json={"variant_id": v2["id"]}, headers=headers).json()["variant_id"] == v2["id"]
    assert client.put(f"/campaigns/{c['id']}", json={"name": "Renamed"}, headers=headers).json()["variant_id"] == v2["id"]
    r = client.put(f"/campaigns/{c['id']}", json={"variant_id": None}, headers=headers)
    assert r.status_code == 200 and r.json()["variant_id"] is None


def test_campaign_update_variant_from_other_offer_rejected(client, headers, scenario, db):
    a, b = _offer(client, headers), _offer(client, headers)
    vb = _variant(client, headers, b["id"])
    c = _legacy_campaign(client, headers, scenario, a["id"])
    assert client.put(f"/campaigns/{c['id']}", json={"variant_id": vb["id"]}, headers=headers).status_code == 400
    assert db.get(Campaign, c["id"]).variant_id is None


def test_campaign_update_other_users_variant_rejected(client, headers, other_headers, scenario, db):
    theirs = _variant(client, other_headers, _offer(client, other_headers)["id"])
    o = _offer(client, headers)
    c = _legacy_campaign(client, headers, scenario, o["id"])
    r = client.put(f"/campaigns/{c['id']}", json={"variant_id": theirs["id"]}, headers=headers)
    assert r.status_code == 400
    assert db.get(Campaign, c["id"]).variant_id is None


def test_campaign_without_offer_cannot_select_variant(client, headers, scenario):
    v = _variant(client, headers, _offer(client, headers)["id"])
    r = client.put(f"/campaigns/{scenario.campaign.id}", json={"variant_id": v["id"]}, headers=headers)
    assert r.status_code == 400


def test_inactive_variant_cannot_be_newly_selected(client, headers, scenario):
    o = _offer(client, headers)
    inactive = _variant(client, headers, o["id"], is_active=False)
    assert client.post("/campaigns/", json=_campaign(scenario, offer_id=o["id"], variant_id=inactive["id"]), headers=headers).status_code == 400
    c = _legacy_campaign(client, headers, scenario, o["id"])
    assert client.put(f"/campaigns/{c['id']}", json={"variant_id": inactive["id"]}, headers=headers).status_code == 400


def test_existing_inactive_variant_reference_is_not_broken(client, headers, scenario):
    o = _offer(client, headers)
    v = _variant(client, headers, o["id"])
    c = client.post("/campaigns/", json=_campaign(scenario, offer_id=o["id"], variant_id=v["id"]), headers=headers).json()
    upd = {"name": "V", "content_type": "TEXT", "subject": "S", "body_text": "hi", "is_active": False}
    assert client.put(f"/offers/{o['id']}/variants/{v['id']}", json=upd, headers=headers).status_code == 200
    r = client.put(f"/campaigns/{c['id']}", json={"name": "Edited", "variant_id": v["id"]}, headers=headers)
    assert r.status_code == 200 and r.json()["variant_id"] == v["id"]
    assert client.get(f"/campaigns/{c['id']}", headers=headers).json()["variant_id"] == v["id"]


def test_legacy_campaign_without_variant_unchanged(client, headers, scenario):
    r = client.put(f"/campaigns/{scenario.campaign.id}", json={"name": "New name"}, headers=headers)
    assert r.status_code == 200 and r.json()["variant_id"] is None and r.json()["body"] == "Hello there"


def test_variant_campaign_still_skips_promotion_block(client, headers, scenario):
    o = _offer(client, headers)
    v = _variant(client, headers, o["id"])
    r = client.post("/campaigns/", json=_campaign(scenario, offer_id=o["id"], variant_id=v["id"]), headers=headers)
    assert r.json()["body"] == "Body"


def test_responses_expose_no_secrets(client, headers):
    o = _offer(client, headers)
    v = _variant(client, headers, o["id"])
    assert "user_id" not in o and "user_id" not in v
    assert set(v) == {"id", "offer_id", "name", "content_type", "from_name", "subject", "body_html", "body_text", "image_url", "is_active", "created_at"}


# ---------------------------------------------------------------- Phase 2D-6 audit hardening

@pytest.mark.parametrize("extra", [
    {"content_type": "TEXT", "body_text": "  \n "},
    {"content_type": "HTML", "body_html": " \n "},
    {"content_type": "TEXT_IMAGE", "body_text": "   "},
])
def test_whitespace_only_variant_content_rejected(client, headers, extra):
    o = _offer(client, headers)
    r = client.post(f"/offers/{o['id']}/variants", json={"name": "V", "subject": "S", **extra}, headers=headers)
    assert r.status_code == 422


def test_zero_ids_never_stored_on_campaign(client, headers, scenario, db):
    o = _offer(client, headers)
    assert client.post("/campaigns/", json=_campaign(scenario, offer_id=0), headers=headers).status_code == 400
    assert client.post("/campaigns/", json=_campaign(scenario, offer_id=o["id"], variant_id=0), headers=headers).status_code == 400
    c = _legacy_campaign(client, headers, scenario, o["id"])
    assert client.put(f"/campaigns/{c['id']}", json={"variant_id": 0}, headers=headers).status_code == 400
    assert db.get(Campaign, c["id"]).variant_id is None


def test_variant_body_cannot_override_path_offer(client, headers):
    a, b = _offer(client, headers), _offer(client, headers)
    body = {"name": "V", "content_type": "TEXT", "subject": "S", "body_text": "x", "offer_id": b["id"]}
    r = client.post(f"/offers/{a['id']}/variants", json=body, headers=headers)
    assert r.status_code == 201 and r.json()["offer_id"] == a["id"]
    assert client.get(f"/offers/{b['id']}/variants", headers=headers).json() == []
