from typing import List
from fastapi_filter.contrib.sqlalchemy import Filter

from app.models import Book
from app.constant import Cover, Language, Condition, Country, StockLocation


class BookFilter(Filter):
    q: str | None = None
    serial_number: int | None = None
    sku: str | None = None
    name: str | None = None
    slug: str | None = None
    regular_price__lte: float | None = None
    regular_price__gte: float | None = None
    sale_price__lte: float | None = None
    sale_price__gte: float | None = None
    in_stock: bool | None = None
    quantity_lte: int | None = None
    quantity_gte: int | None = None
    pre_order: bool | None = None
    cover: Cover | None = None
    language: Language | None = None
    is_used: bool | None = None
    condition__in: List[Condition] | None = None
    condition__nin: List[Condition] | None = None
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

    class Constants(Filter.Constants):
        model = Book
        search_field_name = 'q'
        search_model_fields = ['name', 'slug']
        
        