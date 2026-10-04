"""Secrets must not leak through normal API serialization."""
import json

from tests.factories import SMTP_PASSWORD

FORBIDDEN_KEYS = {"smtp_password", "encrypted_password", "password"}


def _keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _keys(v)


def _assert_clean(response, *secrets):
    assert not (set(_keys(response.json())) & FORBIDDEN_KEYS) if "json" in response.headers.get("content-type", "") else True
    for secret in (*secrets, SMTP_PASSWORD, SMTP_PASSWORD.replace(" ", "")):
        assert secret not in response.text


def test_sender_password_is_not_exposed_anywhere_in_sender_api(client, headers, scenario):
    sid = scenario.sender.id
    for resp in (
        client.get("/sender-accounts/", headers=headers),
        client.get("/sender-accounts/export", headers=headers),
        client.put(f"/sender-accounts/{sid}", json={"status": "verified"}, headers=headers),
        client.post(f"/sender-accounts/{sid}/verify", headers=headers),
    ):
        assert resp.status_code == 200
        _assert_clean(resp)


def test_campaign_and_delivery_responses_do_not_expose_sender_secrets(client, headers, scenario, smtp):
    cid = scenario.campaign.id
    client.post(f"/campaigns/{cid}/prepare", headers=headers)
    smtp.fail_auth()
    client.post(f"/campaigns/{cid}/send", headers=headers)
    for url in (f"/campaigns/{cid}", "/campaigns/", f"/campaigns/{cid}/deliveries", f"/campaigns/{cid}/analytics"):
        _assert_clean(client.get(url, headers=headers))


def test_sender_failure_message_does_not_contain_password(client, headers, scenario, smtp):
    smtp.fail_auth()
    r = client.post(f"/sender-accounts/{scenario.sender.id}/verify", headers=headers)
    assert r.json()["last_error"]
    _assert_clean(r)


def test_user_response_does_not_expose_password_hash(client, headers):
    r = client.get("/users/me", headers=headers)
    assert r.status_code == 200
    assert "password" not in r.json()
    assert "$2b$" not in r.text
