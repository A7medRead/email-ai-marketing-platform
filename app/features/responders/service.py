from sqlalchemy.orm import Session

from app.features.offers.model import Offer
from app.features.responders.model import Responder
from app.features.responders.schemas import ResponderCreate, ResponderUpdate

DEFAULT_RESPONDER_NAME = "Default Responder"


class ResponderService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, data: ResponderCreate) -> Responder:
        responder = Responder(user_id=user_id, name=data.name)
        self.db.add(responder)
        self.db.commit()
        self.db.refresh(responder)
        return responder

    def list_owned(self, user_id: int) -> list[Responder]:
        return self.db.query(Responder).filter(Responder.user_id == user_id).order_by(Responder.id).all()

    def update(self, responder_id: int, user_id: int, data: ResponderUpdate) -> Responder:
        responder = self.get_owned(responder_id, user_id)
        responder.name = data.name
        self.db.commit()
        self.db.refresh(responder)
        return responder

    def get_owned(self, responder_id: int, user_id: int) -> Responder:
        responder = (
            self.db.query(Responder)
            .filter(Responder.id == responder_id, Responder.user_id == user_id)
            .first()
        )
        if not responder:
            raise ValueError("Responder not found.")
        return responder

    def get_or_create_default(self, user_id: int) -> Responder:
        # "Default" is user-scoped (13A.3): the user's oldest Responder, created on demand. It is
        # never shared across users. Not an explicit flag; deleting the oldest empty Responder
        # shifts the default to the next one.
        responder = (
            self.db.query(Responder)
            .filter(Responder.user_id == user_id)
            .order_by(Responder.id)
            .first()
        )
        return responder or self.create(user_id, ResponderCreate(name=DEFAULT_RESPONDER_NAME))

    def delete(self, responder_id: int, user_id: int) -> None:
        responder = self.get_owned(responder_id, user_id)
        # 13A.13: never cascade into Offers and their Variants; an empty Responder may go.
        if self.db.query(Offer).filter(Offer.responder_id == responder.id).count():
            raise ValueError("Responder still has offers and cannot be deleted.")
        self.db.delete(responder)
        self.db.commit()
