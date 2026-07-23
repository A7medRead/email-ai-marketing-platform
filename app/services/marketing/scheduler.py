from apscheduler.schedulers.background import BackgroundScheduler

from app.database.database import SessionLocal
from app.services.marketing.campaign_scheduler_service import CampaignSchedulerService


scheduler = BackgroundScheduler()


def run_campaign_scheduler():

    db = SessionLocal()

    try:
        service = CampaignSchedulerService(db)
        service.run_scheduled_campaigns()

    finally:
        db.close()



def start_scheduler():

    scheduler.add_job(
        run_campaign_scheduler,
        "interval",
        minutes=1,
        id="campaign_scheduler",
        replace_existing=True,
    )

    scheduler.start()
