"""Offers & Responders backend foundation (Phase 2D-2)."""
import importlib.util
import sqlite3
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.exc import IntegrityError

from app.features.campaigns.model import Campaign
from app.features.offers.enums import VariantContentType as CT
from app.features.offers.model import Offer, OfferVariant
from app.features.offers.schemas import OfferVariantCreate
from app.features.offers.service import OfferService
from app.features.responders.model import Responder
from app.features.responders.schemas import ResponderCreate
from app.features.responders.service import ResponderService
from tests.factories import make_user

ROOT = Path(__file__).resolve().parents[2]


def _offer(db, user, responder=None, **extra):
    offer = Offer(
        user_id=user.id,
        responder_id=responder.id if responder else None,
        name="O",
        title="T",
        description="D",
        **extra,
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer


def _responder(db, user, name="R"):
    return ResponderService(db).create(user.id, ResponderCreate(name=name))


def _variant(db, offer, content_type=CT.TEXT, **extra):
    data = {"name": "V", "content_type": content_type, "subject": "S", "body_text": "hi", **extra}
    return OfferService(db).create_variant(offer.id, offer.user_id, OfferVariantCreate(**data))


# ---------------------------------------------------------------- responder / offer / variant models

def test_user_can_own_multiple_responders(db, scenario):
    a, b = _responder(db, scenario.user, "A"), _responder(db, scenario.user, "B")
    assert {a.user_id, b.user_id} == {scenario.user.id}
    assert db.query(Responder).filter_by(user_id=scenario.user.id).count() == 2


def test_offer_belongs_to_responder_with_affiliate_and_cta_urls(db, scenario):
    r = _responder(db, scenario.user)
    offer = _offer(db, scenario.user, r, cta_url="https://cta.example/x", affiliate_url="https://aff.example/y?a=1&b=2")
    db.refresh(offer)
    assert offer.responder.id == r.id
    assert (offer.cta_url, offer.affiliate_url) == ("https://cta.example/x", "https://aff.example/y?a=1&b=2")


def test_offer_has_multiple_variants_of_different_types(db, scenario):
    offer = _offer(db, scenario.user, _responder(db, scenario.user))
    _variant(db, offer, CT.TEXT)
    _variant(db, offer, CT.HTML, body_html="<p>x</p>", body_text=None)
    _variant(db, offer, CT.IMAGE, image_url="https://img.example/a.png", body_text=None)
    _variant(db, offer, CT.TEXT_IMAGE, image_url="https://img.example/a.png")
    db.refresh(offer)
    assert sorted(v.content_type.value for v in offer.variants) == ["HTML", "IMAGE", "TEXT", "TEXT_IMAGE"]
    assert {v.offer_id for v in offer.variants} == {offer.id}


@pytest.mark.parametrize(
    "ctype,extra",
    [
        (CT.TEXT, {"body_text": None}),
        (CT.IMAGE, {"body_text": None}),
        (CT.TEXT_IMAGE, {"body_text": None}),  # neither text nor image
        (CT.HTML, {"body_text": None}),
    ],
)
def test_variant_requires_content_for_its_type(ctype, extra):
    with pytest.raises(ValueError):
        OfferVariantCreate(name="V", content_type=ctype, subject="S", **extra)


@pytest.mark.parametrize(
    "extra",
    [
        {"body_text": "only text"},
        {"body_text": None, "image_url": "https://img.example/a.png"},
        {"body_text": "both", "image_url": "https://img.example/a.png"},
    ],
)
def test_text_image_variant_accepts_text_image_or_both(extra):
    assert OfferVariantCreate(name="V", content_type=CT.TEXT_IMAGE, subject="S", **extra)


# ---------------------------------------------------------------- responder deletion

def test_responder_with_offers_cannot_be_deleted_and_offers_survive(db, scenario):
    r = _responder(db, scenario.user)
    offer = _offer(db, scenario.user, r)
    with pytest.raises(ValueError):
        ResponderService(db).delete(r.id, scenario.user.id)
    db.expire_all()
    assert db.get(Responder, r.id) is not None
    assert db.get(Offer, offer.id).responder_id == r.id


def test_empty_responder_can_be_deleted(db, scenario):
    r = _responder(db, scenario.user)
    ResponderService(db).delete(r.id, scenario.user.id)
    assert db.get(Responder, r.id) is None


# ---------------------------------------------------------------- campaign consistency

def _campaign_payload(s, **over):
    data = {
        "sender_account_id": s.sender.id,
        "contact_list_id": s.list.id,
        "name": "C",
        "subject": "Hello",
        "body": "Body",
    }
    data.update(over)
    return data


def test_campaign_with_offer_and_matching_variant(client, headers, scenario, db):
    offer = _offer(db, scenario.user, _responder(db, scenario.user))
    variant = _variant(db, offer)
    r = client.post("/campaigns/", json=_campaign_payload(scenario, offer_id=offer.id, variant_id=variant.id), headers=headers)
    assert r.status_code == 200
    assert (r.json()["offer_id"], r.json()["variant_id"]) == (offer.id, variant.id)


def test_legacy_campaign_without_variant_gets_promotion_block(client, headers, scenario, db):
    offer = _offer(db, scenario.user, _responder(db, scenario.user))
    r = client.post("/campaigns/", json=_campaign_payload(scenario, offer_id=offer.id), headers=headers)
    assert r.status_code == 200
    assert r.json()["body"] == "Body\n<hr><section><h2>T</h2><p>D</p></section>"


def test_campaign_with_variant_does_not_get_promotion_block(client, headers, scenario, db):
    offer = _offer(db, scenario.user, _responder(db, scenario.user))
    variant = _variant(db, offer)
    r = client.post("/campaigns/", json=_campaign_payload(scenario, offer_id=offer.id, variant_id=variant.id), headers=headers)
    assert r.status_code == 200
    assert r.json()["body"] == "Body"


def test_campaign_variant_must_belong_to_campaign_offer(client, headers, scenario, db):
    r1 = _responder(db, scenario.user)
    offer_a, offer_b = _offer(db, scenario.user, r1), _offer(db, scenario.user, r1)
    variant_b = _variant(db, offer_b)
    r = client.post("/campaigns/", json=_campaign_payload(scenario, offer_id=offer_a.id, variant_id=variant_b.id), headers=headers)
    assert r.status_code == 400
    assert db.query(Campaign).filter(Campaign.variant_id == variant_b.id).count() == 0


def test_campaign_variant_without_offer_rejected(client, headers, scenario, db):
    variant = _variant(db, _offer(db, scenario.user, _responder(db, scenario.user)))
    r = client.post("/campaigns/", json=_campaign_payload(scenario, variant_id=variant.id), headers=headers)
    assert r.status_code == 400


def test_campaign_without_variant_still_works(client, headers, scenario, db):
    r = client.post("/campaigns/", json=_campaign_payload(scenario), headers=headers)
    assert r.status_code == 200 and r.json()["variant_id"] is None
    assert client.get(f"/campaigns/{scenario.campaign.id}", headers=headers).json()["variant_id"] is None


# ---------------------------------------------------------------- ownership / isolation

def test_cross_user_access_is_denied(client, headers, scenario, db, other_user, make_headers):
    their_resp = _responder(db, other_user)
    their_offer = _offer(db, other_user, their_resp)
    their_variant = _variant(db, their_offer)

    with pytest.raises(ValueError):
        ResponderService(db).get_owned(their_resp.id, scenario.user.id)
    with pytest.raises(ValueError):
        OfferService(db).get_owned(their_offer.id, scenario.user.id)
    with pytest.raises(ValueError):
        OfferService(db).get_owned_variant(their_variant.id, scenario.user.id)
    with pytest.raises(ValueError):
        OfferService(db).create_variant(their_offer.id, scenario.user.id, OfferVariantCreate(
            name="V", content_type=CT.TEXT, subject="S", body_text="x"))
    with pytest.raises(ValueError):
        ResponderService(db).delete(their_resp.id, scenario.user.id)

    body = {"name": "N", "title": "T", "description": "D", "responder_id": their_resp.id}
    assert client.post("/offers/", json=body, headers=headers).status_code == 404
    mine = client.post("/offers/", json={**body, "responder_id": None}, headers=headers).json()
    assert client.put(f"/offers/{mine['id']}", json={"responder_id": their_resp.id}, headers=headers).status_code == 404
    assert client.put(f"/offers/{their_offer.id}", json={"name": "x"}, headers=headers).status_code == 404

    r = client.post(
        "/campaigns/",
        json=_campaign_payload(scenario, offer_id=mine["id"], variant_id=their_variant.id),
        headers=headers,
    )
    assert r.status_code == 400


# ---------------------------------------------------------------- offers API (backward compatible)

def test_offer_api_new_fields_and_default_responder(client, headers, db):
    body = {"name": "N", "title": "T", "description": "D", "cta_url": "https://cta.example/a",
            "affiliate_url": "https://aff.example/b?x=1"}
    r = client.post("/offers/", json=body, headers=headers)
    assert r.status_code == 201
    out = r.json()
    assert out["cta_url"].startswith("https://cta.example/")
    assert out["affiliate_url"].startswith("https://aff.example/b?x=1")
    assert out["responder_id"] is not None
    second = client.post("/offers/", json=body, headers=headers).json()
    assert second["responder_id"] == out["responder_id"]  # default responder is reused, not duplicated


def test_legacy_offer_without_responder_still_loads(client, headers, scenario, db):
    legacy = _offer(db, scenario.user, None, cta_url="https://cta.example/legacy")
    rows = client.get("/offers/", headers=headers).json()
    row = next(o for o in rows if o["id"] == legacy.id)
    assert row["responder_id"] is None and row["affiliate_url"] is None
    assert row["cta_url"].startswith("https://cta.example/legacy")


# ---------------------------------------------------------------- migration / backfill

def _alembic(url):
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


def test_migration_backfills_default_responders(tmp_path):
    path = tmp_path / "mig.db"
    cfg = _alembic(f"sqlite:///{path}")

    # The historical chain cannot be replayed from an empty database, so build the
    # pre-migration schema (only the tables this migration touches) and stamp it.
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR NOT NULL, email VARCHAR NOT NULL, password VARCHAR NOT NULL);
        CREATE TABLE offers (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(160) NOT NULL, title VARCHAR(200) NOT NULL, description TEXT NOT NULL,
            discount VARCHAR(80), coupon_code VARCHAR(80), starts_at DATETIME, expires_at DATETIME,
            cta_label VARCHAR(80), cta_url VARCHAR(2048),
            created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL
        );
        CREATE TABLE campaigns (
            id INTEGER PRIMARY KEY, name VARCHAR(255) NOT NULL,
            offer_id INTEGER, CONSTRAINT fk_campaigns_offer_id_offers FOREIGN KEY(offer_id) REFERENCES offers(id) ON DELETE SET NULL
        );
        INSERT INTO campaigns (id, name) VALUES (1, 'legacy campaign');
        """
    )
    con.commit()
    con.close()
    command.stamp(cfg, "b2c3d4e5f6a7")

    con = sqlite3.connect(path)
    now = "2026-01-01 00:00:00"
    for uid in (1, 2, 3):
        con.execute("INSERT INTO users (id, name, email, password) VALUES (?, 'U', ?, 'x')", (uid, f"u{uid}@x.com"))
    for oid, uid in ((1, 1), (2, 1), (3, 2)):  # user 3 has no offers
        con.execute(
            "INSERT INTO offers (id, user_id, name, title, description, cta_url, created_at, updated_at) "
            "VALUES (?, ?, 'n', 't', 'd', 'https://cta.example', ?, ?)",
            (oid, uid, now, now),
        )
    con.commit()
    con.close()

    # Pinned: the stub schema above only covers the responders chain, not the later reconciliation.
    command.upgrade(cfg, "d4e5f6a7b8c9")

    con = sqlite3.connect(path)
    responders = con.execute("SELECT id, user_id, name FROM responders ORDER BY user_id").fetchall()
    assert [r[1] for r in responders] == [1, 2, 3]  # exactly one per user, none duplicated
    by_user = {r[1]: r[0] for r in responders}
    offers = dict(con.execute("SELECT id, responder_id FROM offers").fetchall())
    assert offers == {1: by_user[1], 2: by_user[1], 3: by_user[2]}
    assert con.execute("SELECT cta_url, affiliate_url FROM offers WHERE id=1").fetchone() == ("https://cta.example", None)

    # Re-running the backfill must be a no-op (no duplicates, no reassignment).
    spec = importlib.util.spec_from_file_location(
        "mig", ROOT / "alembic/versions/c3d4e5f6a7b8_add_responders_and_offer_variants.py"
    )
    mig = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mig)
    from sqlalchemy import create_engine
    eng = create_engine(f"sqlite:///{path}")
    with eng.begin() as conn:
        mig.backfill_default_responders(conn)
    assert con.execute("SELECT COUNT(*) FROM responders").fetchone()[0] == 3
    con.close()
    eng.dispose()

    con = sqlite3.connect(path)
    assert con.execute("SELECT name, variant_id FROM campaigns").fetchall() == [("legacy campaign", None)]
    con.close()

    command.downgrade(cfg, "b2c3d4e5f6a7")
    command.upgrade(cfg, "d4e5f6a7b8c9")
