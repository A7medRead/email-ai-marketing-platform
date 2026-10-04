"""Regression: tracking pixel, click token and unsubscribe link are tied to EmailDelivery.id / Contact.id."""
import re
from urllib.parse import parse_qs, unquote, urlparse

import jwt
import pytest

from app.core.config import ALGORITHM, SECRET_KEY
from app.features.campaigns.delivery_model import EmailDelivery
from app.features.campaigns.delivery_service import EmailDeliveryService
from app.features.campaigns.sender_service import CampaignSenderService
from app.features.contacts.enums import ContactStatus
from app.features.contacts.model import Contact
from tests.factories import Scenario

TRACKING = "http://tracking.test"


def _send(db, smtp, body="Visit https://example.com/offer today", n=1):
    s = Scenario(db, n_contacts=n, body=body)
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    CampaignSenderService(db).send_campaign(s.campaign.id)
    deliveries = {d.recipient_email: d for d in db.query(EmailDelivery).all()}
    return s, deliveries


def test_tracking_pixel_uses_delivery_id(db, smtp):
    s, deliveries = _send(db, smtp)
    html = smtp.sent[0].html
    delivery = deliveries["c0@example.com"]
    assert f"{TRACKING}/track/open/{delivery.id}" in html
    assert 'width="1"' in html and 'height="1"' in html


def test_each_recipient_gets_its_own_delivery_id_in_pixel(db, smtp):
    s, deliveries = _send(db, smtp, n=3)
    for m in smtp.sent:
        assert f"/track/open/{deliveries[m.recipient].id}" in m.html


def _click_claims(html):
    m = re.search(r"/track/click\?token=([^\"'\s<]+)", html)
    assert m, html
    return jwt.decode(unquote(m.group(1)), SECRET_KEY, algorithms=[ALGORITHM])


def test_click_tracking_token_references_delivery_id_and_original_url(db, smtp):
    s, deliveries = _send(db, smtp)
    claims = _click_claims(smtp.sent[0].html)
    assert claims["delivery_id"] == deliveries["c0@example.com"].id
    assert claims["url"].startswith("https://example.com/offer")
    assert claims["purpose"] == "click"


def test_links_in_body_are_rewritten_through_tracking_url(db, smtp):
    _send(db, smtp)
    html = smtp.sent[0].html
    assert "https://example.com/offer" not in html.split("/track/click")[0].split("Visit")[-1]
    assert f"{TRACKING}/track/click?token=" in html


def test_unsubscribe_link_token_references_contact(db, smtp):
    s, _ = _send(db, smtp)
    m = re.search(r"/track/unsubscribe/([^\"'\s<]+)", smtp.sent[0].html)
    claims = jwt.decode(m.group(1), SECRET_KEY, algorithms=[ALGORITHM])
    assert claims == {"contact_id": s.contacts[0].id, "purpose": "unsubscribe"}


def test_plain_text_body_newlines_become_br(db, smtp):
    _send(db, smtp, body="line1\nline2")
    assert "line1<br>line2" in smtp.sent[0].html


def test_html_bodies_are_not_newline_converted(db, smtp):
    _send(db, smtp, body="<html><body>a\nb</body></html>")
    assert "a\nb" in smtp.sent[0].html


def test_open_endpoint_returns_png_and_records_first_open_only(client, db, smtp):
    s, deliveries = _send(db, smtp)
    did = deliveries["c0@example.com"].id
    r = client.get(f"/track/open/{did}")
    assert r.status_code == 200 and r.headers["content-type"] == "image/png"
    assert r.content.startswith(b"\x89PNG")
    db.expire_all()
    first = db.get(EmailDelivery, did).opened_at
    assert first is not None
    client.get(f"/track/open/{did}")
    db.expire_all()
    assert db.get(EmailDelivery, did).opened_at == first


def test_open_endpoint_unknown_delivery_still_returns_pixel(client):
    r = client.get("/track/open/424242")
    assert r.status_code == 200 and r.headers["content-type"] == "image/png"


