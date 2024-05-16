from fastapi import Query
from pydantic import EmailStr, Field
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_filter import FilterDepends, with_prefix

from app.models.user import User
from app.models.address import Address
from app.constant import Role, Gender


class AddressFilter(Filter):
    country: str | None = None
    city__in: list[str] | None = None
    
    class Constants(Filter.Constants):
        model = Address


class UserFilter(Filter):
    q: str | None = Field(Query(None, description='Search by email, phone number, or username'))
    username: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = Field(Query(None, description='Format +8801500001111'))
    role: Role | None = None
    gender: Gender | None = None
    address: AddressFilter | None = FilterDepends(with_prefix("address", AddressFilter))

    class Constants(Filter.Constants):
        model = User
        search_field_name = 'q'
        search_model_fields = ['email', 'phone_number', 'username']
        
    