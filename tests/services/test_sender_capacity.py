"""Phase 2B-1: sender batch_size configuration and sender selection."""
from sqlalchemy import text

from app.features.sender_accounts.enums import SenderAccountStatus
from app.features.sender_accounts.model import DEFAULT_BATCH_SIZE, SenderAccount
from app.features.sender_accounts.selection import (
    available_capacity,
    get_available_senders,
    select_sender,
)
from tests.factories import SMTP_PASSWORD, make_sender, make_user

CREATE = {"email": "new@example.com", "display_name": "New", "smtp_password": "super-secret-pw"}


# ---- model ----

def test_default_batch_size(db):
    sender = make_sender(db, make_user(db))
    assert sender.batch_size == DEFAULT_BATCH_SIZE == 50


def test_custom_batch_size(db):
    sender = make_sender(db, make_user(db), batch_size=30)
    assert sender.batch_size == 30


def test_existing_row_without_batch_size_remains_valid(db):
    """A row inserted the pre-migration way (no batch_size) gets the DB default."""
    user = make_user(db)
    db.execute(
        text(
            "INSERT INTO sender_accounts (user_id, email, name, provider, encrypted_password, "
            "status, verified, daily_limit, hourly_limit, daily_sent, hourly_sent, priority) "
            "VALUES (:u, 'old@example.com', 'Old', 'gmail', 'x', 'VERIFIED', 1, 500, 100, 0, 0, 1)"
        ),
        {"u": user.id},
    )
    db.commit()
    old = db.query(SenderAccount).filter_by(email="old@example.com").one()
    assert old.batch_size == 50
    assert select_sender(db, user.id).id == old.id


# ---- API ----

def test_api_create_defaults_batch_size(client, headers):
    assert client.post("/sender-accounts/", json=CREATE, headers=headers).json()["batch_size"] == 50


def test_api_create_with_batch_size(client, headers):
    r = client.post("/sender-accounts/", json={**CREATE, "batch_size": 20}, headers=headers)
    assert r.status_code == 200
    assert r.json()["batch_size"] == 20


def test_api_update_batch_size_and_returned_in_list(client, headers):
    sid = client.post("/sender-accounts/", json=CREATE, headers=headers).json()["id"]
    r = client.put(f"/sender-accounts/{sid}", json={"batch_size": 30}, headers=headers)
    assert r.status_code == 200
    assert r.json()["batch_size"] == 30
    assert client.get("/sender-accounts/", headers=headers).json()[0]["batch_size"] == 30


def test_api_update_without_batch_size_keeps_it(client, headers):
    sid = client.post("/sender-accounts/", json={**CREATE, "batch_size": 20}, headers=headers).json()["id"]
    body = client.put(f"/sender-accounts/{sid}", json={"display_name": "Renamed"}, headers=headers).json()
    assert body["batch_size"] == 20


def test_api_rejects_invalid_batch_size(client, headers):
    for bad in (0, -5, 100000):
        r = client.post("/sender-accounts/", json={**CREATE, "batch_size": bad}, headers=headers)
        assert r.status_code == 422


def test_api_smtp_password_still_hidden_with_batch_size(client, headers):
    r = client.post("/sender-accounts/", json={**CREATE, "batch_size": 10}, headers=headers)
    assert "super-secret-pw" not in r.text
    assert "encrypted_password" not in r.text
    assert "smtp_password" not in r.text


# ---- selection ----

def test_disabled_and_unverified_senders_are_not_selected(db):
    user = make_user(db)
    make_sender(db, user, email="d@example.com", status=SenderAccountStatus.DISABLED)
    make_sender(db, user, email="p@example.com", status=SenderAccountStatus.PENDING)
    make_sender(db, user, email="f@example.com", status=SenderAccountStatus.FAILED)
    assert get_available_senders(db, user.id) == []
    assert select_sender(db, user.id) is None


def test_enabled_sender_is_eligible_with_capacity(db):
    user = make_user(db)
    sender = make_sender(db, user, batch_size=30)
    assert select_sender(db, user.id).id == sender.id
    assert available_capacity(db, sender) == 30


def test_multiple_senders_are_available(db):
    user = make_user(db)
    a = make_sender(db, user, email="a@example.com", batch_size=50)
    b = make_sender(db, user, email="b@example.com", batch_size=30)
    c = make_sender(db, user, email="c@example.com", batch_size=20)
    assert [s.id for s in get_available_senders(db, user.id)] == [a.id, b.id, c.id]


def test_selection_is_deterministic_priority_then_id(db):
    user = make_user(db)
    a = make_sender(db, user, email="a@example.com")
    b = make_sender(db, user, email="b@example.com", priority=0)
    c = make_sender(db, user, email="c@example.com")
    expected = [b.id, a.id, c.id]
    for _ in range(3):
        assert [s.id for s in get_available_senders(db, user.id)] == expected
        assert select_sender(db, user.id).id == b.id


def test_selection_is_scoped_to_user(db):
    owner, other = make_user(db), make_user(db, email="o2@example.com")
    make_sender(db, other)
    assert select_sender(db, owner.id) is None
