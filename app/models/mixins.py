from datetime import datetime
from sqlalchemy import Column, DateTime
from app.config.database import Base

class TimestampMixin(Base):
    __abstract__ = True
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
    