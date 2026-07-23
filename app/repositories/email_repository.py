from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.email import Email
from app.models.template import Template


def save_email(
    db: Session,
    user_id: int,
    purpose: str,
    description: str,
    tone: str,
    language: str,
    subject: str,
    body: str,
):
    email = Email(
        user_id=user_id,
        purpose=purpose,
        description=description,
        tone=tone,
        language=language,
        subject=subject,
        body=body,
    )

    db.add(email)
    db.commit()
    db.refresh(email)

    return email


def get_all_emails(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10,
):
    return (
        db.query(Email)
        .filter(Email.user_id == user_id)
        .order_by(Email.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_total_emails(
    db: Session,
    user_id: int,
):
    return (
        db.query(Email)
        .filter(Email.user_id == user_id)
        .count()
    )


def get_email_by_id(
    db: Session,
    email_id: int,
):
    return (
        db.query(Email)
        .filter(Email.id == email_id)
        .first()
    )


def update_email(
    db: Session,
    email: Email,
    purpose: str,
    description: str,
    tone: str,
    language: str,
    subject: str,
    body: str,
):
    email.purpose = purpose
    email.description = description
    email.tone = tone
    email.language = language
    email.subject = subject
    email.body = body

    db.commit()
    db.refresh(email)

    return email


def delete_email_by_id(
    db: Session,
    email_id: int,
):
    email = get_email_by_id(
        db,
        email_id,
    )

    if email is None:
        return None

    db.delete(email)
    db.commit()

    return email



def get_dashboard_stats(
    db: Session,
    user_id: int,
):

    total_emails = (
        db.query(Email)
        .filter(
            Email.user_id == user_id
        )
        .count()
    )


    current_month = datetime.now().month
    current_year = datetime.now().year


    this_month = (
        db.query(Email)
        .filter(
            Email.user_id == user_id,
            func.extract(
                "month",
                Email.created_at
            ) == current_month,
            func.extract(
                "year",
                Email.created_at
            ) == current_year,
        )
        .count()
    )


    english = (
        db.query(Email)
        .filter(
            Email.user_id == user_id,
            Email.language == "English",
        )
        .count()
    )


    arabic = (
        db.query(Email)
        .filter(
            Email.user_id == user_id,
            Email.language == "Arabic",
        )
        .count()
    )


    professional = (
        db.query(Email)
        .filter(
            Email.user_id == user_id,
            Email.tone == "Professional",
        )
        .count()
    )


    friendly = (
        db.query(Email)
        .filter(
            Email.user_id == user_id,
            Email.tone == "Friendly",
        )
        .count()
    )


    formal = (
        db.query(Email)
        .filter(
            Email.user_id == user_id,
            Email.tone == "Formal",
        )
        .count()
    )


    casual = (
        db.query(Email)
        .filter(
            Email.user_id == user_id,
            Email.tone == "Casual",
        )
        .count()
    )


    templates = (
        db.query(Template)
        .filter(
            Template.user_id == user_id
        )
        .count()
    )


    return {
        "total_emails": total_emails,

        "this_month": this_month,

        "templates": templates,

        "languages": {
            "English": english,
            "Arabic": arabic,
        },

        "tones": {
            "Professional": professional,
            "Friendly": friendly,
            "Formal": formal,
            "Casual": casual,
        },
    }