"""Phase 2B-2: PENDING -> SENDING atomic claiming and sender distribution."""
import threading
from collections import Counter

from app.features.campaigns.delivery_model import EmailDelivery, EmailDeliveryStatus
from app.features.campaigns.dispatcher import claim_delivery, claim_pending_deliveries
from app.features.sender_accounts.enums import SenderAccountStatus
from app.features.sender_accounts.selection import available_capacity
from tests.factories import (
    make_campaign,
    make_contact,
    make_list,
    make_sender,
    make_user,
)

S = EmailDeliveryStatus


def setup_queue(db, batch_sizes, pending, **sender_kwargs):
    """User with one sender per batch size and `pending` PENDING deliveries."""
    user = make_user(db)
    senders = [
        make_sender(db, user, email=f"s{i}@example.com", batch_size=b, priority=i + 1, **sender_kwargs)
        for i, b in enumerate(batch_sizes)
    ]
    contacts = [make_contact(db, user, f"c{i}@example.com") for i in range(pending)]
    campaign = make_campaign(db, user, senders[0], make_list(db, user, contacts))
    db.add_all(
        EmailDelivery(
            campaign_id=campaign.id, contact_id=c.id, recipient_email=c.email, status=S.PENDING
        )
        for c in contacts
    )
    db.commit()
    return user, senders, campaign


def count(db, status):
    return db.query(EmailDelivery).filter_by(status=status).count()


def per_sender(db):
    rows = db.query(EmailDelivery).filter_by(status=S.SENDING).all()
    return Counter(r.sender_account_id for r in rows)


# ---- distribution ----

def test_one_sender_fewer_pending_than_capacity(db):
    user, (a,), _ = setup_queue(db, [50], 30)
    assert len(claim_pending_deliveries(db, user.id)) == 30
    assert count(db, S.SENDING) == 30 and count(db, S.PENDING) == 0


def test_one_sender_over_capacity(db):
    user, (a,), _ = setup_queue(db, [50], 80)
    assert len(claim_pending_deliveries(db, user.id)) == 50
    assert count(db, S.SENDING) == 50 and count(db, S.PENDING) == 30


def test_multiple_senders_distributed_by_capacity(db):
    user, (a, b, c), _ = setup_queue(db, [50, 30, 20], 100)
    assert len(claim_pending_deliveries(db, user.id)) == 100
    assert per_sender(db) == {a.id: 50, b.id: 30, c.id: 20}
    assert count(db, S.PENDING) == 0


def test_multiple_senders_insufficient_capacity(db):
    user, (a, b, c), _ = setup_queue(db, [50, 30, 20], 150)
    assert len(claim_pending_deliveries(db, user.id)) == 100
    assert per_sender(db) == {a.id: 50, b.id: 30, c.id: 20}
    assert count(db, S.PENDING) == 50


def test_partial_fill_follows_priority_order(db):
    user, (a, b, c), _ = setup_queue(db, [50, 30, 20], 60)
    claim_pending_deliveries(db, user.id)
    assert per_sender(db) == {a.id: 50, b.id: 10}


def test_priority_beats_creation_order(db):
    user, (a, b), _ = setup_queue(db, [10, 10], 5)
    a.priority, b.priority = 2, 1
    db.commit()
    claim_pending_deliveries(db, user.id)
    assert per_sender(db) == {b.id: 5}


def test_disabled_and_other_ineligible_senders_get_nothing(db):
    user, (a, b), _ = setup_queue(db, [50, 50], 20)
    b.status = SenderAccountStatus.DISABLED
    db.commit()
    for st in (SenderAccountStatus.PENDING, SenderAccountStatus.FAILED):
        make_sender(db, user, email=f"{st.value}@example.com", status=st, batch_size=50, priority=0)
    claim_pending_deliveries(db, user.id)
    assert per_sender(db) == {a.id: 20}


def test_zero_batch_size_sender_gets_nothing(db):
    user, (a,), _ = setup_queue(db, [0], 5)
    assert claim_pending_deliveries(db, user.id) == []
    assert count(db, S.PENDING) == 5


