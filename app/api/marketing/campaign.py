from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.repositories.marketing import campaign_repository
from app.schemas.marketing.campaign import (
    CampaignCreate,
    CampaignResponse,
    CampaignUpdate,
)
from app.services.marketing import campaign_service
from app.services.marketing.email_delivery_service import EmailDeliveryService
from app.services.marketing.campaign_sender_service import CampaignSenderService

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
    try:
        return campaign_service.create_campaign(
            db=db,
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return campaign_service.get_campaigns(
        db=db,
        user_id=current_user.id,
    )


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
    campaign = campaign_repository.get_campaign_by_id(
        db=db,
        campaign_id=campaign_id,
        user_id=current_user.id,
    )

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found.",
        )

    try:
        return campaign_service.update_campaign(
            db=db,
            campaign=campaign,
            data=data,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.delete(
    "/{campaign_id}",
)
def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    campaign = campaign_repository.get_campaign_by_id(
        db=db,
        campaign_id=campaign_id,
        user_id=current_user.id,
    )

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found.",
        )

    campaign_service.delete_campaign(
        db=db,
        campaign=campaign,
    )

    return {
        "message": "Campaign deleted successfully."
    }

@router.post(
    "/{campaign_id}/prepare",
)
def prepare_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    campaign = campaign_repository.get_campaign_by_id(
        db=db,
        campaign_id=campaign_id,
        user_id=current_user.id,
    )


    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found.",
        )


    service = EmailDeliveryService(
        db=db
    )


    deliveries = service.create_campaign_deliveries(
        campaign=campaign,
    )


    return {
        "message": "Campaign prepared successfully.",
        "deliveries_created": len(deliveries),
    }

@router.post(
    "/{campaign_id}/send",
)
def send_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    campaign = campaign_repository.get_campaign_by_id(
        db=db,
        campaign_id=campaign_id,
        user_id=current_user.id,
    )


    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found.",
        )


    sender = CampaignSenderService(
        db=db
    )


    result = sender.send_campaign(
        campaign_id=campaign_id,
    )


    return {
        "message": "Campaign sending completed.",
        "result": result,
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

    campaign = campaign_repository.get_campaign_by_id(
        db=db,
        campaign_id=campaign_id,
        user_id=current_user.id,
    )


    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found.",
        )


    def run_sender():

        sender = CampaignSenderService(
            db=db
        )

        sender.send_campaign(
            campaign_id=campaign_id,
        )


    background_tasks.add_task(
        run_sender
    )


    return {
        "message": "Campaign sending started.",
        "campaign_id": campaign_id,
    }
