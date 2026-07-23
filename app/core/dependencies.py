from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import SECRET_KEY, ALGORITHM
from app.database.database import get_db
from app.repositories.user_repository import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
    )


    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )


        user_id = payload.get("sub")


        if user_id is None:
            raise credentials_exception

    except JWTError as e:
        raise credentials_exception

    user = get_user_by_id(
        db,
        int(user_id),
    )


    if user is None:
        raise credentials_exception

    return user
