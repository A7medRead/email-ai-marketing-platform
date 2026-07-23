from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)

from sqlalchemy.orm import Session

import shutil



from app.database.database import get_db


from app.schemas.user_schema import (
    UserRegister,
    UserResponse,
    LoginRequest,
    TokenResponse,
    UserUpdate,
)


from app.services.user_service import (
    register_user,
    login_user,
)


from app.core.dependencies import get_current_user

from app.models.user import User



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


    extension = (
        file.filename
        .split(".")[-1]
    )


    filename = (
        f"user_{current_user.id}.{extension}"
    )


    path = (
        f"uploads/avatars/{filename}"
    )



    with open(
        path,
        "wb"
    ) as buffer:


        shutil.copyfileobj(
            file.file,
            buffer
        )



    current_user.avatar = (
        f"/uploads/avatars/{filename}"
    )



    db.commit()


    db.refresh(
        current_user
    )



    return current_user