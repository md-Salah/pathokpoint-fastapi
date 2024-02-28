from sqlalchemy import String, Float, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from typing import Set

from app.models.mixins import TimestampMixin


class ShippingMethod(TimestampMixin):
    __tablename__ = 'shipping_methods'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    
    base_charge: Mapped[float] = mapped_column(Float, nullable=False)
    weight_charge_per_kg: Mapped[float] = mapped_column(Float, nullable=False)
    
    include_countries: Mapped[Set[str]] = mapped_column(ARRAY(String), nullable=True, default=set)
    include_districts: Mapped[Set[str]] = mapped_column(ARRAY(String), nullable=True, default=set)
    exclude_districts: Mapped[Set[str]] = mapped_column(ARRAY(String), nullable=True, default=set)
    
    def __repr__(self):
        return f'<ShippingMethod {self.name}>'