from pydantic import EmailStr, Field

from app.pydantic_schema.base import BaseModel


class ContactUs(BaseModel):
    name: str
    email: EmailStr
    phone_number: str = Field(
        min_length=10, max_length=14, pattern=r'^\+?\d{10,14}$')
    message: str = Field(min_length=10, max_length=10000)
