from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from jose import JWTError, jwt

from app.infrastructure.database import get_db
from app.features.contacts.model import Contact
from app.features.contacts.enums import ContactStatus
from app.core.config import SECRET_KEY, ALGORITHM


router = APIRouter(
    prefix="/track",
    tags=["Tracking"],
)


@router.get("/unsubscribe/{token}")
def unsubscribe(
    token: str,
    db: Session = Depends(get_db),
):
    try:
        claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if claims.get("purpose") != "unsubscribe":
            raise JWTError("Invalid token purpose")
        contact_id = int(claims["contact_id"])
    except (JWTError, KeyError, TypeError, ValueError):
        return HTMLResponse("<h2>This unsubscribe link is invalid.</h2>", status_code=400)

    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        return HTMLResponse("<h2>This unsubscribe link is invalid.</h2>", status_code=404)

    contact.status = ContactStatus.UNSUBSCRIBED
    db.commit()


    return HTMLResponse(
        """
        <h2>You have been unsubscribed successfully.</h2>
        """
    )
