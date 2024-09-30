from fastapi import Query
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import UUID4, Field

from app.constant.country import Country
from app.filter_schema.base import BaseFilter
from app.models.publisher import Publisher


class PublisherFilter(BaseFilter, Filter):
    q: str | None = Field(Query(None, description='Search by name or slug'))
    id__in: list[UUID4] | None = None
    name: str | None = None
    slug__in: list[str] | None = None
    country: Country | None = None
    is_islamic: bool | None = None
    is_english: bool | None = None
    is_popular: bool | None = None
    is_in_menu: bool | None = None
    
    author__slug__in: list[str] | None = None
    category__slug__in: list[str] | None = None
    tag__slug__in: list[str] | None = None

    class Constants(Filter.Constants):
        model = Publisher
    