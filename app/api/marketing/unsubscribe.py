from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse

from app.database.database import get_db
from app.models.marketing.contact import Contact


router = APIRouter(
    prefix="/track",
    tags=["Tracking"],
)


@router.get("/unsubscribe/{contact_id}")
def unsubscribe(
    contact_id: int,
    db: Session = Depends(get_db),
):

    contact = (
        db.query(Contact)
        .filter(
            Contact.id == contact_id
        )
        .first()
    )

    if contact:
        contact.status = "UNSUBSCRIBE"
        db.commit()


    return HTMLResponse(
        """
        <h2>You have been unsubscribed successfully.</h2>
        """
    )
