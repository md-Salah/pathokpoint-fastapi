from fastapi_filter.contrib.sqlalchemy import Filter

from app.models.category import Category

class CategoryFilter(Filter):
    q: str | None = None
    name: str | None = None
    slug: str | None = None

    is_islamic: bool | None = None
    is_english_featured: bool | None = None
    is_bangla_featured: bool | None = None
    is_job_featured: bool | None = None
    is_comics: bool | None = None
    is_popular: bool | None = None
    is_big_sale: bool | None = None

    class Constants(Filter.Constants):
        model = Category
        search_field_name = 'q'
        search_model_fields = ['name', 'slug']
        
