from pydantic import model_validator, ConfigDict
from typing import Optional, Set, Literal
from typing_extensions import Self
from fastapi import HTTPException

from app.pydantic_schema.mixins import TimestampMixin
from app.pydantic_schema.base import BaseModel

class BookBase(BaseModel):
    sku: Optional[str] = None
    name: str
    short_description: Optional[str] = None
    regular_price: float
    sale_price: Optional[float] = None
    manage_stock: bool = True
    quantity: int = 1
    in_stock: bool = True
    shipping_required: bool = True
    edition: Optional[str] = None
    notes: Optional[str] = None
    cover: Literal['hardcover', 'paperback', None] = None
    description: Optional[str] = None
    images: Set[str] = set()
    tags: Set[str] = set()
    language: Literal['bangla', 'english', None] = None
    is_used: bool = True
    condition: Literal['new', 'old_like_new',
                       'old_good_enough', 'old_readable', None] = None
    isbn: Optional[str] = None
    no_of_pages: Optional[int] = None
    slug: Optional[str] = None
    is_draft: bool = True

    # Features
    is_featured: bool = False
    is_must_read: bool = False
    is_vintage: bool = False
    is_islamic: bool = False
    is_translated: bool = False
    is_recommended: bool = False
    is_big_sale: bool = False

    # Inventory
    stock_location: Literal['mirpur_11', 'on_demand', None] = None
    shelf: Optional[str] = None
    row_col: Optional[str] = None
    bar_code: Optional[str] = None
    weight: float = 0
    cost: float = 0
    
    # Relationship

class CreateBook(BookBase):
    pass
    @model_validator(mode='after')
    def validate_model(self) -> Self:
        try:
            if self.regular_price:
                assert self.regular_price >= 0, 'regular_price cannot be negative'
            if self.sale_price:
                assert self.sale_price >= 0, 'sale_price cannot be negative'
            if self.no_of_pages:
                assert self.no_of_pages >= 0, 'no_of_pages cannot be negative'
            
            assert self.weight >= 0, 'weight cannot be negative'
            assert self.cost >= 0, 'cost cannot be negative'
            assert self.quantity >= 0, 'quantity cannot be negative' 
            
            if self.name:
                self.name = self.name.strip()
            if self.short_description:
                self.short_description = self.short_description.strip()
            if self.edition:
                self.edition = self.edition.strip()
            if self.notes:
                self.notes = self.notes.strip()
            if self.description:
                self.description = self.description.strip()
            if self.slug:
                self.slug = self.slug.strip()

        except AssertionError as err:
            raise HTTPException(status_code=400, detail=str(err))
        return self


class UpdateBook(BookBase):
    name: Optional[str] = None
    regular_price: Optional[float] = None


class ReadBook(BookBase, TimestampMixin):
    slug: str
    
    
    

    
