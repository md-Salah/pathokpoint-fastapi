from pydantic import Field
from fastapi import Query
from fastapi_filter.contrib.sqlalchemy import Filter

from app.models.publisher import Publisher
from app.constant.country import Country

class PublisherFilter(Filter):
    q: str | None = Field(Query(None, description='Search by name or slug'))
    name: str | None = None
    slug: str | None = None
    country: Country | None = None
    is_islamic: bool | None = None
    is_english: bool | None = None
    is_popular: bool | None = None

    class Constants(Filter.Constants):
        model = Publisher
        search_field_name = 'q'
        search_model_fields = ['name', 'slug']