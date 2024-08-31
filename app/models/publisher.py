from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from typing import List

from app.models.mixins import TimestampMixin
from app.models.book import Book
from app.models.image import Image
from app.constant import Country


class Publisher(TimestampMixin):
    __tablename__ = 'publishers'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, index=True, unique=True)
    slug: Mapped[str] = mapped_column(String(100), index=True, unique=True)

    description: Mapped[str | None]
    is_islamic: Mapped[bool] = mapped_column(Boolean, default=False)
    is_english: Mapped[bool] = mapped_column(Boolean, default=False)
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False)
    is_big_sale: Mapped[bool] = mapped_column(Boolean, default=False)
    is_in_menu: Mapped[bool] = mapped_column(Boolean, default=False)
    is_in_hero: Mapped[bool] = mapped_column(Boolean, default=False)
    country: Mapped[Country | None]
    book_published: Mapped[int | None]

    # Relationship
    books: Mapped[List['Book']] = relationship(back_populates='publisher')

    image_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('images.id'))
    image: Mapped['Image'] = relationship(foreign_keys=[image_id], cascade='all, delete-orphan', single_parent=True)

    banner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey('images.id'))
    banner: Mapped['Image'] = relationship(foreign_keys=[banner_id], cascade='all, delete-orphan', single_parent=True)

    def __repr__(self):
        return f'<Publisher (name={self.name}, slug={self.slug})>'
