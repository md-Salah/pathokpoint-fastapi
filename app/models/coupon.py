from sqlalchemy import String, ARRAY, Column, Table, ForeignKey, Boolean, Enum, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING

from app.models.mixins import TimestampMixin
from app.models.base import Base
from app.models import Order, Author, Book, Publisher, Category
if TYPE_CHECKING:
    from app.models import Tag, User, Courier

from app.constant.discount_type import DiscountType
from app.constant.condition import Condition


class Coupon(TimestampMixin):
    __tablename__ = 'coupons'

    id: Mapped[uuid.UUID] = mapped_column(UUID(
        as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(20), index=True, unique=True)
    short_description: Mapped[str | None] = mapped_column(String(100))
    expiry_date: Mapped[datetime | None]

    discount_type: Mapped[DiscountType] = mapped_column(Enum(DiscountType))
    discount_old: Mapped[float | None]
    discount_new: Mapped[float | None]
    max_discount_old: Mapped[float | None]
    max_discount_new: Mapped[float | None]
    min_spend_old: Mapped[float] = mapped_column(Float, default=0)
    min_spend_new: Mapped[float] = mapped_column(Float, default=0)

    use_limit: Mapped[int | None]
    use_limit_per_user: Mapped[int | None]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    max_shipping_charge: Mapped[float | None]

    include_conditions: Mapped[List[Condition]] = mapped_column(
        ARRAY(Enum(Condition)), default=list)

    # Relationships
    include_books: Mapped[List['Book']] = relationship(
        secondary='coupon_book_include_link', backref='coupons')
    include_authors: Mapped[List['Author']] = relationship(
        secondary='coupon_author_include_link', backref='coupons')
    include_categories: Mapped[List['Category']] = relationship(
        secondary='coupon_category_include_link', backref='coupons')
    include_publishers: Mapped[List['Publisher']] = relationship(
        secondary='coupon_publisher_include_link', backref='coupons')
    include_tags: Mapped[List['Tag']] = relationship(
        secondary='coupon_tag_include_link', backref='coupons')

    exclude_books: Mapped[List['Book']] = relationship(
        secondary='coupon_book_exclude_link')
    exclude_authors: Mapped[List['Author']] = relationship(
        secondary='coupon_author_exclude_link')
    exclude_categories: Mapped[List['Category']] = relationship(
        secondary='coupon_category_exclude_link')
    exclude_publishers: Mapped[List['Publisher']] = relationship(
        secondary='coupon_publisher_exclude_link')
    exclude_tags: Mapped[List['Tag']] = relationship(
        secondary='coupon_tag_exclude_link')

    allowed_users: Mapped[List['User']] = relationship(
        secondary='coupon_user_link')
    exclude_couriers: Mapped[List['Courier']] = relationship(
        secondary='coupon_courier_exclude_link')

    orders: Mapped[List['Order']] = relationship(back_populates='coupon')

    def __repr__(self):
        return f'<Coupon (code={self.code}, is_active={self.is_active})>'


coupon_book_include_link = Table(
    'coupon_book_include_link',
    Base.metadata,
    Column('coupon_id', UUID(as_uuid=True),
           ForeignKey('coupons.id'), primary_key=True),
    Column('book_id', UUID(as_uuid=True),
           ForeignKey('books.id'), primary_key=True),
)
coupon_book_exclude_link = Table(
    'coupon_book_exclude_link',
    Base.metadata,
    Column('coupon_id', UUID(as_uuid=True),
           ForeignKey('coupons.id'), primary_key=True),
    Column('book_id', UUID(as_uuid=True),
           ForeignKey('books.id'), primary_key=True),
)

coupon_author_include_link = Table(
    'coupon_author_include_link',
    Base.metadata,
    Column('coupon_id', UUID(as_uuid=True),
           ForeignKey('coupons.id'), primary_key=True),
    Column('author_id', UUID(as_uuid=True),
           ForeignKey('authors.id'), primary_key=True),
)
coupon_author_exclude_link = Table(
    'coupon_author_exclude_link',
    Base.metadata,
    Column('coupon_id', UUID(as_uuid=True),
           ForeignKey('coupons.id'), primary_key=True),
    Column('author_id', UUID(as_uuid=True),
           ForeignKey('authors.id'), primary_key=True),
)

coupon_category_include_link = Table(
    'coupon_category_include_link',
    Base.metadata,
    Column('coupon_id', UUID(as_uuid=True),
           ForeignKey('coupons.id'), primary_key=True),
    Column('category_id', UUID(as_uuid=True),
           ForeignKey('categories.id'), primary_key=True),
)

coupon_category_exclude_link = Table(
    'coupon_category_exclude_link',
    Base.metadata,
    Column('coupon_id', UUID(as_uuid=True),
           ForeignKey('coupons.id'), primary_key=True),
    Column('category_id', UUID(as_uuid=True),
           ForeignKey('categories.id'), primary_key=True),
)

coupon_publisher_include_link = Table(
    'coupon_publisher_include_link',
    Base.metadata,
    Column('coupon_id', UUID(as_uuid=True),
           ForeignKey('coupons.id'), primary_key=True),
    Column('publisher_id', UUID(as_uuid=True),
           ForeignKey('publishers.id'), primary_key=True),
)

coupon_publisher_exclude_link = Table(
    'coupon_publisher_exclude_link',
    Base.metadata,
    Column('coupon_id', UUID(as_uuid=True),
           ForeignKey('coupons.id'), primary_key=True),
    Column('publisher_id', UUID(as_uuid=True),
           ForeignKey('publishers.id'), primary_key=True),
)

coupon_tag_include_link = Table(
    'coupon_tag_include_link',
    Base.metadata,
    Column('coupon_id', UUID(as_uuid=True),
           ForeignKey('coupons.id'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True),
           ForeignKey('tags.id'), primary_key=True),
)

coupon_tag_exclude_link = Table(
    'coupon_tag_exclude_link',
    Base.metadata,
    Column('coupon_id', UUID(as_uuid=True),
           ForeignKey('coupons.id'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True),
           ForeignKey('tags.id'), primary_key=True),
)

coupon_user_link = Table(
    'coupon_user_link',
    Base.metadata,
    Column('coupon_id', UUID(as_uuid=True),
           ForeignKey('coupons.id'), primary_key=True),
    Column('user_id', UUID(as_uuid=True),
           ForeignKey('users.id'), primary_key=True),
)

coupon_courier_exclude_link = Table(
    'coupon_courier_exclude_link',
    Base.metadata,
    Column('coupon_id', UUID(as_uuid=True),
           ForeignKey('coupons.id'), primary_key=True),
    Column('courier_id', UUID(as_uuid=True),
           ForeignKey('couriers.id'), primary_key=True),
)
