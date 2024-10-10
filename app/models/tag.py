import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.book import Book
from app.models.mixins import TimestampMixin


class Tag(TimestampMixin):
    __tablename__ = 'tags'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), index=True)
    slug: Mapped[str] = mapped_column(String(100), index=True)
    private: Mapped[bool] = mapped_column(Boolean, default=False)
    is_in_menu: Mapped[bool] = mapped_column(Boolean, default=False)
    is_in_hero: Mapped[bool] = mapped_column(Boolean, default=False)

    books: Mapped[list['Book']] = relationship(
        secondary='book_tag_link', back_populates='tags')

    def __repr__(self):
        return f'<Tag (name={self.name}, slug={self.slug})>'


book_tag_link = Table(
    'book_tag_link',
    Base.metadata,
    Column('book_id', UUID(as_uuid=True),
           ForeignKey('books.id'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True),
           ForeignKey('tags.id'), primary_key=True),
)