def test_other_users_deliveries_are_not_claimed(db):
    user, _, _ = setup_queue(db, [50], 3)
    other = make_user(db, email="other@example.com")
    make_sender(db, other, email="o@example.com")
    assert claim_pending_deliveries(db, other.id) == []
    assert count(db, S.PENDING) == 3


# ---- capacity ----

def test_capacity_subtracts_sending_but_not_sent(db):
    user, (a,), _ = setup_queue(db, [10], 10)
    claim_pending_deliveries(db, user.id)
    assert available_capacity(db, a) == 0
    # Finishing deliveries frees capacity; SENT/FAILED are never counted.
    for d in db.query(EmailDelivery).limit(4).all():
        d.status = S.SENT
    for d in db.query(EmailDelivery).filter_by(status=S.SENDING).limit(2).all():
        d.status = S.FAILED
    db.commit()
    assert available_capacity(db, a) == 4


def test_full_sender_gets_nothing_more(db):
    user, (a,), _ = setup_queue(db, [5], 12)
    claim_pending_deliveries(db, user.id)
    assert claim_pending_deliveries(db, user.id) == []
    assert count(db, S.SENDING) == 5 and count(db, S.PENDING) == 7


# ---- idempotency ----

def test_second_dispatch_does_not_reclaim(db):
    user, _, _ = setup_queue(db, [50, 30], 40)
    first = claim_pending_deliveries(db, user.id)
    assert len(first) == 40
    assert claim_pending_deliveries(db, user.id) == []


def test_sending_sent_failed_are_not_claimable(db):
    user, (a,), _ = setup_queue(db, [50], 3)
    d1, d2, d3 = db.query(EmailDelivery).order_by(EmailDelivery.id).all()
    d1.status, d2.status, d3.status = S.SENDING, S.SENT, S.FAILED
    db.commit()
    assert [claim_delivery(db, d.id, a.id, a.batch_size) for d in (d1, d2, d3)] == [False] * 3
    assert claim_pending_deliveries(db, user.id) == []
    assert [d.status for d in db.query(EmailDelivery).order_by(EmailDelivery.id)] == [
        S.SENDING, S.SENT, S.FAILED,
    ]


# ---- concurrency (separate sessions on the same SQLite file) ----

def run_threads(session_factory, fn, n):
    barrier = threading.Barrier(n)
    results, errors = [None] * n, []

    def worker(i):
        session = session_factory()
        try:
            barrier.wait()
            results[i] = fn(session)
        except Exception as e:  # surfaced below, never swallowed
            errors.append(e)
        finally:
            session.close()

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert not errors, errors
    return results


def test_same_delivery_cannot_be_claimed_by_two_workers(db, session_factory):
    user, (a, b), _ = setup_queue(db, [50, 50], 1)
    delivery_id = db.query(EmailDelivery).one().id
    senders = {0: (a.id, a.batch_size), 1: (b.id, b.batch_size)}

    for _ in range(20):  # repeat to shake out races
        db.query(EmailDelivery).update({"status": S.PENDING, "sender_account_id": None})
        db.commit()
        idx = iter(range(2))
        lock = threading.Lock()

        def attempt(session):
            with lock:
                i = next(idx)
            return claim_delivery(session, delivery_id, *senders[i])

        results = run_threads(session_factory, attempt, 2)
        assert sorted(results) == [False, True]
        db.expire_all()
        assert db.get(EmailDelivery, delivery_id).status == S.SENDING


def test_concurrent_dispatchers_never_double_claim(db, session_factory):
    user, (a, b, c), _ = setup_queue(db, [50, 30, 20], 150)
    # Plain int: ORM instances belong to the main thread's session, which is not thread-safe.
    user_id = user.id

    results = run_threads(
        session_factory,
        lambda s: [d.id for d in claim_pending_deliveries(s, user_id)],
        4,
    )
    ids = [i for r in results for i in r]
    assert len(ids) == len(set(ids)) == 100  # no delivery claimed twice, capacity filled
    db.expire_all()
    assert per_sender(db) == {a.id: 50, b.id: 30, c.id: 20}
    assert count(db, S.PENDING) == 50


