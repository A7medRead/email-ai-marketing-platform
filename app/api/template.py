from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.repositories import template_repository
from app.schemas.template_schema import (
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
)
from app.services import template_service

router = APIRouter(
    prefix="/templates",
    tags=["Templates"],
)


@router.post(
    "/",
    response_model=TemplateResponse,
)
def create_template(
    request: TemplateCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return template_service.create_template(
        db=db,
        user_id=current_user.id,
        data=request,
    )


@router.get(
    "/",
    response_model=list[TemplateResponse],
)
def get_templates(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return template_service.get_templates(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit,
        search=search,
    )


@router.put(
    "/{template_id}",
    response_model=TemplateResponse,
)
def update_template(
    template_id: int,
    request: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    template = template_repository.get_template_by_id(
        db=db,
        user_id=current_user.id,
        template_id=template_id,
    )

    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )

    return template_service.update_template(
        db=db,
        template=template,
        data=request,
    )


@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    template = template_repository.get_template_by_id(
        db=db,
        user_id=current_user.id,
        template_id=template_id,
    )

    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )

    template_service.delete_template(
        db=db,
        template=template,
    )

    return {
        "message": "Template deleted successfully",
    }