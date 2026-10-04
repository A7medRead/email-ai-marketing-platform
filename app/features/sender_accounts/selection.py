from sqlalchemy import func
from sqlalchemy.orm import Session

from app.features.campaigns.delivery_model import EmailDelivery, EmailDeliveryStatus
from app.features.sender_accounts.enums import SenderAccountStatus
from app.features.sender_accounts.model import SenderAccount


def available_capacity(db: Session, sender: SenderAccount) -> int:
    """How many more deliveries this sender can claim right now.

    batch_size minus the deliveries it currently holds in SENDING. SENT/FAILED
    do not count. daily_limit/hourly_limit are intentionally not considered.
    """
    in_flight = (
        db.query(func.count(EmailDelivery.id))
        .filter(
            EmailDelivery.sender_account_id == sender.id,
            EmailDelivery.status == EmailDeliveryStatus.SENDING,
        )
        .scalar()
    )
    return max(sender.batch_size - in_flight, 0)


def get_available_senders(db: Session, user_id: int) -> list[SenderAccount]:
    """Senders that may take work, in a stable order.

    Eligible = VERIFIED status (PENDING/FAILED/DISABLED are skipped) with
    capacity left. Order: lowest `priority` first, then lowest `id`, so the
    result is deterministic and needs no round-robin state.
    """
    senders = (
        db.query(SenderAccount)
        .filter(
            SenderAccount.user_id == user_id,
            SenderAccount.status == SenderAccountStatus.VERIFIED,
        )
        .order_by(SenderAccount.priority.asc(), SenderAccount.id.asc())
        .all()
    )
    return [s for s in senders if available_capacity(db, s) > 0]


def select_sender(db: Session, user_id: int) -> SenderAccount | None:
    """The first available sender, or None."""
    senders = get_available_senders(db, user_id)
    return senders[0] if senders else None
