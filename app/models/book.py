import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    Float,
    ForeignKey,
    Identity,
    Integer,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constant import Condition, Country, Cover, Language, StockLocation
from app.models.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models import Author, Category, Image, Publisher, Tag


class Book(TimestampMixin):
    __tablename__ = 'books'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    public_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1), unique=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(15), unique=True)

    name: Mapped[str] = mapped_column(String(100), index=True)
    slug: Mapped[str] = mapped_column(String(100), index=True)
    short_description: Mapped[str | None]
    regular_price: Mapped[float]
    sale_price: Mapped[float]
    manage_stock: Mapped[bool]
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    pre_order: Mapped[bool] = mapped_column(Boolean, default=False)
    shipping_required: Mapped[bool] = mapped_column(Boolean, default=True)
    edition: Mapped[str | None]
    notes: Mapped[str | None]
    cover: Mapped[Cover | None] = mapped_column(Enum(Cover))
    description: Mapped[str | None]
    language: Mapped[Language | None] = mapped_column(Enum(Language))
    is_used: Mapped[bool]
    condition: Mapped[Condition] = mapped_column(Enum(Condition))
    isbn: Mapped[str | None]
    no_of_pages: Mapped[int | None] = mapped_column(Integer, default=None)
    country: Mapped[Country | None] = mapped_column(Enum(Country))
    is_draft: Mapped[bool] = mapped_column(Boolean, default=True)

    # Features
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_must_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_vintage: Mapped[bool] = mapped_column(Boolean, default=False)
    is_islamic: Mapped[bool] = mapped_column(Boolean, default=False)
    is_translated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    is_big_sale: Mapped[bool] = mapped_column(Boolean, default=False)
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False)

    # Inventory
    stock_location: Mapped[StockLocation] = mapped_column(Enum(StockLocation))
    shelf: Mapped[str | None]
    row_col: Mapped[str | None]
    bar_code: Mapped[str | None]
    weight_in_gm: Mapped[float] = mapped_column(Float, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0)

    # Relationship
    authors: Mapped[List['Author']] = relationship(
        secondary='book_author_link', back_populates='books')
    translators: Mapped[List['Author']] = relationship(
        secondary='book_translator_link', back_populates='translated_books')
    publisher_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey('publishers.id'))
    publisher: Mapped['Publisher'] = relationship(back_populates='books')
    categories: Mapped[List['Category']] = relationship(
        secondary='book_category_link', back_populates='books')
    images: Mapped[List['Image']] = relationship(
        secondary='book_image_link', cascade="all, delete-orphan", lazy="selectin", single_parent=True)
    tags: Mapped[List['Tag']] = relationship(
        secondary='book_tag_link', back_populates='books')

    def __repr__(self):
        return f'<Book (name={self.name}, slug={self.slug})>'


book_image_link = Table(
    'book_image_link',
    Base.metadata,
    Column('book_id', UUID(as_uuid=True), ForeignKey(
        'books.id', ondelete="CASCADE"), primary_key=True),
    Column('image_id', UUID(as_uuid=True), ForeignKey(
        'images.id', ondelete="CASCADE"), primary_key=True, unique=True)
)
