from sqlalchemy import Integer, String, Float, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid

from app.models.mixins import TimestampMixin

class Book(TimestampMixin):
    __tablename__ = 'books'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    sku: Mapped[str] = mapped_column(String(15), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    banglish_name: Mapped[str] = mapped_column(String, index=True, nullable=True)
    short_description: Mapped[str] = mapped_column(String, nullable=True)
    regular_price: Mapped[float] = mapped_column(Float)
    sale_price: Mapped[float] = mapped_column(Float, nullable=True)
    manage_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    shipping_required: Mapped[bool] = mapped_column(Boolean, default=True)
    edition: Mapped[str] = mapped_column(String, nullable=True)
    notes: Mapped[str] = mapped_column(String, nullable=True)
    cover: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    images: Mapped[list[str]] = mapped_column(ARRAY(String))
    tags: Mapped[list[str]] = mapped_column(ARRAY(String))
    language: Mapped[str] = mapped_column(String, nullable=True)
    condition: Mapped[str] = mapped_column(String, nullable=True)
    isbn: Mapped[str] = mapped_column(String, nullable=True)
    no_of_pages: Mapped[int] = mapped_column(Integer, nullable=True)
    slug: Mapped[str] = mapped_column(String(100), index=True, unique=True, nullable=False)
    
    # Features
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    must_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_vintage: Mapped[bool] = mapped_column(Boolean, default=False)
    is_islamic: Mapped[bool] = mapped_column(Boolean, default=False)
    is_translated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    big_sale: Mapped[bool] = mapped_column(Boolean, default=False)

    # Stock
    stock_location: Mapped[str] = mapped_column(String, nullable=True)
    shelf: Mapped[str] = mapped_column(String, nullable=True)
    row_col: Mapped[str] = mapped_column(String, nullable=True)
    bar_code: Mapped[str] = mapped_column(String, nullable=True)
    weight: Mapped[float] = mapped_column(Float, default=0)
    selector: Mapped[str] = mapped_column(String, nullable=True)
    cost: Mapped[float] = mapped_column(Float, default=0)
    
    def __repr__(self):
        return f'<Book {self.name}>'
