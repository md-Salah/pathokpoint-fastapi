from fastapi import Query
from pydantic import Field, UUID4
from fastapi_filter.contrib.sqlalchemy import Filter

from app.models.tag import Tag

class TagFilter(Filter):
    id__in: list[UUID4] | None = None
    q: str | None = Field(Query(None, description='Search by name or slug'))
    name: str | None = None
    slug__in: list[str] | None = None
    private: bool | None = None
    is_in_menu: bool | None = None

    class Constants(Filter.Constants):
        model = Tag
        search_field_name = 'q'
        search_model_fields = ['name', 'slug']