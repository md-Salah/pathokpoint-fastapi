from sqlalchemy import Integer, Float, ForeignKey, Enum, Identity
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from typing import List, TYPE_CHECKING

from app.constant.orderstatus import Status

from app.models.mixins import TimestampMixin
if TYPE_CHECKING:
    from app.models import Courier, Coupon, Transaction
    
from app.models.book import Book
from app.models.user import User
from app.models.address import Address
from app.models.base import Base
    
class OrderItem(Base):
    __tablename__ = 'order_items'
    
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('books.id'), primary_key=True)
    book: Mapped['Book'] = relationship()
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('orders.id'), primary_key=True)
    order: Mapped['Order'] = relationship(back_populates='order_items')
    
    regular_price: Mapped[float]
    sold_price: Mapped[float]
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    def __repr__(self):
        return f'<OrderItem (book_id={self.book_id}, qty={self.quantity})>'


class OrderStatus(TimestampMixin):
    __tablename__ = 'order_status'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    
    status: Mapped[Status] = mapped_column(Enum(Status))
    note: Mapped[str | None]
    admin_note: Mapped[str | None]
    
    admin_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('users.id'))
    updated_by: Mapped['User'] = relationship()
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('orders.id'))
    order: Mapped['Order'] = relationship(back_populates='order_status')
    
    def __repr__(self):
        return f'<OrderStatus (status={self.status}, created_at={self.created_at})>'
    
class Order(TimestampMixin):
    __tablename__ = 'orders'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    invoice: Mapped[int] = mapped_column(Integer, Identity(start=1), unique=True, autoincrement=True)
    
    is_full_paid: Mapped[bool]
    order_items: Mapped[List['OrderItem']] = relationship(back_populates='order', cascade='all, delete-orphan', lazy='joined')
    new_book_total: Mapped[float]
    old_book_total: Mapped[float]
    shipping_charge: Mapped[float]
    weight_charge: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float]
    discount: Mapped[float] = mapped_column(Float, default=0.0)
    net_amount: Mapped[float]
    paid: Mapped[float]
    payment_reversed: Mapped[float] = mapped_column(Float, default=0.0)
    due: Mapped[float]
    refunded: Mapped[float] = mapped_column(Float, default=0.0)
    
    customer_note: Mapped[str | None]
    tracking_id: Mapped[str | None]
    
    # Admin only fields
    shipping_cost: Mapped[float] = mapped_column(Float, default=0.0)
    cod_receivable: Mapped[float] = mapped_column(Float, default=0.0)
    cod_received: Mapped[float] = mapped_column(Float, default=0.0)
    cost_of_good_new: Mapped[float] = mapped_column(Float, default=0.0)
    cost_of_good_old: Mapped[float] = mapped_column(Float, default=0.0)
    additional_cost: Mapped[float] = mapped_column(Float, default=0.0)
    gross_profit: Mapped[float] = mapped_column(Float, default=0.0)
     
    order_status: Mapped[List['OrderStatus']] = relationship(back_populates='order', cascade='all, delete-orphan', lazy='joined', order_by='OrderStatus.created_at')
    transactions: Mapped[List['Transaction']] = relationship(back_populates='order')
    coupon_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('coupons.id'))
    coupon: Mapped['Coupon'] = relationship(back_populates='orders', lazy='selectin')
    customer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('users.id')) 
    customer: Mapped['User'] = relationship(back_populates='orders')
    address_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('addresses.id'))
    address: Mapped['Address'] = relationship()
    courier_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('couriers.id'))
    courier: Mapped['Courier'] = relationship(back_populates='orders')
    
    def __repr__(self):
        return f'<Order (invoice={self.invoice})>'

