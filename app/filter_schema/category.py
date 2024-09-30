from fastapi import Query
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import UUID4, Field

from app.filter_schema.base import BaseFilter
from app.models.category import Category


class CategoryFilter(BaseFilter, Filter):
    id__in: list[UUID4] | None = None
    q: str | None = Field(Query(None, description='Search by name or slug'))
    name: str | None = None
    slug__in: list[str] | None = None

    is_islamic: bool | None = None
    is_english_featured: bool | None = None
    is_bangla_featured: bool | None = None
    is_job_featured: bool | None = None
    is_comics: bool | None = None
    is_popular: bool | None = None
    is_big_sale: bool | None = None
    is_in_menu: bool | None = None

    author__slug__in: list[str] | None = None
    publisher__slug__in: list[str] | None = None
    tag__slug__in: list[str] | None = None

    class Constants(Filter.Constants):
        model = Category
