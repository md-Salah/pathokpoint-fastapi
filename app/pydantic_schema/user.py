from pydantic import EmailStr, ConfigDict, Field, SecretStr, UUID4

from app.pydantic_schema.mixins import IdTimestampMixin, id_timestamp_mixin_example
from app.pydantic_schema.base import BaseModel

from app.constant.role import Role

example_user = {
    "first_name": "Md",
    "last_name": "Abdullah",
    "username": "md_abdullah",
    "email": "abdullah2024@gmail.com",
    "phone_number": "+8801712345678",
    "image": "https://example.com/image.png"
}

example_user_in = {
    **example_user,
    "password": "********",
}

example_user_out = {
    **example_user,
    "is_verified": True,
    "role": Role.customer,
}

example_update_user_by_admin = {
    **example_user_out,
    "password": "*********",
}


class UserBase(BaseModel):
    first_name: str | None = Field(None, min_length=2, max_length=50, pattern=r'^[a-zA-Z ]+$')
    last_name: str | None = Field(None, min_length=2, max_length=50, pattern=r'^[a-zA-Z ]+$')
    username: str | None = Field(None, min_length=5, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    email: EmailStr
    phone_number: str | None = Field(None, min_length=14, max_length=14, pattern=r'^\+\d{13}$')
    image: str | UUID4 | None = None

class CreateUser(UserBase):
    password: SecretStr = Field(..., min_length=8, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={"example": example_user_in}) # type: ignore


class UpdateUser(CreateUser):
    email: EmailStr | None = None
    password: SecretStr | None = None


class UserOut(UserBase, IdTimestampMixin):
    is_verified: bool
    role: Role
    
    model_config = ConfigDict(
        json_schema_extra={"example": example_user_out | id_timestamp_mixin_example})
    

class UpdateUserByAdmin(UpdateUser):
    is_verified: bool | None = None
    role: Role | None = None

    model_config = ConfigDict(
        json_schema_extra={"example": example_update_user_by_admin }) 
    