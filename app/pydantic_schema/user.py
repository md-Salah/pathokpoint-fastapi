from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: str | None = None
    email: EmailStr
    phone_number: str | None = None

class CreateUser(UserBase):
    password: str

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
    token: str
    