import enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship

from app.config.database import Base
from app.models.mixins import Timestamp


class Order(Timestamp, Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
    user = Column(Integer, ForeignKey('users.id'))
    
    items = relationship('Book')
    