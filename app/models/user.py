from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.mixins import TimestampMixin

class User(TimestampMixin):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    first_name = Column(String(50))
    last_name = Column(String(50))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), index=True, unique=True, nullable=False)
    password = Column(String(100))
    
    phone_number = Column(String(15), index=True)
    profile_picture = Column(String(255))
    
    role = Column(String(20), default='customer')