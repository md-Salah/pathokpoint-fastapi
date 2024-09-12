from pydantic import UUID4, PositiveInt, NonNegativeFloat, NonNegativeInt
from typing import ClassVar

from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.common import BookOut


class ItemIn(BaseModel):
    book_id: UUID4
    quantity: PositiveInt

    _example: ClassVar = {
        "book_id": "550e8400-e29b-41d4-a716-446655440000",
        "quantity": 1,
    }


class ItemUpdate(BaseModel):
    book_id: UUID4
    quantity: NonNegativeInt

    _example: ClassVar = {
        **ItemIn._example,
    }


class ItemOut(BaseModel):
    book: BookOut
    quantity: NonNegativeInt
    regular_price: NonNegativeFloat
    sold_price: NonNegativeFloat

    _example: ClassVar = {
        'book': BookOut._example,
        "quantity": 1,
        'regular_price': 100,
        'sold_price': 90,
    }
