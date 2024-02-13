from app.config.database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

class Book(Base):
    __tablename__ = 'books'

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    sku = Column(String, unique=True)
    name = Column(String, index=True)
    banglish_name = Column(String, index=True)
    short_description = Column(String)
    regular_price = Column(Float)
    sale_price = Column(Float)
    manage_stock = Column(Boolean, default=True)
    quantity = Column(Integer, default=1)
    in_stock = Column(Boolean, default=True)
    shipping_required = Column(Boolean, default=True)
    edition = Column(String)
    notes = Column(String)
    cover = Column(String)
    description = Column(String)
    images = Column(ARRAY(String))
    tags = Column(ARRAY(String))
    language = Column(String)
    condition = Column(String)
    isbn = Column(String)
    no_of_pages = Column(Integer)
    slug = Column(String, index=True, unique=True, nullable=False)

    # Features
    featured = Column(Boolean, default=False)
    must_read = Column(Boolean, default=False)
    is_vintage = Column(Boolean, default=False)
    is_islamic = Column(Boolean, default=False)
    is_translated = Column(Boolean, default=False)
    is_recommended = Column(Boolean, default=False)
    big_sale = Column(Boolean, default=False)

    # Stock
    stock_location = Column(String)
    shelf = Column(String)
    row_col = Column(String)
    bar_code = Column(String)
    weight = Column(Float, default=0)
    selector = Column(String)
    cost = Column(Float, default=0)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
