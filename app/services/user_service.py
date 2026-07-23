from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
)

from app.core.auth import create_access_token

from app.repositories.user_repository import (
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