def test_open_does_not_change_delivery_status(client, db, smtp):
    """Status stays SENT; OPENED/CLICKED enum values exist but are not set by tracking."""
    s, deliveries = _send(db, smtp)
    did = deliveries["c0@example.com"].id
    client.get(f"/track/open/{did}")
    db.expire_all()
    assert db.get(EmailDelivery, did).status.value == "sent"


def test_click_endpoint_redirects_and_records_click(client, db, smtp):
    s, deliveries = _send(db, smtp)
    did = deliveries["c0@example.com"].id
    token = parse_qs(urlparse(re.search(r"/track/click\?token=[^\"'\s<]+", smtp.sent[0].html).group(0)).query)["token"][0]
    r = client.get("/track/click", params={"token": token}, follow_redirects=False)
    assert r.status_code in (302, 307)
    assert r.headers["location"].startswith("https://example.com/offer")
    db.expire_all()
    assert db.get(EmailDelivery, did).clicked_at is not None


@pytest.mark.parametrize("claims", [
    {"delivery_id": 1, "url": "https://x.test", "purpose": "unsubscribe"},
    {"delivery_id": 1, "url": "javascript:alert(1)", "purpose": "click"},
])
def test_click_endpoint_rejects_wrong_purpose_or_non_http_destination(client, claims):
    token = jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)
    assert client.get("/track/click", params={"token": token}, follow_redirects=False).status_code == 400


def test_click_endpoint_rejects_garbage_and_wrongly_signed_tokens(client):
    assert client.get("/track/click", params={"token": "garbage"}).status_code == 400
    forged = jwt.encode({"delivery_id": 1, "url": "https://x.test", "purpose": "click"}, "other-key", algorithm=ALGORITHM)
    assert client.get("/track/click", params={"token": forged}).status_code == 400


def test_unsubscribe_endpoint_marks_contact_unsubscribed(client, db, smtp):
    s, _ = _send(db, smtp)
    token = re.search(r"/track/unsubscribe/([^\"'\s<]+)", smtp.sent[0].html).group(1)
    r = client.get(f"/track/unsubscribe/{token}")
    assert r.status_code == 200 and "unsubscribed successfully" in r.text
    db.expire_all()
    assert db.get(Contact, s.contacts[0].id).status == ContactStatus.UNSUBSCRIBED


def test_unsubscribe_endpoint_rejects_invalid_token_and_wrong_purpose(client):
    assert client.get("/track/unsubscribe/not-a-token").status_code == 400
    wrong = jwt.encode({"contact_id": 1, "purpose": "click"}, SECRET_KEY, algorithm=ALGORITHM)
    assert client.get(f"/track/unsubscribe/{wrong}").status_code == 400


def test_unsubscribe_unknown_contact_is_404(client):
    token = jwt.encode({"contact_id": 9999, "purpose": "unsubscribe"}, SECRET_KEY, algorithm=ALGORITHM)
    assert client.get(f"/track/unsubscribe/{token}").status_code == 404


def test_unsubscribed_contact_is_skipped_on_the_next_campaign_send(client, db, smtp):
    s, _ = _send(db, smtp, n=2)
    token = re.search(r"/track/unsubscribe/([^\"'\s<]+)", smtp.sent[0].html).group(1)
    client.get(f"/track/unsubscribe/{token}")
    smtp.sent.clear()
    from tests.factories import make_campaign
    c2 = make_campaign(db, s.user, s.sender, s.list)
    ds = EmailDeliveryService(db).create_campaign_deliveries(c2)
    assert len(ds) == 1  # unsubscribed contact excluded at preparation


# --- HTML link rewriting regression (anchor hrefs must keep the full URL) ---

def _click_urls(html):
    """Original destinations of every tracked link in the sent HTML."""
    tokens = re.findall(r"/track/click\?token=([^\"'\s<]+)", html)
    return [
        jwt.decode(unquote(t), SECRET_KEY, algorithms=[ALGORITHM])["url"] for t in tokens
    ]


