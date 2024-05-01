from pydantic import UUID4
from fastapi_filter.contrib.sqlalchemy import Filter

from app.models import Review


class ReviewFilter(Filter):
    q: str | None = None
    average_rating__lte: float | None = None
    average_rating__gte: float | None = None
    is_approved: bool | None = None
    book_id: UUID4 | None = None
    user_id: UUID4 | None = None
    order_id: UUID4 | None = None

    class Constants(Filter.Constants):
        model = Review
        search_field_name = 'q'
        search_model_fields = ['comment']
