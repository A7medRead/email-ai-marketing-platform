from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)

from sqlalchemy.orm import Session

import logging
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageOps, UnidentifiedImageError



from app.infrastructure.database import get_db


from app.features.users.schemas import (
    UserRegister,
    UserResponse,
    LoginRequest,
    TokenResponse,
    UserUpdate,
)


from app.features.users.service import (
    register_user,
    login_user,
    create_password_reset_token,
    reset_password,
)


from app.core.dependencies import get_current_user

from app.features.users.model import User



router = APIRouter(
    prefix="/users",
    tags=["Users"],
)





@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    request: UserRegister,
    db: Session = Depends(get_db),
):

    try:

        return register_user(
            db=db,
            data=request,
        )


    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )








from fastapi.security import OAuth2PasswordRequestForm



@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    try:

        return login_user(
            db=db,
            data=form_data,
        )


    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )








@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):

    return current_user







@router.put(
    "/me",
    response_model=UserResponse,
)
def update_me(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):


    for key, value in data.model_dump(
        exclude_unset=True
    ).items():


        setattr(
            current_user,
            key,
            value
        )



    db.commit()


    db.refresh(
        current_user
    )


    return current_user







# ============================
# Upload Avatar
# ============================


@router.put(
    "/me/avatar",
    response_model=UserResponse,
)
def upload_avatar(

    file: UploadFile = File(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user),

):


    content = file.file.read(5 * 1024 * 1024 + 1)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Avatar must be 5 MB or smaller.")

    try:
        with Image.open(BytesIO(content)) as uploaded:
            if uploaded.format not in {"JPEG", "PNG", "WEBP"}:
                raise HTTPException(status_code=415, detail="Use a JPEG, PNG, or WebP image.")
            image = ImageOps.exif_transpose(uploaded)
            image.thumbnail((1200, 1200))
            output = BytesIO()
            extension, output_format = {
                "JPEG": ("jpg", "JPEG"),
                "PNG": ("png", "PNG"),
                "WEBP": ("webp", "WEBP"),
            }[uploaded.format]
            image.save(output, format=output_format)
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=415, detail="Uploaded file is not a valid image.") from exc

    filename = f"user_{current_user.id}.{extension}"
    avatar_dir = Path("uploads/avatars")
    avatar_dir.mkdir(parents=True, exist_ok=True)
    path = avatar_dir / filename
    path.write_bytes(output.getvalue())



    current_user.avatar = (
        f"/uploads/avatars/{filename}"
    )



    db.commit()


    db.refresh(
        current_user
    )



    return current_user

# ============================
# Forgot Password
# ============================


from pydantic import BaseModel


class ForgotPasswordRequest(BaseModel):
    email: str



class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str



@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):

    try:
        create_password_reset_token(db=db, email=data.email)
    except Exception:
        logging.exception("Password recovery email could not be sent")

    return {
        "message": "If an account matches that address, a reset link will be sent."
    }





@router.post("/reset-password")
def change_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):

    try:

        reset_password(
            db=db,
            token=data.token,
            new_password=data.new_password,
        )


        return {
            "message": "Password updated"
        }


    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
