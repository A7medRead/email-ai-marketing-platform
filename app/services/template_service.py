from sqlalchemy.orm import Session

from app.repositories import template_repository
from app.schemas.template_schema import (
    TemplateCreate,
    TemplateUpdate,
)


def create_template(
    db: Session,
    user_id: int,
    data: TemplateCreate,
):
    return template_repository.create_template(
        db=db,
        user_id=user_id,
        name=data.name,
        purpose=data.purpose,
        description=data.description,
        tone=data.tone,
        language=data.language,
        subject=data.subject,
        body=data.body,
    )


def get_templates(
    db: Session,
    user_id: int,
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
):
    return template_repository.get_all_templates(
        db=db,
        user_id=user_id,
        page=page,
        limit=limit,
        search=search,
    )


def update_template(
    db: Session,
    template,
    data: TemplateUpdate,
):
    return template_repository.update_template(
        db=db,
        template=template,
        name=data.name,
        purpose=data.purpose,
        description=data.description,
        tone=data.tone,
        language=data.language,
        subject=data.subject,
        body=data.body,
    )


def delete_template(
    db: Session,
    template,
):
    template_repository.delete_template(
        db=db,
        template=template,
    )