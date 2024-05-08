from fastapi import Query
from pydantic import Field
from fastapi_filter.contrib.sqlalchemy import Filter

from app.models.tag import Tag

class TagFilter(Filter):
    q: str | None = Field(Query(None, description='Search by name or slug'))
    name: str | None = None
    slug: str | None = None
    private: bool | None = None

    class Constants(Filter.Constants):
        model = Tag
        search_field_name = 'q'
        search_model_fields = ['name', 'slug']