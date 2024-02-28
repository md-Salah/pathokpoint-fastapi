from sqlalchemy import String, ARRAY, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from typing import Set

from app.models.mixins import TimestampMixin
from app.models.book import Book


class Publisher(TimestampMixin):
    __tablename__ = 'publishers'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), index=True, unique=True, nullable=False)

    description: Mapped[str] = mapped_column(String, nullable=True)
    image: Mapped[str] = mapped_column(String, nullable=True)
    banner: Mapped[str] = mapped_column(String, nullable=True)
    
    tags: Mapped[Set[str]] = mapped_column(ARRAY(String), default=set)
    
    # Boolean featured fields
    is_islamic: Mapped[bool] = mapped_column(Boolean, default=False)
    is_english: Mapped[bool] = mapped_column(Boolean, default=False)
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False)
    
    country: Mapped[str] = mapped_column(String, nullable=True)
    book_published: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Relationship
    books: Mapped[Set['Book']] = relationship(back_populates='publisher')
    
    def __repr__(self):
        return f'<Publisher (name={self.name}, slug={self.slug})>'
