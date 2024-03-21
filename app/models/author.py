from sqlalchemy import Integer, String, Column, Table, ForeignKey, Boolean, Identity
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from datetime import date
from typing import List

from app.models.mixins import TimestampMixin
from app.models.base import Base
from app.models.book import Book
from app.models.image import Image
from app.constant import Country


class Author(TimestampMixin):
    __tablename__ = 'authors'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    serial_number: Mapped[int] = mapped_column(Integer, Identity(start=1), unique=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, index=True)
    slug: Mapped[str] = mapped_column(String(100), index=True)

    description: Mapped[str | None]
    birth_date: Mapped[date | None]
    death_date: Mapped[date | None]
    book_published: Mapped[int | None] = mapped_column(Integer, default=0)

    city: Mapped[str | None]
    country: Mapped[Country | None]
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationship
    books: Mapped[List['Book']] = relationship(
        secondary='book_author_link', back_populates='authors')
    translated_books: Mapped[List['Book']] = relationship(
        secondary='book_translator_link', back_populates='translators')

    image_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('images.id'))
    image: Mapped['Image'] = relationship(foreign_keys=[image_id])

    banner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey('images.id'))
    banner: Mapped['Image'] = relationship(foreign_keys=[banner_id])

    def __repr__(self):
        return f'<Author (name={self.name}, slug={self.slug})>'


book_author_link = Table(
    "book_author_link",
    Base.metadata,
    Column("book_id", UUID(as_uuid=True),
           ForeignKey('books.id'), primary_key=True),
    Column("author_id", UUID(as_uuid=True),
           ForeignKey('authors.id'), primary_key=True),
)

book_translator_link = Table(
    "book_translator_link",
    Base.metadata,
    Column("book_id", UUID(as_uuid=True),
           ForeignKey('books.id'), primary_key=True),
    Column("translator_id", UUID(as_uuid=True),
           ForeignKey('authors.id'), primary_key=True),
)
