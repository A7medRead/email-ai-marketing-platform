from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

from app.repositories.email_repository import (
    get_dashboard_stats,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/stats")
def dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_dashboard_stats(
        db=db,
        user_id=current_user.id,
    )

from app.models.marketing.campaign import Campaign
from app.models.marketing.email_delivery import EmailDelivery


@router.get("/marketing")
def marketing_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    campaigns = (
        db.query(Campaign)
        .filter(
            Campaign.user_id == current_user.id
        )
        .all()
    )


    deliveries = (
        db.query(EmailDelivery)
        .join(Campaign)
        .filter(
            Campaign.user_id == current_user.id
        )
        .all()
    )


    return {

        "campaigns": len(campaigns),

        "recipients": len(deliveries),

        "sent": len([
            d for d in deliveries
            if d.status.value.lower() == "sent"
        ]),

        "failed": len([
            d for d in deliveries
            if d.status.value.lower() == "failed"
        ]),

        "opened": len([
            d for d in deliveries
            if d.opened_at
        ]),

        "clicked": len([
            d for d in deliveries
            if d.clicked_at
        ]),
    }
