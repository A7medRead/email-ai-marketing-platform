from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.features.offers.model import Offer
from app.features.offers.service import OfferInUseError, OfferService
from app.features.offers.schemas import (
    OfferCreate,
    OfferResponse,
    OfferUpdate,
    OfferVariantCreate,
    OfferVariantResponse,
)
from app.features.users.model import User
from app.infrastructure.database import get_db

router = APIRouter(prefix="/offers", tags=["Offers"])


def _owned_offer(db: Session, offer_id: int, user: User) -> Offer:
    try:
        return OfferService(db).get_owned(offer_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


def _owned_variant(db: Session, offer_id: int, variant_id: int, user: User):
    try:
        return OfferService(db).get_offer_variant(offer_id, variant_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/", response_model=list[OfferResponse])
def list_offers(
    responder_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Offer).filter(Offer.user_id == user.id)
    if responder_id is not None:
        query = query.filter(Offer.responder_id == responder_id)
    return query.order_by(Offer.created_at.desc()).all()


@router.get("/{offer_id}", response_model=OfferResponse)
def get_offer(offer_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _owned_offer(db, offer_id, user)


@router.post("/", response_model=OfferResponse, status_code=201)
def create_offer(data: OfferCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    values = data.model_dump()
    for field in ("cta_url", "affiliate_url"):
        if values.get(field):
            values[field] = str(values[field])
    try:
        values["responder_id"] = OfferService(db).resolve_responder_id(user.id, values["responder_id"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
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
        if field in ("cta_url", "affiliate_url") and value:
            value = str(value)
        if field == "responder_id":
            if value is None:
                continue
            try:
                value = OfferService(db).resolve_responder_id(user.id, value)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
        setattr(offer, field, value)
    if offer.starts_at and offer.expires_at and offer.expires_at <= offer.starts_at:
        raise HTTPException(status_code=400, detail="Offer expiry must be after its start date.")
    db.commit()
    db.refresh(offer)
    return offer


@router.delete("/{offer_id}")
def delete_offer(offer_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # 404 for other users' offers first (no existence leak), then 409 if a Campaign still uses it.
    _owned_offer(db, offer_id, user)
    try:
        OfferService(db).delete_offer(offer_id, user.id)
    except OfferInUseError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"message": "Offer deleted"}


@router.get("/{offer_id}/variants", response_model=list[OfferVariantResponse])
def list_variants(offer_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _owned_offer(db, offer_id, user)
    return OfferService(db).list_variants(offer_id, user.id)


@router.post("/{offer_id}/variants", response_model=OfferVariantResponse, status_code=201)
def create_variant(
    offer_id: int, data: OfferVariantCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    _owned_offer(db, offer_id, user)
    return OfferService(db).create_variant(offer_id, user.id, data)


@router.get("/{offer_id}/variants/{variant_id}", response_model=OfferVariantResponse)
def get_variant(offer_id: int, variant_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _owned_variant(db, offer_id, variant_id, user)


@router.put("/{offer_id}/variants/{variant_id}", response_model=OfferVariantResponse)
def update_variant(
    offer_id: int,
    variant_id: int,
    data: OfferVariantCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _owned_variant(db, offer_id, variant_id, user)
    return OfferService(db).update_variant(offer_id, variant_id, user.id, data)


@router.delete("/{offer_id}/variants/{variant_id}")
def delete_variant(offer_id: int, variant_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _owned_variant(db, offer_id, variant_id, user)
    try:
        OfferService(db).delete_variant(offer_id, variant_id, user.id)
    except OfferInUseError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"message": "Variant deleted"}
