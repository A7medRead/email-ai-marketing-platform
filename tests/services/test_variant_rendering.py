"""Phase 2D-4: OfferVariant rendering and its use by the existing sending path."""
import socket

import pytest

from app.features.campaigns.delivery_model import EmailDelivery, EmailDeliveryStatus
from app.features.campaigns.delivery_service import EmailDeliveryService
from app.features.campaigns.sender_service import CampaignSenderService
from app.features.offers.enums import VariantContentType as CT
from app.features.offers.model import Offer, OfferVariant
from app.features.offers.renderer import render_campaign_email, render_variant
from tests.factories import Scenario

IMG = "https://img.example/a.png"


def _variant(offer_id=1, ctype=CT.TEXT, **extra):
    data = {"offer_id": offer_id, "name": "V", "content_type": ctype, "subject": "Variant subject", **extra}
    return OfferVariant(**data)


# ---------------------------------------------------------------- renderer

def test_text_variant_escapes_and_keeps_newlines():
    subject, from_name, html = render_variant(_variant(body_text="Hi <b>there</b>\nline2 {{first_name}}", from_name="Brand"))
    assert subject == "Variant subject" and from_name == "Brand"
    assert html == "Hi &lt;b&gt;there&lt;/b&gt;\nline2 {{first_name}}"  # no personalization, newlines left to SMTP layer


def test_empty_from_name_is_none():
    assert render_variant(_variant(body_text="x", from_name=""))[1] is None


