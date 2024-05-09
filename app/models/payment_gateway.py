from sqlalchemy import String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.models.mixins import TimestampMixin
from app.models import Transaction

class PaymentGateway(TimestampMixin):
    __tablename__ = 'payment_gateways'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str | None] = mapped_column(String(100))
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
        
    transactions: Mapped[list['Transaction']] = relationship(back_populates='gateway')
        
    def __repr__(self):
        return f'<PaymentGateway (name={self.name}, is_enabled={self.is_enabled})>'
    