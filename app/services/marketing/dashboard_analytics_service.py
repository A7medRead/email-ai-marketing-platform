from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.marketing.campaign import Campaign
from app.models.marketing.email_delivery import EmailDelivery


class DashboardAnalyticsService:


    def __init__(
        self,
        db: Session,
    ):
        self.db = db



    def get_dashboard_analytics(
        self,
        user_id: int,
    ):

        total_campaigns = (
            self.db.query(Campaign)
            .filter(
                Campaign.user_id == user_id
            )
            .count()
        )


        completed_campaigns = (
            self.db.query(Campaign)
            .filter(
                Campaign.user_id == user_id,
                Campaign.status == "completed"
            )
            .count()
        )


        failed_campaigns = (
            self.db.query(Campaign)
            .filter(
                Campaign.user_id == user_id,
                Campaign.status == "failed"
            )
            .count()
        )


        total_sent = (
            self.db.query(EmailDelivery)
            .join(Campaign)
            .filter(
                Campaign.user_id == user_id,
                EmailDelivery.status == "sent"
            )
            .count()
        )


        total_failed = (
            self.db.query(EmailDelivery)
            .join(Campaign)
            .filter(
                Campaign.user_id == user_id,
                EmailDelivery.status == "failed"
            )
            .count()
        )


        success_rate = 0

        total_deliveries = total_sent + total_failed

        if total_deliveries:
            success_rate = round(
                (total_sent / total_deliveries) * 100,
                2
            )


        opened = (
            self.db.query(EmailDelivery)
            .join(Campaign)
            .filter(
                Campaign.user_id == user_id,
                EmailDelivery.opened_at.isnot(None)
            )
            .count()
        )


        clicked = (
            self.db.query(EmailDelivery)
            .join(Campaign)
            .filter(
                Campaign.user_id == user_id,
                EmailDelivery.clicked_at.isnot(None)
            )
            .count()
        )


        open_rate = 0
        click_rate = 0

        if total_deliveries:
            open_rate = round(
                (opened / total_deliveries) * 100,
                2
            )

            click_rate = round(
                (clicked / total_deliveries) * 100,
                2
            )


        return {
            "total_campaigns": total_campaigns,
            "completed_campaigns": completed_campaigns,
            "failed_campaigns": failed_campaigns,
            "total_sent": total_sent,
            "total_failed": total_failed,
            "success_rate": success_rate,
            "opened": opened,
            "clicked": clicked,
            "open_rate": open_rate,
            "click_rate": click_rate,
        }


    def get_top_campaigns(
        self,
        user_id: int,
    ):

        campaigns = (
            self.db.query(Campaign)
            .filter(
                Campaign.user_id == user_id
            )
            .order_by(
                Campaign.created_at.desc()
            )
            .limit(5)
            .all()
        )


        return [
            {
                "id": c.id,
                "name": c.name,
                "status": c.status.value,
                "sent": c.sent_count,
                "failed": c.failed_count,
                "success_rate": round(
                    (
                        c.sent_count /
                        (c.sent_count + c.failed_count)
                    ) * 100,
                    2
                ) if (c.sent_count + c.failed_count) else 0,
            }
            for c in campaigns
        ]
