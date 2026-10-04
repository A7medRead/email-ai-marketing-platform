"""Phase 2D-5: Affiliate/Variant links go through the existing click tracker with exact destinations."""
import re
from urllib.parse import parse_qs, unquote, urlparse

import jwt
import pytest

from app.core.config import ALGORITHM, SECRET_KEY
from app.features.campaigns.delivery_service import EmailDeliveryService
from app.features.campaigns.sender_service import CampaignSenderService
from app.features.offers.enums import VariantContentType as CT
from app.features.offers.model import Offer, OfferVariant
from tests.factories import Scenario

IMG = "https://cdn.example.com/p.png"


def _variant_send(db, smtp, ctype, affiliate_url=None, cta_url=None, **fields):
    s = Scenario(db, n_contacts=1, subject="Campaign subject", body="LEGACY BODY")
    offer = Offer(user_id=s.user.id, name="O", title="Promo", description="d",
                  affiliate_url=affiliate_url, cta_url=cta_url)
    db.add(offer)
    db.commit()
    variant = OfferVariant(offer_id=offer.id, name="V", content_type=ctype, subject="VS", **fields)
    db.add(variant)
    db.commit()
    s.campaign.offer_id, s.campaign.variant_id = offer.id, variant.id
    db.commit()
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    CampaignSenderService(db).send_campaign(s.campaign.id)
    return s, smtp.sent[0].html


def _tokens(html):
    return [unquote(t) for t in re.findall(r"/track/click\?token=([^\"'\s<]+)", html)]


def _urls(html):
    return [jwt.decode(t, SECRET_KEY, algorithms=[ALGORITHM])["url"] for t in _tokens(html)]


URLS = [
    "https://example.com/path",
    "http://example.com/path",
    "https://example.com/path?utm_source=x&utm_campaign=y",
    "https://example.com/path?a=1&b=2",
    "https://example.com/path#section",
    "https://example.com/path%20encoded",
    "https://aff.example.com/click?aff_id=123&subid=abc&click_id=Zx9&utm_medium=email#top",
]


@pytest.mark.parametrize("url", URLS)
def test_variant_html_link_redirects_to_exact_destination(client, db, smtp, url):
    s, html = _variant_send(db, smtp, CT.HTML, body_html=f'<p><a href="{url}">\n Get Started\n</a></p>')
    assert _urls(html) == [url]
    assert "LEGACY BODY" not in html and "<hr><section>" not in html
    assert "<br> Get Started<br></a>" in html  # anchor text intact (newlines -> <br> as before)
    token = parse_qs(urlparse(re.search(r"/track/click\?token=[^\"'\s<]+", html).group(0)).query)["token"][0]
    r = client.get("/track/click", params={"token": token}, follow_redirects=False)
    assert r.status_code in (302, 307)
    assert r.headers["location"] == url


def test_spec_example_end_to_end(client, db, smtp):
    url = "https://affiliate.example.com/click?aff_id=123&subid=abc"
    s, html = _variant_send(db, smtp, CT.HTML, body_html=f'<a href="{url}">\n  Get Started\n</a>')
    token = parse_qs(urlparse(re.search(r"/track/click\?token=[^\"'\s<]+", html).group(0)).query)["token"][0]
    assert client.get("/track/click", params={"token": token}, follow_redirects=False).headers["location"] == url


def test_variant_single_quoted_and_escaped_ampersand_href(db, smtp):
    _, html = _variant_send(db, smtp, CT.HTML,
                            body_html="<a href='https://a.example/x?a=1&amp;b=2#f'>A</a>")
    assert _urls(html) == ["https://a.example/x?a=1&b=2#f"]


def test_multiple_variant_links_keep_independent_destinations(db, smtp):
    a, b = "https://offer-a.example/click?id=1", "https://offer-b.example/click?id=2&subid=z"
    _, html = _variant_send(db, smtp, CT.HTML,
                            body_html=f'<a href="{a}">Offer A</a><a href="{b}">Offer B</a>')
    assert _urls(html) == [a, b]
    assert len(set(_tokens(html))) == 2


