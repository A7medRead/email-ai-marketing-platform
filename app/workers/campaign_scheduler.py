from apscheduler.schedulers.background import BackgroundScheduler

from app.infrastructure.database import SessionLocal
from app.features.campaigns.scheduler_service import CampaignSchedulerService
# The worker runs in its own process and must register every ORM model before
# SQLAlchemy configures relationships used by the scheduler.
from app.features import model_registry as _model_registry  # noqa: F401


scheduler = BackgroundScheduler()


def run_campaign_scheduler():

    db = SessionLocal()

    try:
        service = CampaignSchedulerService(db)
        service.run_scheduled_campaigns()

    finally:
        db.close()



def start_scheduler():

    if scheduler.running:
        return

    scheduler.add_job(
        run_campaign_scheduler,
        "interval",
        minutes=1,
        id="campaign_scheduler",
        replace_existing=True,
    )

    scheduler.start()
