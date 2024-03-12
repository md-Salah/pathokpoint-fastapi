from sqlalchemy import String, Boolean, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from typing import TYPE_CHECKING

from app.models.mixins import TimestampMixin
if TYPE_CHECKING:
    from app.models import User, PaymentGateway, Order

class Transaction(TimestampMixin):
    __tablename__ = 'transactions'

    id: Mapped[uuid.UUID] = mapped_column(UUID(
        as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)

    amount: Mapped[float] = mapped_column(Float)
    transaction_id: Mapped[str] = mapped_column(String, unique=True)
    reference: Mapped[str | None] = mapped_column(String)
    account_number: Mapped[str] = mapped_column(String)
    is_manual: Mapped[bool] = mapped_column(Boolean)

    is_refund: Mapped[bool] = mapped_column(Boolean, default=False)
    refund_reason: Mapped[str | None] = mapped_column(String)

    # Relationships
    refunded_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey('users.id'))
    refunded_by: Mapped['User'] = relationship()

    gateway_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('payment_gateways.id'))
    gateway: Mapped['PaymentGateway'] = relationship(
        back_populates='transactions')

    order_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('orders.id'))
    order: Mapped['Order'] = relationship(back_populates='transactions')
