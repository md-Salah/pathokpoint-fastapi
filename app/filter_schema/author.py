from fastapi_filter.contrib.sqlalchemy import Filter

from app.models.author import Author
from app.constant.country import Country

class AuthorFilter(Filter):
    name: str | None = None
    slug: str | None = None
    country: Country | None = None
    is_popular: bool | None = None

    q: str | None = None
    class Constants(Filter.Constants):
        model = Author
        search_field_name = 'q'
        search_model_fields = ['name', 'slug']