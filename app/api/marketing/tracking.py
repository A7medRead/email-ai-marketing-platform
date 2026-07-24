from fastapi import APIRouter, Depends
from fastapi.responses import Response, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.database import get_db

from app.models.marketing.email_delivery import (
    EmailDelivery,
)


router = APIRouter(
    prefix="/track",
    tags=["Tracking"],
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
        if not delivery.opened_at:
            delivery.opened_at = datetime.utcnow()

            db.commit()


    # 1x1 transparent pixel
    pixel = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01"
        b"\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00"
        b"\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDAT"
        b"\x08\xd7c\xf8\xff\xff?"
        b"\x00\x05\xfe\x02\xfe"
        b"\xdc\xccY\xe7"
        b"\x00\x00\x00\x00IEND"
        b"\xaeB`\x82"
    )

    return Response(
        content=pixel,
        media_type="image/png",
    )


@router.get("/click/{delivery_id}")
def track_click(
    delivery_id: int,
    url: str,
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
        if not delivery.clicked_at:
            delivery.clicked_at = datetime.utcnow()

            db.commit()


    return RedirectResponse(
        url=url
    )
