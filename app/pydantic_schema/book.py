from pydantic import UUID4, ConfigDict, Field
from typing import List

from app.pydantic_schema.mixins import TimestampMixin, timestamp_mixin_example
from app.pydantic_schema.base import BaseModel

from app.constant import Cover, Language, Condition, StockLocation, Country
from app.pydantic_schema.author import AuthorOut
from app.pydantic_schema.category import CategoryOut
from app.pydantic_schema.publisher import PublisherOut
from app.pydantic_schema.image import ImageOut
from app.pydantic_schema.tag import TagOut

    
example_book = {
    'serial_number': 1,
    'name': 'The God of Small Things',
    'slug': 'the-god-of-small-things',
    'short_description': "Novel by Arundhati Roy, published in 1997, which won the Booker Prize in 1997.",
    'regular_price': 300,
    'sale_price': 80,
    'manage_stock': True,
    'quantity': 10,
    'in_stock': True,
    'pre_order': False, 
    'shipping_required': True,
    'edition': '1st edition, 1997',
    'notes': 'This is a special edition with a special cover',
    'cover': Cover.hardcover,
    'description': "The God of Small Things is the debut novel of Indian writer Arundhati Roy. It is a story about the childhood experiences of fraternal twins whose lives are destroyed by the Love Laws that lay down who should be loved, and how. And how much.",
    'language': Language.english,
    'is_used': True,
    'condition': Condition.old_like_new,
    'isbn': '9780679457312',
    'no_of_pages': 333,
    'is_draft': False,
    'country': Country.BD,
    
    'is_featured': True,
    'is_must_read': True,
    'is_vintage': True,
    'is_islamic': False,
    'is_translated': False,
    'is_recommended': True,
    'is_big_sale': False,
    
    'bar_code': '123456',
    'weight_in_gm': 540,
    
    'authors': [],
    'translators': [],
    'publisher': '11a132d7-6758-4603-8c32-668485ae8a6b',  
    'categories': [],
    'images': [],
    'tags': [],
}

example_book_admin = {
    **example_book,
    'sku': '123456',
    'stock_location': StockLocation.mirpur_11,
    'shelf': '101',
    'row_col': '1A',
    'cost': 200,     
}

_10_lakh = 1000000

class BookBase(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": example_book})
    
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=100, pattern=r'^[a-z0-9-]+$')
    short_description: str | None = Field(None, min_length=10, max_length=1000)
    regular_price: float = Field(ge=0, le=_10_lakh)
    sale_price: float = Field(ge=0, le=_10_lakh)
    manage_stock: bool 
    quantity: int = Field(0, ge=0, le=_10_lakh)
    in_stock: bool = True
    pre_order: bool = False
    shipping_required: bool = True
    edition: str | None = Field(None, min_length=2, max_length=100)
    notes: str | None = Field(None, min_length=2, max_length=1000)
    cover: Cover | None = None
    description: str | None = Field(None, min_length=10, max_length=10000)
    language: Language | None = None
    is_used: bool 
    condition: Condition 
    isbn: str | None = Field(None, min_length=10, max_length=13)
    no_of_pages: int | None = Field(None, ge=0, le=10000)
    country: Country | None = None
    is_draft: bool = True

    # Features
    is_featured: bool = False
    is_must_read: bool = False
    is_vintage: bool = False
    is_islamic: bool = False
    is_translated: bool = False
    is_recommended: bool = False
    is_big_sale: bool = False
    is_popular: bool = False
    
    bar_code: str | None = Field(None, min_length=4, max_length=20)
    weight_in_gm: float = Field(0, ge=0, le=10000) # 10 kg max
    
    
class BookBaseAdmin(BookBase):
    model_config = ConfigDict(json_schema_extra={"example": example_book_admin})
    
    sku: str = Field(min_length=4, max_length=15)
    stock_location: StockLocation = StockLocation.mirpur_11
    shelf: str | None = Field(None, min_length=2, max_length=20)
    row_col: str | None = Field(None, min_length=2, max_length=20)
    cost: float = Field(0, ge=0, le=_10_lakh) 


class CreateBook(BookBaseAdmin):
    authors: List[UUID4] = []
    translators: List[UUID4] = []
    categories: List[UUID4] = []
    publisher: UUID4 | None = None
    images: List[UUID4] = []
    tags: List[UUID4] = []

class UpdateBook(CreateBook):
    sku: str | None = Field(None, min_length=4, max_length=15)
    name: str | None = Field(None, min_length=2, max_length=100)
    slug: str | None = Field(None, min_length=2, max_length=100, pattern=r'^[a-z0-9-]+$')
    regular_price: float | None = Field(None, ge=0, le=_10_lakh)
    sale_price: float | None = Field(None, ge=0, le=_10_lakh)
    manage_stock: bool | None = None
    quantity: int | None = Field(None, ge=0, le=_10_lakh)
    is_used: bool | None = None
    condition: Condition | None = None
    stock_location: StockLocation | None = None


class BookOut(BookBase, TimestampMixin):
    model_config = ConfigDict(json_schema_extra={"example": example_book | timestamp_mixin_example})
        
    authors: List[AuthorOut] = []
    translators: List[AuthorOut] = []
    categories: List[CategoryOut] = []
    publisher: PublisherOut | None = None
    images: List[ImageOut] = []
    tags: List[TagOut] = []
    
    serial_number: int
    
        
class BookOutAdmin(BookOut, BookBaseAdmin):
    model_config = ConfigDict(json_schema_extra={"example": example_book_admin | timestamp_mixin_example})
