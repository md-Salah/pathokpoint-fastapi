from fastapi import Query
from pydantic import EmailStr, Field
from fastapi_filter.contrib.sqlalchemy import Filter

from app.models.user import User
from app.constant import Role

class UserFilter(Filter):
    q: str | None = Field(Query(None, description='Search by email, phone number, or username'))
    username: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = Field(Query(None, description='Format +8801500001111'))
    role: Role | None = None

    class Constants(Filter.Constants):
        model = User
        search_field_name = 'q'
        search_model_fields = ['email', 'phone_number', 'username']
        
    