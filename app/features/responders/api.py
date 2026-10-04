from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.features.responders.schemas import ResponderCreate, ResponderResponse, ResponderUpdate
from app.features.responders.service import ResponderService
from app.features.users.model import User
from app.infrastructure.database import get_db

router = APIRouter(prefix="/responders", tags=["Responders"])


@router.get("/", response_model=list[ResponderResponse])
def list_responders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ResponderService(db).list_owned(user.id)


@router.post("/", response_model=ResponderResponse, status_code=201)
def create_responder(data: ResponderCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ResponderService(db).create(user.id, data)


@router.get("/{responder_id}", response_model=ResponderResponse)
def get_responder(responder_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return ResponderService(db).get_owned(responder_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{responder_id}", response_model=ResponderResponse)
def update_responder(
    responder_id: int, data: ResponderUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    try:
        return ResponderService(db).update(responder_id, user.id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{responder_id}")
def delete_responder(responder_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = ResponderService(db)
    try:
        service.get_owned(responder_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    try:
        service.delete(responder_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"message": "Responder deleted"}
