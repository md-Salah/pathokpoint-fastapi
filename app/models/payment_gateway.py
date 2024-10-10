import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Image, Transaction
from app.models.mixins import TimestampMixin


class PaymentGateway(TimestampMixin):
    __tablename__ = 'payment_gateways'

    id: Mapped[uuid.UUID] = mapped_column(UUID(
        as_uuid=True), primary_key=True, default=uuid.uuid4)
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
