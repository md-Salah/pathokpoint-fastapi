from pydantic import ConfigDict, Field, PositiveInt, UUID4, PositiveFloat, field_validator, ValidationInfo
import re

from app.pydantic_schema.mixins import IdTimestampMixin
from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.common import UserOut, ImageOut

example_review = {
    "product_rating": 5,
    "time_rating": 5,
    "delivery_rating": 5,
    "website_rating": 5,
    "comment": "This is a great book!"
}

example_review_update = {
    **example_review,
    "images": ["uuid4"]
}

example_review_in = {
    **example_review,
    "order_id": "uuid4",
    "book_id": "uuid4",
    "images": ["uuid4"],
}

example_review_out = {
    **IdTimestampMixin._example,
    **example_review_in,
    'average_rating': 5.0,
    'is_approved': True,
    'user': UserOut._example,
    'order_id': 'uuid4',
    'book_id': 'uuid4',
    'images': [ImageOut._example]
}


class ReviewBase(BaseModel):
    product_rating: PositiveInt = Field(ge=1, le=5)
    time_rating: PositiveInt = Field(ge=1, le=5)
    delivery_rating: PositiveInt = Field(ge=1, le=5)
    website_rating: PositiveInt = Field(ge=1, le=5)
    comment: str | None = Field(None, min_length=3, max_length=500)

    @field_validator('comment')
    @classmethod
    def contains_spam(cls, v: str):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        url_pattern = r'\b(?:https?://|www\.)\S+\b'

        if re.search(email_pattern, v) or re.search(url_pattern, v):
            raise ValueError('Review cannot contain email or URL')
        return v


class CreateReview(ReviewBase):
    order_id: UUID4 | None = None
    book_id: UUID4 | None = None
    images: list[UUID4] = []
    model_config = ConfigDict(json_schema_extra={"example": example_review_in})

    @field_validator('book_id')
    @classmethod
    def book_or_order_required(cls, v, info: ValidationInfo):
        if not any([v, info.data.get('order_id')]):
            raise ValueError('Review must have either book_id or order_id')
        elif all([v, info.data.get('order_id')]):
            raise ValueError('Review cannot have both book_id and order_id')
        return v


class UpdateReview(ReviewBase):
    product_rating: PositiveInt | None = Field(None, ge=1, le=5)
    time_rating: PositiveInt | None = Field(None, ge=1, le=5)
    delivery_rating: PositiveInt | None = Field(None, ge=1, le=5)
    website_rating: PositiveInt | None = Field(None, ge=1, le=5)
    images: list[UUID4] | None = None

    model_config = ConfigDict(
        json_schema_extra={"example": example_review_update})


class ReviewOut(CreateReview, IdTimestampMixin):
    average_rating: PositiveFloat = Field(ge=1, le=5)
    is_approved: bool
    user: UserOut
    images: list[ImageOut]

    model_config = ConfigDict(json_schema_extra={"example":
                                                 example_review_out})
