from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.models.marketing.campaign import Campaign
from app.models.marketing.campaign_enums import CampaignStatus
from app.models.marketing.email_delivery import EmailDeliveryStatus
from app.models.marketing.email_delivery import EmailDelivery

from app.schemas.marketing.campaign import (
    CampaignCreate,
    CampaignResponse,
    CampaignUpdate,
)

from app.services.marketing.campaign_service import CampaignService

from app.services.marketing.email_delivery_service import EmailDeliveryService
from app.services.marketing.campaign_sender_service import CampaignSenderService
from app.services.marketing.campaign_analytics_service import CampaignAnalyticsService


router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"],
)



@router.post(
    "/",
    response_model=CampaignResponse,
)
def create_campaign(
    data: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = CampaignService(db)

    try:
        return service.create_campaign(
            user_id=current_user.id,
            data=data,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )



@router.get(
    "/",
    response_model=list[CampaignResponse],
)
def get_campaigns(
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    query = (
        db.query(Campaign)
        .filter(
            Campaign.user_id == current_user.id
        )
    )


    if search:
        query = query.filter(
            Campaign.name.ilike(f"%{search}%")
            |
            Campaign.subject.ilike(f"%{search}%")
        )


    if status:
        query = query.filter(
            Campaign.status == status.lower()
        )


    return (
        query
        .order_by(Campaign.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )



@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse,
)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = CampaignService(db)

    campaign = service.get_campaign(
        campaign_id,
        current_user.id,
    )

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found",
        )

    return campaign



@router.put(
    "/{campaign_id}",
    response_model=CampaignResponse,
)
def update_campaign(
    campaign_id: int,
    data: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = CampaignService(db)

    campaign = service.update_campaign(
        campaign_id,
        current_user.id,
        data,
    )

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found",
        )

    return campaign



@router.delete(
    "/{campaign_id}",
)
def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = CampaignService(db)

    result = service.delete_campaign(
        campaign_id,
        current_user.id,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found",
        )

    return {
        "message": "Campaign deleted successfully"
    }



@router.post(
    "/{campaign_id}/prepare",
)
def prepare_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = CampaignService(db)

    campaign = service.get_campaign(
        campaign_id,
        current_user.id,
    )

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found",
        )


    delivery_service = EmailDeliveryService(db)


    existing = delivery_service.get_campaign_deliveries(
        campaign_id
    )


    if existing:

        campaign.status = CampaignStatus.PREPARED
        db.commit()

        return {
            "message": "Campaign already prepared",
            "deliveries_created": len(existing),
        }


    deliveries = delivery_service.create_campaign_deliveries(
        campaign
    )


    campaign.status = CampaignStatus.PREPARED
    db.commit()


    return {
        "message": "Campaign prepared",
        "deliveries_created": len(deliveries),
    }



@router.post(
    "/{campaign_id}/send",
)
def send_campaign(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = CampaignService(db)

    campaign = service.get_campaign(
        campaign_id,
        current_user.id,
    )

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found",
        )


    campaign.status = CampaignStatus.RUNNING
    db.commit()


    def run_sender():

        sender = CampaignSenderService(db)

        sender.send_campaign(
            campaign_id
        )


    background_tasks.add_task(
        run_sender
    )


    return {
        "message": "Campaign sending started",
        "campaign_id": campaign_id,
    }



@router.post(
    "/{campaign_id}/retry",
)
def retry_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = CampaignService(db)

    campaign = service.get_campaign(
        campaign_id,
        current_user.id,
    )

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found",
        )


    deliveries = (
        db.query(EmailDelivery)
        .filter(
            EmailDelivery.campaign_id == campaign_id,
            EmailDelivery.status == EmailDeliveryStatus.FAILED,
        )
        .all()
    )


    if not deliveries:

        campaign.status = CampaignStatus.PREPARED
        campaign.failed_count = 0
        campaign.sent_count = 0

        db.commit()

        return {
            "message": "Campaign reset for retry",
            "retry_count": 0,
        }


    for delivery in deliveries:
        delivery.status = EmailDeliveryStatus.PENDING
        delivery.error_message = None
        delivery.sent_at = None


    campaign.status = CampaignStatus.PREPARED
    campaign.failed_count = 0
    campaign.sent_count = 0


    db.commit()


    return {
        "message": "Campaign ready for retry",
        "retry_count": len(deliveries),
    }



@router.get(
    "/{campaign_id}/analytics",
)
def campaign_analytics(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = CampaignService(db)

    campaign = service.get_campaign(
        campaign_id,
        current_user.id,
    )

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found",
        )


    analytics = CampaignAnalyticsService(db)

    return analytics.get_campaign_analytics(
        campaign_id
    )


@router.post(
    "/scheduler/run",
)
def run_scheduler(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    from app.services.marketing.campaign_scheduler_service import CampaignSchedulerService

    scheduler = CampaignSchedulerService(db)

    return scheduler.run_scheduled_campaigns()


@router.get(
    "/{campaign_id}/deliveries",
)
def get_deliveries(
    campaign_id: int,
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = CampaignService(db)

    campaign = service.get_campaign(
        campaign_id,
        current_user.id,
    )


    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found",
        )


    delivery_service = EmailDeliveryService(db)

    deliveries = delivery_service.get_campaign_deliveries(
        campaign_id,
        search=search,
        status=status,
        page=page,
        limit=limit,
    )


    total = deliveries["total"]
    items = deliveries["items"]
    pages = max(1, (total + limit - 1) // limit)

    return {
        "items": [
            {
                "id": d.id,
                "recipient_email": d.recipient_email,
                "status": d.status,
                "sent_at": d.sent_at,
                "opened_at": d.opened_at,
                "clicked_at": d.clicked_at,
                "error_message": d.error_message,
            }
            for d in items
        ],
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
        "has_previous": page > 1,
        "has_next": page < pages,
    }