# ---- Phase 2B-3: stale recovery, retry, failure handling ----

from datetime import datetime, timedelta

from app.features.campaigns.dispatcher import (
    MAX_ATTEMPTS,
    STALE_CLAIM_MINUTES,
    complete_delivery,
    fail_delivery,
    is_temporary_failure,
    recover_stale_deliveries,
)
from app.features.contacts.enums import ContactStatus

NOW = datetime(2026, 1, 1, 12, 0, 0)
TEMP = "(451, b'try again later')"
PERM = "(550, b'mailbox unavailable')"


def get(db, delivery_id):
    db.expire_all()
    return db.get(EmailDelivery, delivery_id)


def claimed(db, batch_sizes=(50,), pending=1, now=NOW):
    user, senders, _ = setup_queue(db, list(batch_sizes), pending)
    return user, senders, claim_pending_deliveries(db, user.id, now=now)


def age(minutes):
    return NOW + timedelta(minutes=minutes)


# stale recovery

def test_fresh_sending_stays_sending(db):
    _, _, (d,) = claimed(db)
    assert recover_stale_deliveries(db, age(STALE_CLAIM_MINUTES - 1)) == (0, 0)
    d = get(db, d.id)
    assert d.status == S.SENDING and d.claimed_at == NOW


def test_stale_sending_returns_to_pending_and_clears_claim(db):
    _, _, (d,) = claimed(db)
    assert recover_stale_deliveries(db, age(STALE_CLAIM_MINUTES + 1)) == (1, 0)
    d = get(db, d.id)
    assert d.status == S.PENDING and d.claimed_at is None and d.attempt_count == 1


def test_recovery_is_idempotent(db):
    claimed(db, pending=3)
    assert recover_stale_deliveries(db, age(60)) == (3, 0)
    assert recover_stale_deliveries(db, age(60)) == (0, 0)
    assert count(db, S.PENDING) == 3


def test_recovery_does_not_touch_delivery_finished_meanwhile(db):
    _, _, (d,) = claimed(db)
    complete_delivery(db, d.id, now=age(10))
    assert recover_stale_deliveries(db, age(60)) == (0, 0)
    assert get(db, d.id).status == S.SENT


def test_stale_with_attempts_exhausted_is_failed_not_requeued(db):
    _, _, (d,) = claimed(db)
    db.query(EmailDelivery).update({"attempt_count": MAX_ATTEMPTS})
    db.commit()
    assert recover_stale_deliveries(db, age(60)) == (0, 1)
    d = get(db, d.id)
    assert d.status == S.FAILED and d.claimed_at is None and d.error_message


def test_recovery_frees_sender_capacity(db):
    user, (sender,), _ = setup_queue(db, [50], 50)
    claim_pending_deliveries(db, user.id, now=NOW)
    assert available_capacity(db, sender) == 0
    # One delivery's claim is stale (the rest were claimed later).
    rows = db.query(EmailDelivery).order_by(EmailDelivery.id).all()
    for r in rows[1:]:
        r.claimed_at = age(40)
    db.commit()
    assert recover_stale_deliveries(db, age(STALE_CLAIM_MINUTES + 1)) == (1, 0)
    assert available_capacity(db, sender) == 1


# retry / failure handling

def test_temporary_failure_returns_to_pending_with_backoff(db):
    _, _, (d,) = claimed(db)
    assert fail_delivery(db, d.id, TEMP, now=NOW) == S.PENDING
    d = get(db, d.id)
    assert d.status == S.PENDING and d.claimed_at is None
    assert d.next_attempt_at == NOW + timedelta(minutes=1)
    assert d.error_message == TEMP


def test_permanent_failure_becomes_failed_and_releases_capacity(db):
    _, (sender,), (d,) = claimed(db)
    assert fail_delivery(db, d.id, PERM, now=NOW) == S.FAILED
    d = get(db, d.id)
    assert d.status == S.FAILED and d.claimed_at is None and d.error_message == PERM
    assert available_capacity(db, sender) == sender.batch_size


