from fastapi import Query
from pydantic import Field, UUID4
from fastapi_filter.contrib.sqlalchemy import Filter

from app.models.author import Author
from app.constant.country import Country

class AuthorFilter(Filter):
    id__in: list[UUID4] | None = None
    q: str | None = Field(Query(None, description='Search by author name or slug'))
    name: str | None = None
    slug__in: list[str] | None = None
    country: Country | None = None
    is_popular: bool | None = None
    followers_count__lte: int | None = None
    followers_count__gte: int | None = None

    class Constants(Filter.Constants):
        model = Author
        search_field_name = 'q'
        search_model_fields = ['name', 'slug']
        
        