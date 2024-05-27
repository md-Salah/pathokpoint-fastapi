from pydantic import UUID4, PositiveInt, NonNegativeFloat, NonNegativeInt
from typing import ClassVar

from app.pydantic_schema.base import BaseModel
from app.pydantic_schema.common import BookOut


class ItemBase(BaseModel):
    quantity: PositiveInt = 1
    
    _example: ClassVar = {
        "quantity": 1,
    }
    
class ItemIn(ItemBase):
    book_id: UUID4
    
    _example: ClassVar = {
        "book_id": "550e8400-e29b-41d4-a716-446655440000",
        **ItemBase._example
    }
    
class ItemUpdate(ItemIn):
    quantity: NonNegativeInt = 1
    is_removed: bool = False
    note: str | None = None
    
    _example: ClassVar = {
        **ItemIn._example,
        "is_removed": False,
        "note": "This is a note"
    }
    
class ItemOut(ItemBase):
    book: BookOut
    regular_price: NonNegativeFloat
    sold_price: NonNegativeFloat
    is_removed: bool = False
    note: str | None = None
    
    _example: ClassVar = {
        'book': BookOut._example,
        **ItemBase._example,
        'regular_price': 100,
        'sold_price': 90,
        'is_removed': False,
        'note': "Dead book"
    }
    
    