from sqlalchemy import Boolean, ForeignKey, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from typing import List, TYPE_CHECKING

from app.models.base import Base
from app.models.mixins import TimestampMixin
from app.models.order import Order
from app.models.user import User
from app.models.book import Book
if TYPE_CHECKING:
    from app.models.image import Image


class Review(TimestampMixin):
    __tablename__ = 'reviews'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    
    product_rating: Mapped[int]
    time_rating: Mapped[int]
    delivery_rating: Mapped[int]
    website_rating: Mapped[int]
    average_rating: Mapped[float]
    comment: Mapped[str]
    
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationship
    images: Mapped[List['Image']] = relationship(secondary='review_image_link', backref='reviews', cascade='all, delete')
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='reviews')
    
    order_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('orders.id'))
    order: Mapped['Order'] = relationship(backref='review')
    
    book_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('books.id'))
    book: Mapped['Book'] = relationship(backref='reviews')

    def __repr__(self):
        return f'<Review (id={self.id})>'


review_image_link = Table(
    'review_image_link',
    Base.metadata,
    Column('review_id', UUID(as_uuid=True), ForeignKey('reviews.id', ondelete='CASCADE'), primary_key=True),
    Column('image_id', UUID(as_uuid=True), ForeignKey('images.id', ondelete='CASCADE'), primary_key=True)
)

