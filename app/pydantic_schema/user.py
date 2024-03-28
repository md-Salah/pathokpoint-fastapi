from pydantic import EmailStr, ConfigDict, Field, SecretStr, UUID4

from app.pydantic_schema.mixins import IdTimestampMixin
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

example_user_in_by_admin = {
    **example_user_in,
    "is_verified": False,
    "role": Role.customer
}

example_user_out = {
    **example_user,
    **IdTimestampMixin._example,
    "is_verified": True,
    "role": Role.customer,
}


class UserBase(BaseModel):
    first_name: str | None = Field(None, min_length=2, max_length=50, pattern=r'^[a-zA-Z ]+$')
    last_name: str | None = Field(None, min_length=2, max_length=50, pattern=r'^[a-zA-Z ]+$')
    username: str | None = Field(None, min_length=5, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    email: EmailStr
    phone_number: str | None = Field(None, min_length=14, max_length=14, pattern=r'^\+\d{13}$')
    image: UUID4 | None = None


class CreateUser(UserBase):
    password: SecretStr = Field(..., min_length=8, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={"example": example_user_in},  # type: ignore
        str_to_lower=False,
        str_strip_whitespace=False,
        )  


class UpdateUser(CreateUser):
    email: EmailStr = Field(None)
    password: SecretStr = Field(None, min_length=8, max_length=100)


class CreateUserByAdmin(CreateUser):
    is_verified: bool = False
    role: Role = Role.customer

    model_config = ConfigDict(
        json_schema_extra={"example": example_user_in_by_admin})


class UpdateUserByAdmin(CreateUserByAdmin):
    email: EmailStr = Field(None)
    password: SecretStr = Field(None, min_length=8, max_length=100)


class UserOut(UserBase, IdTimestampMixin):
    username: str = Field(min_length=5, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    is_verified: bool
    role: Role

    model_config = ConfigDict(
        json_schema_extra={"example": example_user_out})
