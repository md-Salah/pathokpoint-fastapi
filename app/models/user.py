from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.mixins import TimestampMixin
# from app.models.order import Order

class User(TimestampMixin):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), index=True, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    
    phone_number: Mapped[str] = mapped_column(String(15), nullable=True) 
    profile_picture: Mapped[str] = mapped_column(String(255), nullable=True)   
    
    role: Mapped[str] = mapped_column(String(20), default='customer')
    
    # orders: Mapped[list["Order"]] = relationship(back_populates='user')
    
    def __repr__(self):
        return f'<User (username={self.username})>'
    
    