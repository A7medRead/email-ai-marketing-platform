from sqlalchemy.orm import Session

from app.models.template import Template


def create_template(
    db: Session,
    user_id: int,
    name: str,
    purpose: str,
    description: str,
    tone: str,
    language: str,
):
    template = Template(
        user_id=user_id,
        name=name,
        purpose=purpose,
        description=description,
        tone=tone,
        language=language,
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return template


def get_all_templates(
    db: Session,
    user_id: int,
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
):
    query = (
        db.query(Template)
        .filter(Template.user_id == user_id)
    )

    if search:
        query = query.filter(
            (Template.name.ilike(f"%{search}%")) |
            (Template.purpose.ilike(f"%{search}%"))
        )

    return (
        query.order_by(Template.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

def get_template_by_id(
    db: Session,
    user_id: int,
    template_id: int,
):
    return (
        db.query(Template)
        .filter(
            Template.id == template_id,
            Template.user_id == user_id,
        )
        .first()
    )


def update_template(
    db: Session,
    template: Template,
    name: str,
    purpose: str,
    description: str,
    tone: str,
    language: str,
):
    template.name = name
    template.purpose = purpose
    template.description = description
    template.tone = tone
    template.language = language

    db.commit()
    db.refresh(template)

    return template


def delete_template(
    db: Session,
    template: Template,
):
    db.delete(template)
    db.commit()