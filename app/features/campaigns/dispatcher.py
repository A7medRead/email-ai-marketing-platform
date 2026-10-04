"""Queue dispatcher: claim, retry and recovery of EmailDelivery rows.

Several workers (API-triggered sends and the scheduler) may run at once on SQLite, so:
- claiming is one conditional UPDATE (PENDING -> SENDING). Only the caller that flips the row
  owns it, and the sender's batch capacity is re-checked inside the same statement, so no email
  is sent twice and no sender exceeds batch_size;
- results are written only while the row is still SENDING, so a late result from a worker that
  was already recovered cannot overwrite a newer state;
- a worker that dies mid-send leaves a SENDING row; recover_stale_deliveries releases it after
  STALE_CLAIM_MINUTES, and a crash counts as an attempt so a poison row cannot loop forever;
- only clearly temporary errors are retried (with backoff); unknown errors are permanent so we
  never resend on a guess.
"""
import re
from datetime import datetime, timedelta

from sqlalchemy import and_, func, or_, update
from sqlalchemy.orm import Session

from app.features.campaigns.delivery_model import EmailDelivery, EmailDeliveryStatus
from app.features.campaigns.model import Campaign
from app.features.contacts.enums import ContactStatus
from app.features.contacts.model import Contact
from app.features.sender_accounts.model import SenderAccount
from app.features.sender_accounts.selection import available_capacity, get_available_senders

# A claim covers a whole batch up front and its emails are sent one by one
# (each SMTP connect can take up to 20s), so a healthy claim can legitimately
# be old by the time its last email goes out. Stay well above that.
STALE_CLAIM_MINUTES = 30

# Total send attempts per delivery (claims). Backoff before attempt n+1 is
# 5**(n-1) minutes: 1 minute after attempt 1, 5 after attempt 2.
MAX_ATTEMPTS = 3


def retry_delay(attempt_count: int) -> timedelta:
    return timedelta(minutes=5 ** (attempt_count - 1))


_SMTP_CODE = re.compile(r"\(\s*([45]\d\d)\b")
_NETWORK_HINTS = (
    "timed out",
    "timeout",
    "connection refused",
    "connection reset",
    "connection unexpectedly closed",
    "server disconnected",
    "temporarily",
    "network is unreachable",
    "name or service not known",
    "nodename nor servname",
)


def is_temporary_failure(message: str | None) -> bool:
    """Conservative classification from the error text the SMTP layer returns
    (it only exposes str(exception), no structured code).

    Temporary: an SMTP 4xx code, or a network/timeout error. Everything else
    - 5xx (invalid recipient, authentication 535, ...) and anything we do not
    recognise - is treated as permanent, so unknown errors are never retried.
    """
    text = (message or "").lower()
    code = _SMTP_CODE.search(text)
    if code:
        return code.group(1).startswith("4")
    return any(hint in text for hint in _NETWORK_HINTS)


# Raised by app.infrastructure.email.smtp when connecting/logging in to the
# sender's own SMTP account (never for a recipient problem).
_SENDER_CONNECT_PREFIX = "smtp connection failed"
_SENDER_LOGIN_HINTS = (
    "authentication",
    "username and password not accepted",
    "account has been disabled",
    "account disabled",
    "account suspended",
    "account has been suspended",
)
_SENDER_QUOTA_HINTS = (
    "sending quota",
    "sending limit",
    "user sending",
)


def is_sender_failure(message: str | None) -> bool:
    """True only for clear sender-account problems, from the error text.

    - login stage (message carries the connect/login prefix) rejected for
      authentication, or the account is disabled/suspended;
    - an explicit *sending* quota/limit of the account (a recipient's
      "mailbox over quota" does not match).
    Any other 4xx/5xx (550 mailbox unavailable, ...), timeouts and unknown
    errors are NOT sender failures.
    """
    text = (message or "").lower()
    if _SENDER_CONNECT_PREFIX in text and any(h in text for h in _SENDER_LOGIN_HINTS):
        return True
    return any(h in text for h in _SENDER_QUOTA_HINTS)


def _claimable(now: datetime):
    return and_(
        EmailDelivery.status == EmailDeliveryStatus.PENDING,
        or_(EmailDelivery.next_attempt_at.is_(None), EmailDelivery.next_attempt_at <= now),
    )


def claim_delivery(
    db: Session,
    delivery_id: int,
    sender_id: int,
    batch_size: int,
    now: datetime | None = None,
) -> bool:
    """Atomically move one delivery PENDING -> SENDING and assign it to the sender.

    Only claimable if its retry time (next_attempt_at) has arrived. The claim
    stamps claimed_at and counts the attempt.

    A single conditional UPDATE: only the caller that flips the row sees
    rowcount == 1 and owns it. The WHERE also re-checks the sender's batch
    capacity inside the same statement, so two dispatchers cannot both fill
    the same sender past batch_size. Commits immediately (short transaction).
    """
    now = now or datetime.utcnow()
    in_flight = (
        db.query(func.count(EmailDelivery.id))
        .filter(
            EmailDelivery.sender_account_id == sender_id,
            EmailDelivery.status == EmailDeliveryStatus.SENDING,
        )
        .scalar_subquery()
    )
    result = db.execute(
        update(EmailDelivery)
        .where(
            EmailDelivery.id == delivery_id,
            _claimable(now),
            in_flight < batch_size,
        )
        .values(
            status=EmailDeliveryStatus.SENDING,
            sender_account_id=sender_id,
            claimed_at=now,
            next_attempt_at=None,
            attempt_count=EmailDelivery.attempt_count + 1,
        )
        .execution_options(synchronize_session=False)
    )
    db.commit()
    return result.rowcount == 1


