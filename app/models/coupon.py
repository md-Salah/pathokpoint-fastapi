from sqlalchemy import Integer, String, ARRAY, Date, Column, Table, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from datetime import date, datetime
from typing import Set

from app.models.mixins import TimestampMixin
from app.models.base import Base
from app.models.order import Order
from app.models.book import Book

import enum


class DiscountType(enum.Enum):
    fixed_amount = 'fixed_amount'
    percentage = 'percentage'
    flat_rate = 'flat_rate'


class Coupon(TimestampMixin):
    __tablename__ = 'coupons'

    id: Mapped[uuid.UUID] = mapped_column(UUID(
        as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String, index=True, nullable=False)
    short_description: Mapped[str | None] = mapped_column(String)
    expiry_date: Mapped[datetime | None] = mapped_column(DateTime)

    discount_type: Mapped[DiscountType] = mapped_column(Enum(DiscountType), nullable=False)
    discount_old: Mapped[float] = mapped_column(Integer, default=0)
    discount_new: Mapped[float] = mapped_column(Integer, default=0)
    max_discount_old: Mapped[float] = mapped_column(Integer, default=-1)
    max_discount_new: Mapped[float] = mapped_column(Integer, default=-1)
    min_spend_old: Mapped[float] = mapped_column(Integer, default=0)
    min_spend_new: Mapped[float] = mapped_column(Integer, default=0)

    use_limit: Mapped[int] = mapped_column(Integer, default=-1)
    use_limit_per_user: Mapped[int] = mapped_column(Integer, default=-1)
    individual_use: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    free_shipping: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    # include_books: Mapped[Set[Book]] = mapped_column(relationship())
    # include_authors: Mapped[Set[str]] = mapped_column(ARRAY(String), default=set)
    # include_categories: Mapped[Set[str]] = mapped_column(ARRAY(String), default=set)
    # include_publishers: Mapped[Set[str]] = mapped_column(ARRAY(String), default=set)
    # include_tags: Mapped[Set[str]] = mapped_column(ARRAY(String), default=set)

    # exclude_categories: Mapped[Set[str]] = mapped_column(ARRAY(String), default=set)
    # exclude_publishers: Mapped[Set[str]] = mapped_column(ARRAY(String), default=set)
    # exclude_tags: Mapped[Set[str]] = mapped_column(ARRAY(String), default=set)

    # allowed_users: Mapped[Set[str]] = mapped_column(ARRAY(String), default=set)
    
    orders: Mapped['Order'] = relationship(secondary='order_coupon_link', back_populates='coupons')

    def __repr__(self):
        return f'<Coupon (code={self.code})>'


order_coupon_link = Table(
    'order_coupon_link',
    Base.metadata,
    Column('order_id', UUID(as_uuid=True), ForeignKey('orders.id'), primary_key=True),
    Column('coupon_id', UUID(as_uuid=True), ForeignKey('coupons.id'), primary_key=True),
)