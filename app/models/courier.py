from sqlalchemy import String, Float, Boolean, Enum, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from typing import List

from app.models.mixins import TimestampMixin
from app.models.order import Order
from app.constant.country import Country
from app.constant.city import City

class Courier(TimestampMixin):
    __tablename__ = 'couriers'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    method_name: Mapped[str] = mapped_column(String, unique=True)
    company_name: Mapped[str]
    
    base_charge: Mapped[float]
    weight_charge_per_kg: Mapped[float]
    allow_cash_on_delivery: Mapped[bool] = mapped_column(Boolean, default=True)
    delivery_time: Mapped[str | None] 
    note: Mapped[str | None] 

    include_country: Mapped[List[Country]] = mapped_column(ARRAY(Enum(Country)), default=list)
    include_city: Mapped[List[City]] = mapped_column(ARRAY(Enum(City)), default=list)
    exclude_city: Mapped[List[City]] = mapped_column(ARRAY(Enum(City)), default=list)
    
    # Relationships
    orders: Mapped[List['Order']] = relationship(back_populates='courier')

    def __repr__(self):
        return f'<Courier (method_name={self.method_name}, base_charge={self.base_charge})>'