@pytest.mark.parametrize("url", [
    "https://example.com/page",
    "http://example.com/page",
    "https://example.com/page?a=1&b=2",
    "https://example.com/page#section",
    "https://example.com/a%20b?q=%C3%A9#x",
    "https://affiliate.example.com/click?offer=123&aff_id=9&sub=a#top",
])
def test_html_anchor_href_keeps_complete_destination(db, smtp, url):
    _send(db, smtp, body=f'<p><a href="{url}">Go</a></p>')
    html = smtp.sent[0].html
    assert _click_urls(html) == [url]
    # Anchor stays well-formed: quoted attribute closed, link text intact.
    assert re.search(r'<a href="http://tracking\.test/track/click\?token=[^"]+">Go</a>', html)


def test_regression_href_url_is_not_cut_at_whitespace_after_the_tag(db, smtp):
    """Old regex `https?://\\S+` swallowed `">Shop` into the URL and dropped the closing quote."""
    _send(db, smtp, body='<a href="https://shop.example.com/x">Shop now</a>')
    html = smtp.sent[0].html
    assert _click_urls(html) == ["https://shop.example.com/x"]
    assert '">Shop now</a>' in html


def test_affiliate_cta_with_whitespace_in_anchor(db, smtp):
    url = "https://affiliate.example.com/click?offer=123"
    _send(db, smtp, body=f'<a href="{url}">\n    Click Here\n</a>')
    assert _click_urls(smtp.sent[0].html) == [url]
    assert "Click Here" in smtp.sent[0].html


def test_single_quoted_href_is_tracked(db, smtp):
    _send(db, smtp, body="<a href='https://example.com/q?a=1'>Go</a>")
    assert _click_urls(smtp.sent[0].html) == ["https://example.com/q?a=1"]


def test_html_escaped_ampersand_in_href_becomes_real_destination(db, smtp):
    _send(db, smtp, body='<a href="https://example.com/p?a=1&amp;b=2">Go</a>')
    assert _click_urls(smtp.sent[0].html) == ["https://example.com/p?a=1&b=2"]


def test_multiple_links_are_rewritten_independently(db, smtp):
    _send(db, smtp, body='<a href="https://example.com/one">One</a> <a href="https://example.com/two?x=1">Two</a>')
    assert _click_urls(smtp.sent[0].html) == ["https://example.com/one", "https://example.com/two?x=1"]


def test_non_http_links_and_images_are_left_alone(db, smtp):
    body = (
        '<a href="mailto:a@example.com">m</a><a href="tel:+123">t</a>'
        '<a href="javascript:void(0)">j</a><a href="#top">h</a>'
        '<img src="https://cdn.example.com/p.png">'
    )
    _send(db, smtp, body=body)
    html = smtp.sent[0].html
    for kept in ('href="mailto:a@example.com"', 'href="tel:+123"', 'href="javascript:void(0)"',
                 'href="#top"', 'src="https://cdn.example.com/p.png"'):
        assert kept in html
    assert _click_urls(html) == []


def test_plain_text_url_is_still_tracked_without_touching_surrounding_text(db, smtp):
    _send(db, smtp, body="Visit https://example.com/offer?a=1 today\nBye")
    html = smtp.sent[0].html
    assert _click_urls(html) == ["https://example.com/offer?a=1"]
    assert " today<br>Bye" in html


def test_click_endpoint_resolves_html_href_to_exact_affiliate_url(client, db, smtp):
    url = "https://affiliate.example.com/click?offer=123&aff_id=9"
    s, deliveries = _send(db, smtp, body=f'<a href="{url}">Click Here</a>')
    token = parse_qs(urlparse(re.search(r"/track/click\?token=[^\"'\s<]+", smtp.sent[0].html).group(0)).query)["token"][0]
    r = client.get("/track/click", params={"token": token}, follow_redirects=False)
    assert r.status_code in (302, 307)
    assert r.headers["location"] == url
    db.expire_all()
    assert db.get(EmailDelivery, deliveries["c0@example.com"].id).clicked_at is not None
