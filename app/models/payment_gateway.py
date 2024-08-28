from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.models.mixins import TimestampMixin
from app.models import Transaction, Image


class PaymentGateway(TimestampMixin):
    __tablename__ = 'payment_gateways'

    id: Mapped[uuid.UUID] = mapped_column(UUID(
        as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(20), unique=True)
    title: Mapped[str] = mapped_column(String(20))
    is_disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin_only: Mapped[bool] = mapped_column(Boolean, default=False)

    image_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('images.id'))
    image: Mapped['Image'] = relationship(
        foreign_keys=[image_id], cascade='all, delete-orphan', single_parent=True, lazy='selectin')

    transactions: Mapped[list['Transaction']
                         ] = relationship(back_populates='gateway')

    def __repr__(self):
        return f'<PaymentGateway (name={self.name}, is_disabled={self.is_disabled})>'
