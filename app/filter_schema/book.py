from fastapi import Query
from typing import List
from pydantic import UUID4, Field, field_validator
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_filter import FilterDepends, with_prefix

from app.models import Book, Author, Category, Publisher, Tag
from app.constant import Cover, Language, Condition, Country, StockLocation

class TagFilter(Filter):
    id__in: List[UUID4] | None = None
    name__in: List[str] | None = None
    slug__in: List[str] | None = None

    class Constants(Filter.Constants):
        model = Tag

class PublisherFilter(Filter):
    id__in: List[UUID4] | None = None
    name__in: List[str] | None = None
    slug__in: List[str] | None = None

    class Constants(Filter.Constants):
        model = Publisher
        
class AuthorFilter(Filter):
    id__in: List[UUID4] | None = None
    name__in: List[str] | None = None
    slug__in: List[str] | None = None

    class Constants(Filter.Constants):
        model = Author

class CategoryFilter(Filter):
    id__in: List[UUID4] | None = None
    name__in: List[str] | None = None
    slug__in: List[str] | None = None

    class Constants(Filter.Constants):
        model = Category


class BookFilterMinimal(Filter):
    q: str | None = Field(Query(None, description='Search by name or slug'))
    public_id: int | None = None
    sku: str | None = None
    name: str | None = None
    slug: str | None = None
    regular_price__lte: float | None = None
    regular_price__gte: float | None = None
    sale_price__lte: float | None = None
    sale_price__gte: float | None = None
    in_stock: bool | None = None
    quantity__lte: int | None = None
    quantity__gte: int | None = None
    pre_order: bool | None = None
    cover: Cover | None = None
    language: Language | None = None
    is_used: bool | None = None
    condition__in: List[Condition] | None = None
    country__in: List[Country] | None = None
    country__nin: List[Country] | None = None
    is_draft: bool | None = None
    is_featured: bool | None = None
    is_must_read: bool | None = None
    is_vintage: bool | None = None
    is_islamic: bool | None = None
    is_translated: bool | None = None
    is_recommended: bool | None = None
    is_big_sale: bool | None = None
    is_popular: bool | None = None
    stock_location: StockLocation | None = None
    shelf: str | None = None
    bar_code: str | None = None
    author: AuthorFilter = FilterDepends(with_prefix("author", AuthorFilter))
    

    order_by: list[str] | None = Field(Query(None, description='Sort by fields created_at, updated_at, name, price, quantity, weight. Add "-" for descending order'))
    
    @field_validator('order_by')
    def restrict_sortable_fields(cls, value):
        if value is None:
            return None
        
        allowed_fields = ['created_at', 'updated_at', 'name', 'regular_price', 'sale_price', 'quantity', 'weight_in_gm', 'shelf', 'cost', 'sold_count']
        
        for field_name in value:
            field_name = field_name.replace('-', '').replace('+', '')
            if field_name not in allowed_fields:
                raise ValueError('You may only sort by {}'.format(', '.join(allowed_fields)))
        return value

    class Constants(Filter.Constants):
        model = Book
        search_field_name = 'q'
        search_model_fields = ['name', 'slug']
        

class BookFilter(BookFilterMinimal):
    publisher: PublisherFilter = FilterDepends(with_prefix("publisher", PublisherFilter))
    category: CategoryFilter = FilterDepends(with_prefix("category", CategoryFilter))
    tag: TagFilter = FilterDepends(with_prefix("tag", TagFilter))
