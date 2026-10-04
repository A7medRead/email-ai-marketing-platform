from sqlalchemy.orm import Session

from datetime import datetime, timedelta
import secrets
import smtplib
from email.message import EmailMessage
from urllib.parse import urlencode
from app.core.config import (
    SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD,
    SMTP_FROM_EMAIL, FRONTEND_URL,
)

from app.core.security import (
    hash_password,
    verify_password,
)

from app.core.auth import create_access_token

from app.features.users.model import User

from app.features.users.repository import (
    create_user,
    get_user_by_email,
)


def register_user(
    db: Session,
    data,
):
    user = get_user_by_email(
        db,
        data.email,
    )

    if user:
        raise ValueError("Email already exists")

    hashed_password = hash_password(
        data.password
    )

    return create_user(
        db=db,
        name=data.name,
        email=data.email,
        password=hashed_password,
    )


def login_user(
    db: Session,
    data,
):
    user = get_user_by_email(
        db,
        data.username,
    )

    if user is None:
        raise ValueError("Invalid email or password")

    if not verify_password(
        data.password,
        user.password,
    ):
        raise ValueError("Invalid email or password")

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

def create_password_reset_token(
    db: Session,
    email: str,
):

    user = get_user_by_email(
        db,
        email,
    )

    if user is None:
        return False

    if not all((SMTP_HOST, SMTP_FROM_EMAIL)):
        raise RuntimeError("Password recovery email is not configured")


    token = secrets.token_urlsafe(32)


    user.reset_token = token

    user.reset_token_expire = (
        datetime.utcnow()
        + timedelta(minutes=30)
    )


    db.commit()

    message = EmailMessage()
    message["Subject"] = "Reset your MailPilot password"
    message["From"] = SMTP_FROM_EMAIL
    message["To"] = user.email
    reset_url = f"{FRONTEND_URL}/reset-password?{urlencode({'token': token})}"
    message.set_content(
        f"Use this link within 30 minutes to reset your password:\n{reset_url}\n"
    )
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls()
            if SMTP_USERNAME:
                server.login(SMTP_USERNAME, SMTP_PASSWORD or "")
            server.send_message(message)
    except Exception:
        user.reset_token = None
        user.reset_token_expire = None
        db.commit()
        raise

    return True



def reset_password(
    db: Session,
    token: str,
    new_password: str,
):

    from app.core.security import hash_password


    user = (
        db.query(User)
        .filter(
            User.reset_token == token
        )
        .first()
    )


    if user is None:
        raise ValueError("Invalid token")

    if (
        user.reset_token_expire is None
        or user.reset_token_expire < datetime.utcnow()
    ):
        raise ValueError("Token has expired")


    user.password = hash_password(
        new_password
    )

    user.reset_token = None
    user.reset_token_expire = None


    db.commit()


    return True