def claim_pending_deliveries(
    db: Session,
    user_id: int,
    campaign_id: int | None = None,
    now: datetime | None = None,
) -> list[EmailDelivery]:
    """Claim PENDING deliveries for the user's eligible senders, up to each
    sender's remaining batch capacity. Senders are visited in the existing
    selection order (priority, then id). Returns the deliveries claimed.

    Claiming only marks rows SENDING; it does not send anything. A claimed
    delivery whose contact is no longer ACTIVE (unsubscribed) is moved to
    CANCELLED instead and not returned.
    """
    now = now or datetime.utcnow()
    claimed_ids: list[int] = []

    for sender in get_available_senders(db, user_id):
        # Plain ints: the commit in claim_delivery expires ORM instances.
        sender_id, batch_size = sender.id, sender.batch_size
        capacity = available_capacity(db, sender)
        if capacity <= 0:
            continue

        query = (
            db.query(EmailDelivery.id)
            .join(Campaign, Campaign.id == EmailDelivery.campaign_id)
            .filter(
                Campaign.user_id == user_id,
                _claimable(now),
            )
        )
        if campaign_id is not None:
            query = query.filter(EmailDelivery.campaign_id == campaign_id)

        candidates = query.order_by(EmailDelivery.id.asc()).limit(capacity).all()

        for (delivery_id,) in candidates:
            if not claim_delivery(db, delivery_id, sender_id, batch_size, now):
                continue
            if _contact_is_active(db, delivery_id):
                claimed_ids.append(delivery_id)
            else:
                _finish(
                    db,
                    delivery_id,
                    status=EmailDeliveryStatus.CANCELLED,
                    error_message="Contact is no longer subscribed.",
                )

    if not claimed_ids:
        return []
    return (
        db.query(EmailDelivery)
        .filter(EmailDelivery.id.in_(claimed_ids))
        .order_by(EmailDelivery.id.asc())
        .all()
    )


def _contact_is_active(db: Session, delivery_id: int) -> bool:
    status = (
        db.query(Contact.status)
        .join(EmailDelivery, EmailDelivery.contact_id == Contact.id)
        .filter(EmailDelivery.id == delivery_id)
        .scalar()
    )
    return status == ContactStatus.ACTIVE


def _finish(db: Session, delivery_id: int, **values) -> bool:
    """Leave SENDING for a new status (claim cleared). Conditional on the
    delivery still being SENDING, so a result arriving after the delivery
    was recovered/finished by someone else is ignored."""
    values.setdefault("next_attempt_at", None)
    result = db.execute(
        update(EmailDelivery)
        .where(
            EmailDelivery.id == delivery_id,
            EmailDelivery.status == EmailDeliveryStatus.SENDING,
        )
        .values(claimed_at=None, **values)
        .execution_options(synchronize_session=False)
    )
    db.commit()
    return result.rowcount == 1


def complete_delivery(db: Session, delivery_id: int, now: datetime | None = None) -> bool:
    """SENDING -> SENT. Clears the claim and any earlier attempt's error."""
    return _finish(
        db,
        delivery_id,
        status=EmailDeliveryStatus.SENT,
        sent_at=now or datetime.utcnow(),
        error_message=None,
    )


def fail_delivery(
    db: Session,
    delivery_id: int,
    message: str,
    now: datetime | None = None,
) -> EmailDeliveryStatus | None:
    """Record a failed send attempt. Returns the new status, or None if the
    delivery was no longer SENDING.

    Temporary failure with attempts left -> PENDING with next_attempt_at set
    (the next dispatcher cycle picks it up once due). Permanent failure, or
    attempts exhausted -> FAILED. The last error stays in error_message.
    """
    now = now or datetime.utcnow()
    attempts = db.query(EmailDelivery.attempt_count).filter(EmailDelivery.id == delivery_id).scalar()
    message = (message or "")[:500]
    if attempts is not None and attempts < MAX_ATTEMPTS and is_temporary_failure(message):
        status = EmailDeliveryStatus.PENDING
        extra = {"next_attempt_at": now + retry_delay(attempts)}
    else:
        status = EmailDeliveryStatus.FAILED
        extra = {}
    done = _finish(db, delivery_id, status=status, error_message=message, **extra)
    return status if done else None


def recover_stale_deliveries(db: Session, now: datetime | None = None) -> tuple[int, int]:
    """Release deliveries whose worker apparently died mid-send.

    A delivery is stale if it is SENDING and claimed_at is older than
    STALE_CLAIM_MINUTES. Returns (requeued, abandoned):
    - requeued: back to PENDING with claimed_at cleared, so another worker can
      retry it (frees the sender's capacity);
    - abandoned: attempts already used up (a crash counts as an attempt), so
      FAILED instead of cycling through crashes forever.

    Each UPDATE re-checks status and claimed_at, so a delivery that finished
    or was re-claimed in the meantime is left alone. Safe to run repeatedly.
    """
    now = now or datetime.utcnow()
    stale = and_(
        EmailDelivery.status == EmailDeliveryStatus.SENDING,
        EmailDelivery.claimed_at < now - timedelta(minutes=STALE_CLAIM_MINUTES),
    )
    abandoned = db.execute(
        update(EmailDelivery)
        .where(stale, EmailDelivery.attempt_count >= MAX_ATTEMPTS)
        .values(
            status=EmailDeliveryStatus.FAILED,
            claimed_at=None,
            error_message="Gave up: worker stopped responding on the last attempt.",
        )
        .execution_options(synchronize_session=False)
    ).rowcount
    requeued = db.execute(
        update(EmailDelivery)
        .where(stale, EmailDelivery.attempt_count < MAX_ATTEMPTS)
        .values(status=EmailDeliveryStatus.PENDING, claimed_at=None)
        .execution_options(synchronize_session=False)
    ).rowcount
    db.commit()
    return requeued, abandoned
