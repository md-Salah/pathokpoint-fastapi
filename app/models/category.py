import uuid
from typing import List

from sqlalchemy import Boolean, Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.book import Book
from app.models.image import Image
from app.models.mixins import TimestampMixin


class Category(TimestampMixin):
    __tablename__ = 'categories'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, index=True, unique=True)
    slug: Mapped[str] = mapped_column(String(100), index=True, unique=True)

    description: Mapped[str | None]
    is_islamic: Mapped[bool] = mapped_column(Boolean, default=False)
    is_english_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_bangla_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_job_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_comics: Mapped[bool] = mapped_column(Boolean, default=False)
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False)
    is_big_sale: Mapped[bool] = mapped_column(Boolean, default=False)
    is_in_menu: Mapped[bool] = mapped_column(Boolean, default=False)
    is_in_hero: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationship
    books: Mapped[List['Book']] = relationship(
        secondary='book_category_link', back_populates='categories')
    parent: Mapped[List['Category']] = relationship(
        secondary='parent_child_link',
        primaryjoin='parent_child_link.c.parent_id == categories.c.id',
        secondaryjoin='parent_child_link.c.child_id == categories.c.id',
        backref='children',
    )
    image_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('images.id'))
    image: Mapped['Image'] = relationship(
        foreign_keys=[image_id], cascade='all, delete-orphan', single_parent=True)

    banner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey('images.id'))
    banner: Mapped['Image'] = relationship(
        foreign_keys=[banner_id], cascade='all, delete-orphan', single_parent=True)

    def __repr__(self):
        return f'<Category (name={self.name}, slug={self.slug})>'


book_category_link = Table(
    "book_category_link",
    Base.metadata,
    Column("book_id", UUID(as_uuid=True),
           ForeignKey('books.id'), primary_key=True),
    Column("category_id", UUID(as_uuid=True),
           ForeignKey('categories.id'), primary_key=True),
)

parent_child_link = Table(
    "parent_child_link",
    Base.metadata,
    Column("parent_id", UUID(as_uuid=True), ForeignKey(
        'categories.id'), primary_key=True),
    Column("child_id", UUID(as_uuid=True), ForeignKey(
        'categories.id'), primary_key=True),
)
