from pydantic import BaseModel, EmailStr
from datetime import datetime



class UserRegister(BaseModel):

    name: str

    email: EmailStr

    password: str





class UserUpdate(BaseModel):

    name: str | None = None

    username: str | None = None

    avatar: str | None = None

    phone: str | None = None

    country: str | None = None

    city: str | None = None

    timezone: str | None = None

    preferred_language: str | None = None

    preferred_tone: str | None = None

    preferred_length: str | None = None





class UserResponse(BaseModel):

    id: int

    name: str

    username: str | None = None

    email: EmailStr


    avatar: str | None = None

    phone: str | None = None

    country: str | None = None

    city: str | None = None


    timezone: str | None = None


    preferred_language: str | None = None

    preferred_tone: str | None = None

    preferred_length: str | None = None


    created_at: datetime | None = None

    updated_at: datetime | None = None

    last_login: datetime | None = None



    model_config = {
        "from_attributes": True
    }





class LoginRequest(BaseModel):

    email: EmailStr

    password: str





class TokenResponse(BaseModel):

    access_token: str

    token_type: str