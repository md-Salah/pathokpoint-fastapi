import enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship

from .db_setup import Base
from .mixins import Timestamp


class Order(Timestamp, Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
    user = Column(Integer, ForeignKey('users.id'))
    
    items = relationship('Book')
    