def test_unknown_error_is_treated_as_permanent(db):
    _, _, (d,) = claimed(db)
    assert fail_delivery(db, d.id, "something odd", now=NOW) == S.FAILED


def test_max_attempts_then_failed(db):
    user, _, (d,) = claimed(db)
    statuses = []
    now = NOW
    for _ in range(MAX_ATTEMPTS):
        statuses.append(fail_delivery(db, d.id, TEMP, now=now))
        now = get(db, d.id).next_attempt_at or now
        if statuses[-1] == S.PENDING:
            assert len(claim_pending_deliveries(db, user.id, now=now)) == 1
    assert statuses == [S.PENDING, S.PENDING, S.FAILED]
    d = get(db, d.id)
    assert d.attempt_count == MAX_ATTEMPTS and d.next_attempt_at is None
    assert claim_pending_deliveries(db, user.id, now=now + timedelta(days=1)) == []


def test_late_result_for_recovered_delivery_is_ignored(db):
    _, _, (d,) = claimed(db)
    recover_stale_deliveries(db, age(60))
    assert complete_delivery(db, d.id) is False
    assert fail_delivery(db, d.id, PERM) is None
    assert get(db, d.id).status == S.PENDING


def test_success_clears_claim_and_previous_error(db):
    user, _, (d,) = claimed(db)
    fail_delivery(db, d.id, TEMP, now=NOW)
    (d,) = claim_pending_deliveries(db, user.id, now=age(2))
    assert complete_delivery(db, d.id, now=age(2)) is True
    d = get(db, d.id)
    assert d.status == S.SENT and d.sent_at == age(2)
    assert d.claimed_at is None and d.next_attempt_at is None and d.error_message is None
    assert d.attempt_count == 2


def test_classification():
    assert is_temporary_failure(TEMP)
    assert is_temporary_failure("Gmail SMTP connection failed: timed out")
    assert is_temporary_failure("Gmail SMTP connection failed: connection refused")
    assert not is_temporary_failure(PERM)
    assert not is_temporary_failure("Gmail SMTP connection failed: (535, b'5.7.8 Username and Password not accepted')")
    assert not is_temporary_failure("{'a@b.com': (550, b'no such user')}")
    assert not is_temporary_failure(None)


# claiming with retry time

def test_future_next_attempt_at_is_not_claimable(db):
    user, (sender,), _ = setup_queue(db, [50], 1)
    d = db.query(EmailDelivery).one()
    d.next_attempt_at = age(5)
    db.commit()
    assert claim_pending_deliveries(db, user.id, now=NOW) == []
    assert claim_delivery(db, d.id, sender.id, 50, now=NOW) is False
    assert get(db, d.id).status == S.PENDING
    assert len(claim_pending_deliveries(db, user.id, now=age(5))) == 1


def test_not_yet_due_deliveries_do_not_starve_due_ones(db):
    user, _, _ = setup_queue(db, [1], 2)
    first, second = db.query(EmailDelivery).order_by(EmailDelivery.id).all()
    first.next_attempt_at = age(5)
    db.commit()
    (got,) = claim_pending_deliveries(db, user.id, now=NOW)
    assert got.id == second.id


# unsubscribe at claim time

def test_unsubscribed_contact_is_cancelled_not_failed(db):
    user, (sender,), _ = setup_queue(db, [50], 2)
    d0 = db.query(EmailDelivery).order_by(EmailDelivery.id).first()
    contact = d0.contact
    contact.status = ContactStatus.UNSUBSCRIBED
    db.commit()
    claimed_rows = claim_pending_deliveries(db, user.id, now=NOW)
    assert [d.id for d in claimed_rows] != [d0.id] and len(claimed_rows) == 1
    d0 = get(db, d0.id)
    assert d0.status == S.CANCELLED and d0.claimed_at is None
    assert available_capacity(db, sender) == 49
