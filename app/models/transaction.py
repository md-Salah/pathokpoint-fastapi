from sqlalchemy import String, Boolean, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.models.mixins import TimestampMixin
from app.models.order import Order

class Transaction(TimestampMixin):
    __tablename__ = 'transactions'

    id: Mapped[uuid.UUID] = mapped_column(UUID(
        as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)

    gateway: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)
    transaction_id: Mapped[str] = mapped_column(String)
    account_number: Mapped[str] = mapped_column(String)
    reference: Mapped[str | None] = mapped_column(String)

    incomming: Mapped[bool] = mapped_column(Boolean, default=True)
    manual: Mapped[bool] = mapped_column(Boolean, default=False)

    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('orders.id'))
    order: Mapped['Order'] = relationship(back_populates='transactions')
    