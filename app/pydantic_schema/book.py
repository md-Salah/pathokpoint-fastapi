from pydantic import UUID4, ConfigDict, Field, field_validator, PositiveInt, ValidationInfo
from typing import List

from app.pydantic_schema.mixins import NameSlugMixin, NameSlugMixinOptional, IdTimestampMixin, id_timestamp_mixin_example

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

class BookBase(NameSlugMixin):
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
    
    model_config = ConfigDict(json_schema_extra={"example": example_book})
    
    @field_validator('sale_price')
    @classmethod
    def validate_sale_price(cls, v: float, info: ValidationInfo):
        if v > info.data['regular_price']:
            raise ValueError('Sale price cannot be greater than regular price')
        return v
    
    @field_validator('condition')
    @classmethod
    def validate_condition(cls, v: Condition, info: ValidationInfo):
        if info.data['is_used'] is True and v == Condition.new:
            raise ValueError('Condition cannot be new when is_used is True')
        return v
    
class BookBaseAdmin(BookBase):
    sku: str = Field(min_length=4, max_length=15)
    stock_location: StockLocation = StockLocation.mirpur_11
    shelf: str | None = Field(None, min_length=2, max_length=20)
    row_col: str | None = Field(None, min_length=2, max_length=20)
    cost: float = Field(0, ge=0, le=_10_lakh) 
    sold_count: int = 0

    model_config = ConfigDict(json_schema_extra={"example": example_book_admin})

class CreateBook(BookBaseAdmin):
    authors: List[UUID4] = []
    translators: List[UUID4] = []
    categories: List[UUID4] = []
    publisher: UUID4 | None = None
    images: List[UUID4] = []
    tags: List[UUID4] = []

class UpdateBook(NameSlugMixinOptional, CreateBook):
    sku: str = Field(None, min_length=4, max_length=15)
    regular_price: float = Field(None, ge=0, le=_10_lakh)
    sale_price: float = Field(None, ge=0, le=_10_lakh)
    manage_stock: bool = Field(None)
    quantity: int = Field(None, ge=0, le=_10_lakh)
    is_used: bool = Field(None)
    condition: Condition = Field(None)
    stock_location: StockLocation = Field(None)


class BookOut(BookBase, IdTimestampMixin):
    authors: List[AuthorOut] = []
    translators: List[AuthorOut] = []
    categories: List[CategoryOut] = []
    publisher: PublisherOut | None = None
    images: List[ImageOut] = []
    tags: List[TagOut] = []
    
    serial_number: PositiveInt
    
    model_config = ConfigDict(json_schema_extra={"example": example_book | id_timestamp_mixin_example})
        
class BookOutAdmin(BookOut, BookBaseAdmin):
    model_config = ConfigDict(json_schema_extra={"example": example_book_admin | id_timestamp_mixin_example})
