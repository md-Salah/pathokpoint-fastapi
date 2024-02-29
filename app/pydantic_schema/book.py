from pydantic import NonNegativeFloat, NonNegativeInt, UUID4, ConfigDict
from enum import Enum
from typing import Set

from app.pydantic_schema.mixins import TimestampMixin, timestamp_mixin_example
from app.pydantic_schema.base import BaseModel

class Cover(Enum):
    hardcover = 'hardcover'
    paperback = 'paperback'
    
class Language(Enum):
    bangla = 'bangla'
    english = 'english'
    other = 'other'
    
class Condition(Enum):
    new = 'new'
    old_like_new = 'old_like_new'
    old_good_enough = 'old_good_enough'
    old_readable = 'old_readable'

class StockLocation(Enum):
    mirpur_11 = 'mirpur_11'
    on_demand = 'on_demand'
    
example_book = {
    'sku': '123456',
    'name': 'The God of Small Things',
    'short_description': "Novel by Arundhati Roy, published in 1997, which won the Booker Prize in 1997.",
    'regular_price': 300,
    'sale_price': 80,
    'manage_stock': True,
    'quantity': 10,
    'in_stock': True,
    'shipping_required': True,
    'edition': '1st edition, 1997',
    'notes': 'This is a special edition with a special cover',
    'cover': 'hardcover',
    'description': "The God of Small Things is the debut novel of Indian writer Arundhati Roy. It is a story about the childhood experiences of fraternal twins whose lives are destroyed by the Love Laws that lay down who should be loved, and how. And how much.",
    'images': ['https://example.com/image1.jpg', 'https://example.com/image2.jpg'],
    'tags': [],
    'language': 'english',
    'is_used': True,
    'condition': 'old_like_new',
    'isbn': '9780679457312',
    'no_of_pages': 333,
    'slug': 'the-god-of-small-things',
    'is_draft': False,
    'is_featured': True,
    'is_must_read': True,
    'is_vintage': True,
    'is_islamic': False,
    'is_translated': False,
    'is_recommended': True,
    'is_big_sale': False,
    
    'stock_location': 'mirpur_11',
    'shelf': 'A',
    'row_col': '1A',
    'bar_code': '123456',
    'weight': 540,
    'cost': 200,
}

class BookBase(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": example_book})
    
    sku: str | None = None
    name: str
    short_description: str | None = None
    regular_price: NonNegativeFloat
    sale_price: NonNegativeFloat | None = None
    manage_stock: bool = True
    quantity: NonNegativeInt = 1
    in_stock: bool = True
    shipping_required: bool = True
    edition: str | None = None
    notes: str | None = None
    cover: Cover | None = None
    description: str | None = None
    images: Set[str] = set()
    tags: Set[str] = set()
    language: Language | None = None
    is_used: bool = True
    condition: Condition | None = None
    isbn: str | None = None
    no_of_pages: NonNegativeInt | None = None
    slug: str | None = None
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
    stock_location: StockLocation | None = None
    shelf: str | None = None
    row_col: str | None = None
    bar_code: str | None = None
    weight: NonNegativeFloat = 0
    cost: NonNegativeFloat = 0

class CreateBook(BookBase):
    # authors: Set[UUID4] = set() # 11a132d7-6758-4603-8c32-668485ae8a6b
    # translators: Set[UUID4] = set()
    # categories: Set[UUID4] = set()
    # publisher: UUID4 | None = None
    pass

class UpdateBook(CreateBook):
    name: str | None = None
    regular_price: float | None = None

class ReadBook(BookBase, TimestampMixin):
    slug: str
    
    # authors: Set[UUID4]
    
    model_config = ConfigDict(json_schema_extra={"example": example_book | timestamp_mixin_example})
    
    
    

    
