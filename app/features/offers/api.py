from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.features.offers.model import Offer
from app.features.offers.schemas import OfferCreate, OfferResponse, OfferUpdate
from app.features.users.model import User
from app.infrastructure.database import get_db

router = APIRouter(prefix="/offers", tags=["Offers"])


@router.get("/", response_model=list[OfferResponse])
def list_offers(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Offer).filter(Offer.user_id == user.id).order_by(Offer.created_at.desc()).all()


@router.post("/", response_model=OfferResponse, status_code=201)
def create_offer(data: OfferCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    values = data.model_dump()
    if values.get("cta_url"):
        values["cta_url"] = str(values["cta_url"])
    offer = Offer(user_id=user.id, **values)
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer


@router.put("/{offer_id}", response_model=OfferResponse)
def update_offer(offer_id: int, data: OfferUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    offer = db.query(Offer).filter(Offer.id == offer_id, Offer.user_id == user.id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "cta_url" and value:
            value = str(value)
        setattr(offer, field, value)
    if offer.starts_at and offer.expires_at and offer.expires_at <= offer.starts_at:
        raise HTTPException(status_code=400, detail="Offer expiry must be after its start date.")
    db.commit()
    db.refresh(offer)
    return offer


@router.delete("/{offer_id}")
def delete_offer(offer_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    offer = db.query(Offer).filter(Offer.id == offer_id, Offer.user_id == user.id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    db.delete(offer)
    db.commit()
    return {"message": "Offer deleted"}