def test_non_http_links_and_image_src_not_tracked_in_variant(db, smtp):
    body = (f'<a href="mailto:a@b.co">m</a><a href="tel:+1">t</a><a href="javascript:void(0)">j</a>'
            f'<a href="#x">h</a><img src="{IMG}">')
    _, html = _variant_send(db, smtp, CT.HTML, body_html=body)
    assert _urls(html) == []
    assert f'src="{IMG}"' in html and 'href="mailto:a@b.co"' in html


def test_image_variant_src_is_not_a_tracked_click(db, smtp):
    _, html = _variant_send(db, smtp, CT.IMAGE, image_url=IMG + "?a=1&b=2")
    assert _urls(html) == []
    assert 'src="https://cdn.example.com/p.png?a=1&amp;b=2"' in html


def test_text_variant_without_link_has_no_tracking_links(db, smtp):
    _, html = _variant_send(db, smtp, CT.TEXT, body_text="Just words")
    assert _urls(html) == []


def test_text_variant_bare_url_is_tracked_exactly_despite_html_escaping(db, smtp):
    url = "https://aff.example.com/c?aff_id=1&subid=a#top"
    _, html = _variant_send(db, smtp, CT.TEXT, body_text=f"Go: {url} now 'ok'")
    assert _urls(html) == [url]
    assert "&amp;" not in _tokens(html)[0] and " now &#x27;ok&#x27;" in html


def test_text_image_variant_tracks_text_url_not_image(db, smtp):
    url = "https://aff.example.com/c?x=1&y=2"
    _, html = _variant_send(db, smtp, CT.TEXT_IMAGE, body_text=f"See {url}", image_url=IMG)
    assert _urls(html) == [url]
    assert f'src="{IMG}"' in html


def test_offer_affiliate_url_does_not_overwrite_variant_links(db, smtp):
    link = "https://variant-link.example/go?id=7"
    _, html = _variant_send(db, smtp, CT.HTML, affiliate_url="https://offer-aff.example/x?id=1",
                            body_html=f'<a href="{link}">Go</a>')
    assert _urls(html) == [link]
    assert "offer-aff.example" not in html


def test_variant_without_cta_gets_no_invented_cta_from_offer(db, smtp):
    _, html = _variant_send(db, smtp, CT.TEXT, body_text="No links here",
                            affiliate_url="https://offer-aff.example/x", cta_url="https://cta.example/c")
    assert _urls(html) == []
    assert "offer-aff.example" not in html and "cta.example" not in html


def test_legacy_campaign_still_gets_cta_url_block_tracked_unchanged(db, smtp):
    s = Scenario(db, n_contacts=1, body="Hi")
    # Legacy promotion block is built by CampaignService; emulate its output (cta_url anchor).
    s.campaign.body = 'Hi\n<hr><section><p><a href="https://cta.example/c?a=1&amp;b=2">Shop now</a></p></section>'
    db.commit()
    EmailDeliveryService(db).create_campaign_deliveries(s.campaign)
    CampaignSenderService(db).send_campaign(s.campaign.id)
    html = smtp.sent[0].html
    assert s.campaign.variant_id is None
    assert _urls(html) == ["https://cta.example/c?a=1&b=2"]
    assert "Shop now</a>" in html


def test_security_validation_unchanged(client):
    bad = jwt.encode({"delivery_id": 1, "url": "javascript:alert(1)", "purpose": "click"}, SECRET_KEY, algorithm=ALGORITHM)
    assert client.get("/track/click", params={"token": bad}, follow_redirects=False).status_code == 400
    forged = jwt.encode({"delivery_id": 1, "url": "https://x.test", "purpose": "click"}, "k", algorithm=ALGORITHM)
    assert client.get("/track/click", params={"token": forged}, follow_redirects=False).status_code == 400
