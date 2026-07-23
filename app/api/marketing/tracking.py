from datetime import datetime

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.marketing.email_delivery import (
    EmailDelivery,
    EmailDeliveryStatus,
)


router = APIRouter(
    prefix="/tracking",
    tags=["Tracking"],
)


PIXEL = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00"
    b"\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDAT"
    b"x\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\r\n-\xb4"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


@router.get("/open/{delivery_id}")
def track_open(
    delivery_id: int,
    db: Session = Depends(get_db),
):

    delivery = (
        db.query(EmailDelivery)
        .filter(
            EmailDelivery.id == delivery_id
        )
        .first()
    )

    if delivery:

        delivery.status = EmailDeliveryStatus.OPENED
        delivery.opened_at = datetime.utcnow()

        db.commit()


    return Response(
        content=PIXEL,
        media_type="image/png",
    )


@router.get("/click/{delivery_id}")
def track_click(
    delivery_id: int,
    db: Session = Depends(get_db),
):

    delivery = (
        db.query(EmailDelivery)
        .filter(
            EmailDelivery.id == delivery_id
        )
        .first()
    )

    if delivery:

        delivery.status = EmailDeliveryStatus.CLICKED
        delivery.clicked_at = datetime.utcnow()

        db.commit()


    return {
        "message": "Click tracked"
    }
