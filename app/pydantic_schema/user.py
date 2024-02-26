from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from app.pydantic_schema.auth import TokenResponse

class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: str | None = None
    email: EmailStr
    phone_number: str | None = None

class CreateUser(UserBase):
    password: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Md",
                "last_name": "Salah",
                "username": "mdsalah",
                "email": "mdsalah@gmail.com",
                "phone_number": "017xxxxxxxx",
                "password": "123456"
            },
        }
    }

class UpdateUser(UserBase):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    profile_picture: str | None = None


class ReadUser(UserBase):
    id: UUID
    role: str

    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True


class ReadUserWithToken(BaseModel):
    user: ReadUser
    token: TokenResponse
    