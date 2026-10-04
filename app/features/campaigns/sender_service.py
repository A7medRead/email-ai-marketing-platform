from sqlalchemy import func
from sqlalchemy.orm import Session

from app.features.campaigns.delivery_model import (
    EmailDelivery,
    EmailDeliveryStatus,
)

from app.features.campaigns.dispatcher import (
    claim_pending_deliveries,
    complete_delivery,
    fail_delivery,
    is_sender_failure,
    recover_stale_deliveries,
)

from app.features.sender_accounts.enums import SenderAccountStatus
from app.features.sender_accounts.model import (
    SenderAccount,
)

from app.features.campaigns.model import (
    Campaign,
    CampaignStatus,
)

from app.features.offers.renderer import render_campaign_email

from app.infrastructure.email.smtp import (
    send_campaign_email,
)



class CampaignSenderService:


    def __init__(
        self,
        db: Session,
    ):

        self.db = db



    def send_campaign(
        self,
        campaign_id: int,
    ):


        campaign = (
            self.db.query(Campaign)
            .filter(
                Campaign.id == campaign_id
            )
            .first()
        )


        if not campaign:
            return {
                "sent": 0,
                "failed": 0,
                "message": "Campaign not found"
            }


        if campaign.status == CampaignStatus.COMPLETED:
            return {
                "sent": 0,
                "failed": 0,
                "message": "Campaign already completed"
            }


        recover_stale_deliveries(self.db)

        # One pass at a time until nothing more is claimable right now.
        # A temporary failure waits for its next_attempt_at, so this ends.
        while self.send_next_batch(campaign):
            pass

        return self._update_campaign_totals(
            campaign.id
        )



    def send_next_batch(
        self,
        campaign: Campaign,
    ) -> int:
        """
        One dispatcher pass: claim (PENDING -> SENDING, bounded by each
        sender's batch_size), send each claimed delivery, record the outcome.
        Returns how many deliveries were claimed.
        """

        claimed = claim_pending_deliveries(
            self.db,
            campaign.user_id,
            campaign_id=campaign.id,
        )

        for delivery in claimed:
            self._send_claimed(
                campaign,
                delivery,
            )

        return len(claimed)



    def _send_claimed(
        self,
        campaign: Campaign,
        delivery: EmailDelivery,
    ):
        """
        Send one SENDING delivery through the sender it was assigned at claim
        time, then record the outcome. The claim already cancelled deliveries
        whose contact is unsubscribed, so those never reach this point.
        """

        delivery_id = delivery.id

        sender_account = (
            self.db.query(SenderAccount)
            .filter(
                SenderAccount.id
                == delivery.sender_account_id
            )
            .first()
        )


        if not sender_account:

            fail_delivery(
                self.db,
                delivery_id,
                "Sender account not found.",
            )

            return


        try:
            email = render_campaign_email(self.db, campaign)
        except ValueError:
            # Invalid Variant state: permanent failure of this delivery, never retried.
            fail_delivery(
                self.db,
                delivery_id,
                "Variant content is invalid.",
            )
            return


        result = send_campaign_email(
            sender_email=sender_account.email,
            sender_name=email.from_name or sender_account.name,
            encrypted_password=sender_account.encrypted_password,
            recipient_email=delivery.recipient_email,
            subject=email.subject,
            body=email.html,
            delivery_id=delivery_id,
            contact_id=delivery.contact_id,
        )


        if result["success"]:

            complete_delivery(
                self.db,
                delivery_id,
            )

        else:

            fail_delivery(
                self.db,
                delivery_id,
                result["message"],
            )

            if is_sender_failure(result["message"]):
                self._mark_sender_failed(
                    sender_account.id,
                    result["message"],
                )



    def _mark_sender_failed(
        self,
        sender_account_id: int,
        message: str,
    ):
        """
        The sender itself is broken (auth/disabled/quota): FAILED makes it
        ineligible for new claims. It becomes VERIFIED again only through
        the normal sender verification flow.
        """

        sender = self.db.get(
            SenderAccount,
            sender_account_id,
        )

        if sender and sender.status == SenderAccountStatus.VERIFIED:

            sender.status = SenderAccountStatus.FAILED
            sender.verified = False
            sender.last_error = message[:500]

            self.db.commit()



    def _update_campaign_totals(
        self,
        campaign_id: int,
    ):
        """
        Counters are recounted from the deliveries' final states, so a
        delivery is counted once no matter how many passes or workers ran.
        """

        def count(status):
            return (
                self.db.query(func.count(EmailDelivery.id))
                .filter(
                    EmailDelivery.campaign_id == campaign_id,
                    EmailDelivery.status == status,
                )
                .scalar()
            )


        sent = count(EmailDeliveryStatus.SENT)
        failed = count(EmailDeliveryStatus.FAILED)
        unfinished = (
            count(EmailDeliveryStatus.PENDING)
            + count(EmailDeliveryStatus.SENDING)
        )


        self.db.expire_all()

        campaign = self.db.get(Campaign, campaign_id)

        if campaign:

            campaign.sent_count = sent
            campaign.failed_count = failed

            if unfinished:
                campaign.status = CampaignStatus.RUNNING
            elif failed == 0:
                campaign.status = CampaignStatus.COMPLETED
            else:
                campaign.status = CampaignStatus.FAILED

            self.db.commit()


        return {
            "sent": sent,
            "failed": failed,
        }
