from pydantic import Field
from pydantic_core import PydanticUndefined
from typing import Any


def FirstLastNameField(default: Any = PydanticUndefined):
    return Field(default, min_length=2, max_length=20, pattern=r'^[a-zA-Z ]+$')


def UsernameField(default: Any = PydanticUndefined):
    username_pattern = r'^[a-zA-Z0-9_.-]+$'
    return Field(default, min_length=5, max_length=25, pattern=username_pattern)


def PhoneNumberField(default: Any = PydanticUndefined):
    return Field(default, min_length=14, max_length=14, pattern=r'^\+\d{13}$')


def PasswordField(default: Any = PydanticUndefined):
    return Field(default, min_length=8, max_length=100)
