"""Characterization: /sender-accounts endpoints, credential handling and secrecy."""
from app.core.encryption import decrypt
from app.features.sender_accounts.enums import SenderAccountStatus
from app.features.sender_accounts.model import SenderAccount
from tests.factories import SMTP_PASSWORD, make_sender, make_user

CREATE = {"email": "new@example.com", "display_name": "New Sender", "smtp_password": "super-secret-pw"}
SECRET_KEYS = {"smtp_password", "encrypted_password", "password"}


def _assert_no_secret(payload, *secrets):
    text = str(payload)
    assert not (SECRET_KEYS & set(payload.keys() if isinstance(payload, dict) else []))
    for secret in secrets:
        assert secret not in text


def test_create_sender_returns_pending_unverified_gmail_account(client, headers, db):
    r = client.post("/sender-accounts/", json=CREATE, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "new@example.com"
    assert body["name"] == "New Sender"
    assert body["provider"] == "gmail"
    assert body["status"] == "pending"
    assert body["verified"] is False


def test_create_sender_returns_current_default_limits(client, headers):
    body = client.post("/sender-accounts/", json=CREATE, headers=headers).json()
    assert (body["daily_limit"], body["hourly_limit"]) == (500, 100)
    assert (body["daily_sent"], body["hourly_sent"], body["priority"]) == (0, 0, 1)


def test_sender_credentials_are_encrypted_at_rest(client, headers, db):
    client.post("/sender-accounts/", json=CREATE, headers=headers)
    account = db.query(SenderAccount).filter_by(email="new@example.com").one()
    assert account.encrypted_password != "super-secret-pw"
    assert "super-secret-pw" not in account.encrypted_password
    assert decrypt(account.encrypted_password) == "super-secret-pw"


def test_sender_password_is_not_exposed_on_create(client, headers):
    body = client.post("/sender-accounts/", json=CREATE, headers=headers).json()
    _assert_no_secret(body, "super-secret-pw")


def test_sender_password_is_not_exposed_in_list(client, headers, db):
    client.post("/sender-accounts/", json=CREATE, headers=headers)
    r = client.get("/sender-accounts/", headers=headers)
    assert r.status_code == 200
    raw = r.text
    assert "super-secret-pw" not in raw
    assert "encrypted_password" not in raw
    assert "smtp_password" not in raw
    assert all(not (SECRET_KEYS & set(item)) for item in r.json())


def test_sender_password_is_not_exposed_on_update_or_verify(client, headers, db, smtp):
    sid = client.post("/sender-accounts/", json=CREATE, headers=headers).json()["id"]
    upd = client.put(f"/sender-accounts/{sid}", json={"smtp_password": "rotated-pw-1"}, headers=headers)
    ver = client.post(f"/sender-accounts/{sid}/verify", headers=headers)
    for r in (upd, ver):
        assert r.status_code == 200
        assert "rotated-pw-1" not in r.text and "encrypted_password" not in r.text


def test_sender_password_is_not_exposed_in_csv_export(client, headers, db):
    client.post("/sender-accounts/", json=CREATE, headers=headers)
    r = client.get("/sender-accounts/export", headers=headers)
    assert r.status_code == 200
    assert "super-secret-pw" not in r.text
    assert r.text.splitlines()[0] == "email,name,provider,status,verified"


def test_updating_password_re_encrypts_it(client, headers, db):
    sid = client.post("/sender-accounts/", json=CREATE, headers=headers).json()["id"]
    client.put(f"/sender-accounts/{sid}", json={"smtp_password": "rotated-pw-1"}, headers=headers)
    db.expire_all()
    account = db.get(SenderAccount, sid)
    assert account.encrypted_password != "rotated-pw-1"
    assert decrypt(account.encrypted_password) == "rotated-pw-1"


def test_update_sender_status_to_disabled(client, headers, db):
    sid = client.post("/sender-accounts/", json=CREATE, headers=headers).json()["id"]
    r = client.put(f"/sender-accounts/{sid}", json={"status": "disabled"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "disabled"


def test_verify_sender_success_marks_verified(client, headers, db, smtp):
    sid = client.post("/sender-accounts/", json=CREATE, headers=headers).json()["id"]
    r = client.post(f"/sender-accounts/{sid}/verify", headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "verified" and r.json()["verified"] is True
    assert smtp.logins == [("new@example.com", "super-secret-pw")]


def test_verify_sender_auth_failure_marks_failed_and_records_error(client, headers, db, smtp):
    sid = client.post("/sender-accounts/", json=CREATE, headers=headers).json()["id"]
    smtp.fail_auth()
    r = client.post(f"/sender-accounts/{sid}/verify", headers=headers)
    body = r.json()
    assert body["status"] == "failed" and body["verified"] is False
    assert "Username and Password not accepted" in body["last_error"]
    assert "super-secret-pw" not in r.text


def test_verify_sender_connection_failure_marks_failed(client, headers, db, smtp):
    sid = client.post("/sender-accounts/", json=CREATE, headers=headers).json()["id"]
    smtp.fail_connect()
    body = client.post(f"/sender-accounts/{sid}/verify", headers=headers).json()
    assert body["status"] == "failed"
    assert body["last_error"].startswith("Gmail SMTP connection failed")


def test_send_test_email_success_current_response_shape(client, headers, scenario, smtp):
    r = client.post(
        f"/sender-accounts/{scenario.sender.id}/send-test",
        json={"recipient_email": "probe@example.com"},
        headers=headers,
    )
    assert r.status_code == 200
    # Current quirk: the service returns a dict, which the API nests under "message".
    assert r.json() == {"message": {"success": True, "message": "Test email sent successfully."}}
    assert smtp.recipients() == ["probe@example.com"]


def test_send_test_email_failure_is_reported_in_body_not_status(client, headers, scenario, smtp):
    smtp.fail_auth()
    r = client.post(
        f"/sender-accounts/{scenario.sender.id}/send-test",
        json={"recipient_email": "probe@example.com"},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["message"]["success"] is False


def test_sender_endpoints_return_404_for_unknown_account(client, headers):
    assert client.put("/sender-accounts/9999", json={"status": "disabled"}, headers=headers).status_code == 404
    assert client.delete("/sender-accounts/9999", headers=headers).status_code == 404
    assert client.post("/sender-accounts/9999/verify", headers=headers).status_code == 404
    assert client.post("/sender-accounts/9999/send-test", json={"recipient_email": "a@b.co"}, headers=headers).status_code == 404


def test_sender_accounts_are_scoped_to_their_owner(client, scenario, other_user, make_headers):
    other = make_headers(other_user)
    assert client.get("/sender-accounts/", headers=other).json() == []
    assert client.post(f"/sender-accounts/{scenario.sender.id}/verify", headers=other).status_code == 404
    assert client.delete(f"/sender-accounts/{scenario.sender.id}", headers=other).status_code == 404


def test_sender_endpoints_require_authentication(client):
    assert client.get("/sender-accounts/").status_code == 401
    assert client.post("/sender-accounts/", json=CREATE).status_code == 401


def test_delete_sender_account(client, headers, scenario, db):
    sender_id = scenario.sender.id
    r = client.delete(f"/sender-accounts/{sender_id}", headers=headers)
    assert r.status_code == 200
    db.expire_all()
    assert db.get(SenderAccount, sender_id) is None


def test_import_accepts_blank_password_and_stores_encrypted_empty_string(client, headers, db):
    """Known quirk: a CSV row without a password still creates an account."""
    csv = "email,name\nimported@example.com,Imported\n"
    r = client.post("/sender-accounts/import", files={"file": ("s.csv", csv, "text/csv")}, headers=headers)
    assert r.status_code == 200 and r.json() == {"imported": 1, "skipped": 0}
    account = db.query(SenderAccount).filter_by(email="imported@example.com").one()
    assert decrypt(account.encrypted_password) == ""
    assert account.status == SenderAccountStatus.PENDING


def test_import_skips_duplicate_emails(client, headers, scenario):
    csv = f"email,name,password\n{scenario.sender.email},Dup,x\n"
    r = client.post("/sender-accounts/import", files={"file": ("s.csv", csv, "text/csv")}, headers=headers)
    assert r.json() == {"imported": 0, "skipped": 1}
