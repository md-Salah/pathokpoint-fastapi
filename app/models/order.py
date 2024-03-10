from sqlalchemy import Integer, String, Float, ARRAY, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from typing import Set, List, TYPE_CHECKING

from app.constant.orderstatus import Status

from app.models.mixins import TimestampMixin
if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.models.coupon import Coupon
    from app.models.courier import Courier
from app.models.address import Address
    
class OrderItem():
    __tablename__ = 'order_items'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('books.id'), primary_key=True, nullable=False)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('orders.id'), primary_key=True, nullable=False)
    
    regular_price: Mapped[float] = mapped_column(Float, nullable=False)
    sold_price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    

    def __repr__(self):
        return f'<OrderItem (order_id={self.order_id}, book_id={self.book_id})>'


class OrderStatus():
    __tablename__ = 'order_status'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('orders.id'), nullable=False)
    
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False)
    
    note_to_customer: Mapped[str | None] = mapped_column(String)
    note_to_admin: Mapped[str | None] = mapped_column(String)
    admin_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), nullable=True)
    
    def __repr__(self):
        return f'<OrderStatus (order_id={self.order_id}, status={self.status})>'
    
class Order(TimestampMixin):
    __tablename__ = 'orders'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)

    # user
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id')) 
    
    # items/books
    # items: Mapped[List['OrderItem']] = relationship(backref='order', cascade='all, delete-orphan', lazy='joined')
    old_book_total: Mapped[float] = mapped_column(Float)
    new_book_total: Mapped[float] = mapped_column(Float)
      
    # Shipping method
    courier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('couriers.id'))
    courier: Mapped['Courier'] = relationship(back_populates='orders')
    shipping_charge: Mapped[float] = mapped_column(Float)
    weight_charge: Mapped[float] = mapped_column(Float)
    
    # Shipping Address
    address_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('addresses.id'))
    address: Mapped['Address'] = relationship(lazy='joined')
    
    # discount
    coupon_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('coupons.id'), nullable=True)
    coupons: Mapped[Set['Coupon']] = relationship(secondary='order_coupon_link', back_populates='orders') # convert to many to many
    discount: Mapped[float] = mapped_column(Float, nullable=True)
    
    # summary
    total: Mapped[float] = mapped_column(Float)
    payable: Mapped[float] = mapped_column(Float)
    paid: Mapped[float] = mapped_column(Float)
    refunded: Mapped[float] = mapped_column(Float)
    cash_on_delivery: Mapped[float] = mapped_column(Float)
    
    # payment
    transactions: Mapped[Set['Transaction']] = relationship(back_populates='order')
    
    
    def __repr__(self):
        return f'<Order id={self.id}>'

