import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models import Order, PaymentGateway, User


class Transaction(TimestampMixin):
    __tablename__ = 'transactions'

    id: Mapped[uuid.UUID] = mapped_column(UUID(
        as_uuid=True), primary_key=True, default=uuid.uuid4)

    amount: Mapped[float]
    transaction_id: Mapped[str] = mapped_column(String, unique=True)
    reference: Mapped[str | None]
    account_number: Mapped[str]
    is_manual: Mapped[bool]

    is_refund: Mapped[bool] = mapped_column(Boolean, default=False)
    refund_reason: Mapped[str | None]

    # Relationships
    refunded_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey('users.id'))
    refunded_by: Mapped['User'] = relationship(foreign_keys=[refunded_by_id])

    gateway_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('payment_gateways.id'))
    gateway: Mapped['PaymentGateway'] = relationship(
        back_populates='transactions')

    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('orders.id'))
    order: Mapped['Order'] = relationship(back_populates='transactions')

    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey('users.id'))
    customer: Mapped['User'] = relationship(
        backref='transactions', foreign_keys=[customer_id])

    def __repr__(self) -> str:
        return f'<Transaction (Tnx_id={self.transaction_id}, amount={self.amount})>'
