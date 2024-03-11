from sqlalchemy import String, ARRAY, Column, Table, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from typing import Set

from app.models.mixins import TimestampMixin
from app.models.base import Base
from app.models.book import Book


class Category(TimestampMixin):
    __tablename__ = 'categories'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), index=True, unique=True, nullable=False)

    description: Mapped[str] = mapped_column(String, nullable=True)
    image: Mapped[str] = mapped_column(String, nullable=True)
    banner: Mapped[str] = mapped_column(String, nullable=True)
    
    tags: Mapped[Set[str]] = mapped_column(ARRAY(String), default=set)
    
    # Boolean featured fields
    is_islamic: Mapped[bool] = mapped_column(Boolean, default=False)
    is_english_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_bangla_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_job_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_comics: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationship
    books: Mapped[Set['Book']] = relationship(secondary='book_category_link', back_populates='categories')
    parent: Mapped[Set['Category']] = relationship(
        secondary='parent_child_link',
        primaryjoin='parent_child_link.c.parent_id == Category.id',
        secondaryjoin='parent_child_link.c.child_id == Category.id',
        backref='children',
    )

    def __repr__(self):
        return f'<Category (name={self.name}, slug={self.slug})>'

book_category_link = Table(
    "book_category_link",
    Base.metadata,
    Column("book_id", UUID(as_uuid=True), ForeignKey('books.id'), primary_key=True),
    Column("category_id", UUID(as_uuid=True), ForeignKey('categories.id'), primary_key=True),
)

parent_child_link = Table(
    "parent_child_link",
    Base.metadata,
    Column("parent_id", UUID(as_uuid=True), ForeignKey('categories.id'), primary_key=True),
    Column("child_id", UUID(as_uuid=True), ForeignKey('categories.id'), primary_key=True),
)