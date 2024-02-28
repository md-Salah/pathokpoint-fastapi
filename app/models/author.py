from sqlalchemy import Integer, String, ARRAY, Date, Column, Table, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from datetime import date
from typing import Set

from app.models.mixins import TimestampMixin, Base
from app.models.book import Book


class Author(TimestampMixin):
    __tablename__ = 'authors'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), index=True, unique=True, nullable=False)

    description: Mapped[str] = mapped_column(String, nullable=True)
    image: Mapped[str] = mapped_column(String, nullable=True)
    banner: Mapped[str] = mapped_column(String, nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=True)
    death_date: Mapped[date] = mapped_column(Date, nullable=True)
    book_published: Mapped[int] = mapped_column(Integer, nullable=True)
    
    tags: Mapped[Set[str]] = mapped_column(ARRAY(String), default=set)
    
    city: Mapped[str] = mapped_column(String, nullable=True)
    country: Mapped[str] = mapped_column(String, nullable=True)
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationship
    books: Mapped[Set['Book']] = relationship(secondary='book_author_link', back_populates='authors')
    
    def __repr__(self):
        return f'<Author (name={self.name}, slug={self.slug})>'
    


book_author_link = Table(
    "book_author_link",
    Base.metadata,
    Column("book_id", UUID(as_uuid=True), ForeignKey('books.id'), primary_key=True),
    Column("author_id", UUID(as_uuid=True), ForeignKey('authors.id'), primary_key=True),
)


