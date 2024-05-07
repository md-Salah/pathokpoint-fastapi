from sqlalchemy import String, Enum, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import date
from typing import TYPE_CHECKING

from app.constant.role import Role
from app.constant.gender import Gender
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models import Order, Address, Review

class User(TimestampMixin):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    
    first_name: Mapped[str | None] = mapped_column(String(20))
    last_name: Mapped[str | None] = mapped_column(String(20))
    username: Mapped[str] = mapped_column(String(25), unique=True)
    email: Mapped[str] = mapped_column(String, index=True, unique=True)
    password: Mapped[str]
    phone_number: Mapped[str | None] 
    image: Mapped[str | None]
    date_of_birth: Mapped[date | None]
    gender: Mapped[Gender | None]
    
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.customer)
    
    
    orders: Mapped[list["Order"]] = relationship(back_populates='customer')
    addresses: Mapped[list["Address"]] = relationship(back_populates='user', cascade='all, delete-orphan')
    reviews: Mapped[list["Review"]] = relationship(back_populates='user')
    
    def __repr__(self):
        return f'<User (username={self.username}, role={self.role})>'
    
    