def test_image_variant_and_no_network(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("renderer must not touch the network")

    monkeypatch.setattr(socket, "socket", boom)
    _, _, html = render_variant(_variant(ctype=CT.IMAGE, image_url=IMG + '?a=1&b="2"'))
    assert html == '<img src="https://img.example/a.png?a=1&amp;b=&quot;2&quot;" alt="">'


@pytest.mark.parametrize(
    "extra,expected",
    [
        ({"body_text": "Hello"}, "Hello"),
        ({"image_url": IMG}, f'<img src="{IMG}" alt="">'),
        ({"body_text": "Hello", "image_url": IMG}, f'Hello\n\n<img src="{IMG}" alt="">'),
    ],
)
def test_text_image_variant_all_cases(extra, expected):
    assert render_variant(_variant(ctype=CT.TEXT_IMAGE, **extra))[2] == expected


def test_html_variant_is_preserved_untouched():
    html = '<html><body><p style="x">Hi &amp; <a href="https://aff.example/z?a=1&b=2">go</a></p></body></html>\n'
    assert render_variant(_variant(ctype=CT.HTML, body_html=html, body_text="ignored"))[2] == html


@pytest.mark.parametrize(
    "ctype,extra",
    [(CT.TEXT, {}), (CT.IMAGE, {"body_text": "x"}), (CT.HTML, {"body_text": "x"}), (CT.TEXT_IMAGE, {})],
)
def test_invalid_variant_state_raises(ctype, extra):
    with pytest.raises(ValueError):
        render_variant(_variant(ctype=ctype, **extra))


# ---------------------------------------------------------------- campaign resolution / sending

def _setup(db, ctype=CT.TEXT, variant_from="Variant Name", campaign_from="Campaign Name", s=None, **extra):
    s = s or Scenario(db, n_contacts=1, subject="Campaign subject", body="Campaign body", from_name=campaign_from)
    offer = Offer(user_id=s.user.id, name="O", title="Promo", description="Legacy promo", cta_url="https://cta.example/c")
    db.add(offer)
    db.commit()
    variant = OfferVariant(
        offer_id=offer.id, name="V", content_type=ctype, subject="Variant subject",
        from_name=variant_from, **({"body_text": "Variant body"} | extra),
    )
    db.add(variant)
    db.commit()
    s.offer, s.variant = offer, variant
    return s


def _send(db, s, smtp):
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    CampaignSenderService(db).send_campaign(s.campaign.id)
    return smtp.sent


def test_legacy_campaign_sends_campaign_fields_unchanged(db, smtp):
    s = _setup(db)
    s.campaign.offer_id = s.offer.id  # offer without variant: no rendering involved
    db.commit()
    assert render_campaign_email(db, s.campaign).html == "Campaign body"
    msg = _send(db, s, smtp)[0]
    assert msg.subject == "Campaign subject" and "Campaign body" in msg.html
    assert "Campaign Name" in msg.from_header and "Variant" not in msg.html


def test_variant_campaign_sends_variant_content(db, smtp):
    s = _setup(db)
    s.campaign.offer_id, s.campaign.variant_id = s.offer.id, s.variant.id
    db.commit()
    msg = _send(db, s, smtp)[0]
    assert msg.subject == "Variant subject"
    assert "Variant Name" in msg.from_header and "Campaign Name" not in msg.from_header
    assert "Variant body" in msg.html and "Campaign body" not in msg.html
    assert "Legacy promo" not in msg.html and "Promo" not in msg.html  # no legacy promotion block
    assert "tracking.test/track/open/" in msg.html and "Unsubscribe" in msg.html  # SMTP layer still wraps it


def test_variant_without_from_name_falls_back_to_campaign_then_sender(db, smtp):
    s = _setup(db, variant_from=None)
    s.campaign.offer_id, s.campaign.variant_id = s.offer.id, s.variant.id
    db.commit()
    assert "Campaign Name" in _send(db, s, smtp)[0].from_header
    assert s.campaign.prepared_from_name == "Campaign Name"  # snapshotted by prepare
    s.campaign.from_name, s.campaign.prepared_body = None, None  # un-prepared again: live fallback path
    db.commit()
    assert render_campaign_email(db, s.campaign).from_name is None  # sender account name used by the sender


def test_variant_newlines_become_br_via_existing_smtp_behavior(db, smtp):
    s = _setup(db, body_text="a\nb")
    s.campaign.offer_id, s.campaign.variant_id = s.offer.id, s.variant.id
    db.commit()
    assert "a<br>b" in _send(db, s, smtp)[0].html


def test_variant_affiliate_link_in_html_reaches_existing_click_tracking(db, smtp):
    s = _setup(db, ctype=CT.HTML, body_text=None, body_html='<p><a href="https://aff.example/z">go</a></p>')
    s.campaign.offer_id, s.campaign.variant_id = s.offer.id, s.variant.id
    db.commit()
    html = _send(db, s, smtp)[0].html
    assert "/track/click?token=" in html  # unchanged existing tracking; no new tracking logic


def test_invalid_variant_is_rejected_at_prepare_and_creates_no_deliveries(db, smtp):
    s = _setup(db, ctype=CT.HTML, body_text=None)  # HTML without body_html
    s.campaign.offer_id, s.campaign.variant_id = s.offer.id, s.variant.id
    db.commit()
    with pytest.raises(ValueError):
        EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    db.rollback()
    assert db.query(EmailDelivery).filter_by(campaign_id=s.campaign.id).count() == 0
    assert s.campaign.prepared_body is None and smtp.sent == []


def test_mismatched_offer_variant_cannot_reach_rendering_via_api(client, headers, scenario, db, smtp):
    s = _setup(db, s=scenario)
    other = Offer(user_id=s.user.id, name="O2", title="T", description="D")
    db.add(other)
    db.commit()
    payload = {"sender_account_id": s.sender.id, "contact_list_id": s.list.id, "name": "C",
               "subject": "S", "body": "B", "offer_id": other.id, "variant_id": s.variant.id}
    assert client.post("/campaigns/", json=payload, headers=headers).status_code == 400
    # and the renderer itself refuses an inconsistent row
    s.campaign.offer_id, s.campaign.variant_id = other.id, s.variant.id
    db.commit()
    with pytest.raises(ValueError):
        render_campaign_email(db, s.campaign)
