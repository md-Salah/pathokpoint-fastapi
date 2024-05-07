from pydantic import EmailStr, ConfigDict, Field, SecretStr, PastDate

from app.constant.gender import Gender
from app.pydantic_schema.mixins import IdTimestampMixin
from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.field import PhoneNumberField, UsernameField, PasswordField, FirstLastNameField

from app.constant.role import Role

base_user = {
    "first_name": "Md",
    "last_name": "Abdullah",
    "phone_number": "+8801712345678",
    "date_of_birth": "1948-11-13",
    "gender": Gender.male
}

example_user_in = {
    **base_user,
    "email": "abdullah2024@gmail.com",
    "password": "secret-password",
}

example_user_in_by_admin = {
    **example_user_in,
    "role": Role.customer
}

example_user_out = {
    **base_user,
    **IdTimestampMixin._example,
    "username": "md-abdullah",
    'email': 'user@example.com',
    "role": Role.customer,
}


class UserBase(BaseModel):
    first_name: str = FirstLastNameField()
    last_name: str = FirstLastNameField()
    phone_number: str | None = PhoneNumberField(None)
    date_of_birth: PastDate | None = None
    gender: Gender | None = None

class CreateUser(UserBase):
    email: EmailStr
    password: SecretStr = PasswordField()

    model_config = ConfigDict(
        json_schema_extra={"example": {**example_user_in}})


class CreateUserByAdmin(CreateUser):
    role: Role = Role.customer

    model_config = ConfigDict(
        json_schema_extra={"example": example_user_in_by_admin})


class UpdateMe(UserBase):
    first_name: str = FirstLastNameField(None)
    last_name: str = FirstLastNameField(None)

    model_config = ConfigDict(
        json_schema_extra={"example": {**base_user}})


class UpdateUserByAdmin(CreateUserByAdmin):
    first_name: str = FirstLastNameField(None)
    last_name: str = FirstLastNameField(None)
    email: EmailStr = Field(None)
    password: SecretStr = PasswordField(None)


class UserOut(UserBase, IdTimestampMixin):
    username: str = UsernameField()
    email: EmailStr
    role: Role

    model_config = ConfigDict(
        json_schema_extra={"example": example_user_out})
