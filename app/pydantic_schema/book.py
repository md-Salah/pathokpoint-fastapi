from pydantic import UUID4, ConfigDict, Field, field_validator, PositiveInt, ValidationInfo
from typing import List

from app.pydantic_schema.mixins import NameSlugMixin, NameSlugMixinOptional, IdTimestampMixin
from app.pydantic_schema.common import AuthorOut, PublisherOut, CategoryOut, TagOut, ImageOut
from app.constant import Cover, Language, Condition, StockLocation, Country


example_book_base = {
    'public_id': 1,
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
}

example_book_base_admin = {
    **example_book_base,
    'sku': '123456',
    'stock_location': StockLocation.mirpur_11,
    'shelf': '101',
    'row_col': '1A',
    'cost': 200,
}


example_book_in = {
    **example_book_base_admin,
    'authors': ['example-uuid'],
    'translators': ['example-uuid'],
    'publisher': 'example-uuid',
    'categories': ['example-uuid'],
    'images': ['example-uuid'],
    'tags': ['example-uuid'],
}

example_book_out = {
    **example_book_base,
    **IdTimestampMixin._example,
    'authors': [AuthorOut._example],
    'translators': [AuthorOut._example],
    'publisher': PublisherOut._example,
    'categories': [CategoryOut._example],
    'images': [ImageOut._example],
}

example_book_out_admin = {
    **example_book_out,
    **example_book_base_admin,
}


_10_lakh: int = 1000000


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
    weight_in_gm: float = Field(0, ge=0, le=10000)  # 10 kg max

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


class CreateBook(BookBaseAdmin):
    publisher_id: UUID4 | None = None
    authors: List[UUID4] = []
    translators: List[UUID4] = []
    categories: List[UUID4] = []
    images: List[UUID4] = []
    tags: List[UUID4] = []

    model_config = ConfigDict(json_schema_extra={"example": example_book_in})


class UpdateBook(NameSlugMixinOptional, CreateBook):
    sku: str = Field(None, min_length=4, max_length=15)
    regular_price: float = Field(None, ge=0, le=_10_lakh)
    sale_price: float = Field(None, ge=0, le=_10_lakh)
    manage_stock: bool = Field(None)
    quantity: int = Field(None, ge=0, le=_10_lakh)
    is_used: bool = Field(None)
    condition: Condition = Field(None)


class BookOut(BookBase, IdTimestampMixin):
    authors: List[AuthorOut] = []
    translators: List[AuthorOut] = []
    categories: List[CategoryOut] = []
    publisher: PublisherOut | None = None
    images: List[ImageOut] = []
    tags: List[TagOut] = []

    public_id: PositiveInt

    model_config = ConfigDict(json_schema_extra={"example": example_book_out})


class BookOutMinimal(BookBase, IdTimestampMixin):
    authors: List[AuthorOut] = []
    images: List[ImageOut] = []


class BookOutAdmin(BookBaseAdmin, BookOut):
    model_config = ConfigDict(
        json_schema_extra={"example": example_book_out_admin})
