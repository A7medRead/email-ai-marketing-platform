from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.features.campaigns.model import Campaign
from app.features.offers.model import Offer, OfferVariant
from app.features.offers.schemas import OfferVariantCreate
from app.features.responders.service import ResponderService


class OfferInUseError(Exception):
    """Raised when an Offer or Variant is still referenced by a Campaign (API maps it to 409).

    Locked decision 13A.13A: deleting a referenced Offer/Variant would leave a Campaign without its
    creative and could make it send the wrong content, so the delete is refused and the Campaign
    is never detached (offer_id/variant_id are never cleared).
    """


class OfferService:
    def __init__(self, db: Session):
        self.db = db

    def get_owned(self, offer_id: int, user_id: int) -> Offer:
        # Every lookup is scoped by user_id; another user's id is indistinguishable from "not found".
        offer = self.db.query(Offer).filter(Offer.id == offer_id, Offer.user_id == user_id).first()
        if not offer:
            raise ValueError("Offer not found.")
        return offer

    def resolve_responder_id(self, user_id: int, responder_id: int | None) -> int:
        """Validate an explicit Responder (must belong to the user) or fall back to the user's default.

        Keeps the invariant Offer.user_id == Offer.responder.user_id: a Responder is only ever
        resolved through the caller's own user_id, never a global or another user's default.
        """
        responders = ResponderService(self.db)
        if responder_id is None:
            return responders.get_or_create_default(user_id).id
        return responders.get_owned(responder_id, user_id).id

    def get_owned_variant(self, variant_id: int, user_id: int) -> OfferVariant:
        # A Variant has no user_id: ownership is derived through its Offer (User -> Responder -> Offer -> Variant).
        variant = (
            self.db.query(OfferVariant)
            .join(Offer, OfferVariant.offer_id == Offer.id)
            .filter(OfferVariant.id == variant_id, Offer.user_id == user_id)
            .first()
        )
        if not variant:
            raise ValueError("Variant not found.")
        return variant

    def create_variant(self, offer_id: int, user_id: int, data: OfferVariantCreate) -> OfferVariant:
        offer = self.get_owned(offer_id, user_id)
        values = data.model_dump()
        if values["image_url"]:
            values["image_url"] = str(values["image_url"])
        variant = OfferVariant(offer_id=offer.id, **values)
        self.db.add(variant)
        self.db.commit()
        self.db.refresh(variant)
        return variant

    def list_variants(self, offer_id: int, user_id: int) -> list[OfferVariant]:
        offer = self.get_owned(offer_id, user_id)
        return self.db.query(OfferVariant).filter(OfferVariant.offer_id == offer.id).order_by(OfferVariant.id).all()

    def get_offer_variant(self, offer_id: int, variant_id: int, user_id: int) -> OfferVariant:
        offer = self.get_owned(offer_id, user_id)
        variant = (
            self.db.query(OfferVariant)
            .filter(OfferVariant.id == variant_id, OfferVariant.offer_id == offer.id)
            .first()
        )
        if not variant:
            raise ValueError("Variant not found.")
        return variant

    def update_variant(self, offer_id: int, variant_id: int, user_id: int, data: OfferVariantCreate) -> OfferVariant:
        variant = self.get_offer_variant(offer_id, variant_id, user_id)
        for field, value in data.model_dump().items():
            setattr(variant, field, str(value) if field == "image_url" and value else value)
        self.db.commit()
        self.db.refresh(variant)
        return variant

    def delete_variant(self, offer_id: int, variant_id: int, user_id: int) -> None:
        variant = self.get_offer_variant(offer_id, variant_id, user_id)
        if self.db.query(Campaign.id).filter(Campaign.variant_id == variant.id).first():
            raise OfferInUseError("Variant is used by one or more campaigns and cannot be deleted.")
        self.db.delete(variant)
        self.db.commit()

    def delete_offer(self, offer_id: int, user_id: int) -> None:
        offer = self.get_owned(offer_id, user_id)
        # Checked in the app, not left to FK actions (SQLite FKs are off at runtime). Variants are
        # included so a Campaign referencing only a Variant still blocks deleting its Offer.
        variant_ids = [v.id for v in offer.variants]
        in_use = Campaign.offer_id == offer.id
        if variant_ids:
            in_use = or_(in_use, Campaign.variant_id.in_(variant_ids))
        if self.db.query(Campaign.id).filter(in_use).first():
            raise OfferInUseError("Offer is used by one or more campaigns and cannot be deleted.")
        self.db.delete(offer)
        self.db.commit()
