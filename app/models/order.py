# from sqlalchemy import Integer, String, Float, ARRAY, ForeignKey
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# import uuid
# from typing import Set, List
# from enum import Enum

# # from app.models.mixins import TimestampMixin
# from app.models.base import Base
# from app.models.book import Book

# class OrderStatus(Enum):
#     PENDING = 'pending'
#     PROCESSING = 'processing'
#     SHIPPED = 'shipped'
#     DELIVERED = 'delivered'
#     CANCELLED = 'cancelled'
#     RETURNED = 'returned'
#     REFUNDED = 'refunded'
#     FAILED = 'failed'
#     COMPLETED = 'completed'
#     ARCHIVED = 'archived'
#     DELETED = 'deleted'
#     UNKNOWN = 'unknown'
    

# class Order():
#     __tablename__ = 'orders'

#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    
#     shipping_charge: Mapped[float] = mapped_column(Float, nullable=False)
#     weight_charge: Mapped[float] = mapped_column(Float, nullable=False)
#     total: Mapped[float] = mapped_column(Float, nullable=False)
#     # coupon_code: Mapped[str] = mapped_column(String, nullable=True)
#     discount: Mapped[float] = mapped_column(Float, nullable=True)
#     payable: Mapped[float] = mapped_column(Float, nullable=False)
    
#     transaction_ids: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
#     paid: Mapped[float] = mapped_column(Float, nullable=False)
#     refunded: Mapped[float] = mapped_column(Float, nullable=False)
#     due: Mapped[float] = mapped_column(Float, nullable=False)
    
    
#     # user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, foreign_key='users.id')
    
#     # shipping_method_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, foreign_key='shipping_methods.id')
#     items: Mapped[Set["Book"]] = relationship("Book", secondary='order_items', backref='orders')
#     # status: Mapped[OrderStatus] = mapped_column(OrderStatus, nullable=False)
    
    
#     def __repr__(self):
#         return f'<Order {self.id}>'


# class OrderItem():
#     __tablename__ = 'order_items'
    
#     # id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    
#     regular_price: Mapped[float] = mapped_column(Float, nullable=False)
#     sold_price: Mapped[float] = mapped_column(Float, nullable=False)
#     quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
#     book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('books.id'), primary_key=True, nullable=False)
#     order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('orders.id'), primary_key=True, nullable=False)

#     def __repr__(self):
#         return f'<OrderItem {self.book_id}>'
