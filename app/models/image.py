from sqlalchemy import String, ForeignKey, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from typing import List

from app.models.mixins import TimestampMixin
from app.models.base import Base
from app.models.book import Book


class Image(TimestampMixin):
    __tablename__ = 'images'

    id: Mapped[uuid.UUID] = mapped_column(UUID(
        as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    src: Mapped[str] = mapped_column(String)
    alt: Mapped[str] = mapped_column(String(100))
    
    books: Mapped[List['Book']] = relationship(secondary='book_image_link', back_populates='images')

    def __repr__(self):
        return f'<Image (name={self.name})>'


book_image_link = Table(
    'book_image_link',
    Base.metadata,
    Column('book_id', UUID(as_uuid=True), ForeignKey('books.id'), primary_key=True),
    Column('image_id', UUID(as_uuid=True), ForeignKey('images.id'), primary_key=True)
)