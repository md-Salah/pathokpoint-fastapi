from fastapi import Query
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import UUID4, Field

from app.constant.country import Country
from app.filter_schema.base import BaseFilter
from app.models.author import Author


class AuthorFilter(BaseFilter, Filter):
    id__in: list[UUID4] | None = None
    q: str | None = Field(
        Query(None, description='Search by author name or slug'))
    name: str | None = None
    slug__in: list[str] | None = None
    country: Country | None = None
    is_popular: bool | None = None
    is_in_menu: bool | None = None
    followers_count__lte: int | None = None
    followers_count__gte: int | None = None

    category__slug__in: list[str] | None = None
    publisher__slug__in: list[str] | None = None
    tag__slug__in: list[str] | None = None

    class Constants(Filter.Constants):
        model = Author
