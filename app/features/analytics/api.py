from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.core.dependencies import get_current_user
from app.features.users.model import User
from app.features.campaigns.model import Campaign
from app.features.contacts.model import Contact
from app.features.templates.model import Template

from app.features.email_generation.repository import (
    get_dashboard_stats,
)

from app.features.analytics.dashboard_service import (
    DashboardAnalyticsService,
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

from app.features.campaigns.model import Campaign
from app.features.campaigns.delivery_model import EmailDelivery


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




@router.get("/analytics")
def dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    service = DashboardAnalyticsService(db)

    return service.get_dashboard_analytics(
        user_id=current_user.id
    )




@router.get("/top-campaigns")
def top_campaigns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    service = DashboardAnalyticsService(db)

    return service.get_top_campaigns(
        user_id=current_user.id
    )


@router.get("/activity")
def dashboard_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    activities = []

    campaigns = (
        db.query(Campaign)
        .filter(
            Campaign.user_id == current_user.id
        )
        .order_by(
            Campaign.created_at.desc()
        )
        .limit(5)
        .all()
    )

    for c in campaigns:
        activities.append({
            "type": "campaign",
            "icon": "✈",
            "color": "purple",
            "text": f'Campaign "{c.name}" was created',
            "time": c.created_at
        })


    contacts = (
        db.query(Contact)
        .filter(
            Contact.user_id == current_user.id
        )
        .order_by(
            Contact.created_at.desc()
        )
        .limit(5)
        .all()
    )

    for c in contacts:
        activities.append({
            "type": "contact",
            "icon": "👤",
            "color": "green",
            "text": f'New contact "{c.first_name} {c.last_name or ""}" added',
            "time": c.created_at
        })


    templates = (
        db.query(Template)
        .filter(
            Template.user_id == current_user.id
        )
        .order_by(
            Template.created_at.desc()
        )
        .limit(5)
        .all()
    )

    for t in templates:
        activities.append({
            "type": "template",
            "icon": "📄",
            "color": "blue",
            "text": f'Template "{t.name}" created',
            "time": t.created_at
        })


    activities.sort(
        key=lambda x: x["time"],
        reverse=True
    )

    return activities[:5]

