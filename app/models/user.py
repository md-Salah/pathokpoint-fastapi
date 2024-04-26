from sqlalchemy import String, Enum, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from typing import TYPE_CHECKING

from app.constant.role import Role
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models import Order, Address

class User(TimestampMixin):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(100), index=True, unique=True)
    password: Mapped[str] = mapped_column(String)
    
    phone_number: Mapped[str | None] = mapped_column(String(14)) 
    image: Mapped[str | None] = mapped_column(String)   
    
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.customer)
    
    
    orders: Mapped[list["Order"]] = relationship(back_populates='customer')
    addresses: Mapped[list["Address"]] = relationship(back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User (username={self.username}, email={self.email})>'
    
    