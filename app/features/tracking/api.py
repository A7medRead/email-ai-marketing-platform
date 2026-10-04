from fastapi import APIRouter, Depends
from fastapi.responses import Response, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
import jwt
from jwt import PyJWTError as JWTError

from app.infrastructure.database import get_db

from app.features.campaigns.delivery_model import (
    EmailDelivery,
)
from app.core.config import SECRET_KEY, ALGORITHM


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


@router.get("/click")
def track_click(
    token: str,
    db: Session = Depends(get_db),
):
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if claims.get("purpose") != "click":
            raise JWTError("Invalid token purpose")
        delivery_id = int(claims["delivery_id"])
        url = claims["url"]
        if not isinstance(url, str) or not url.startswith(("https://", "http://")):
            raise JWTError("Invalid destination")
    except (JWTError, KeyError, TypeError, ValueError):
        return Response(status_code=400, content="Invalid tracking link")

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


    return RedirectResponse(url=url)
