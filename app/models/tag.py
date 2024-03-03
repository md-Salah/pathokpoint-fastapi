from sqlalchemy import Integer, String, ARRAY, Date, Column, Table, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from datetime import date
from typing import Set

from app.models.mixins import TimestampMixin
from app.models.base import Base
from app.models.book import Book

class Tag(TimestampMixin):
    __tablename__ = 'tags'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), index=True, unique=True, nullable=False)
    
    private: Mapped[bool] = mapped_column(Boolean, default=False)
    
    def __repr__(self):
        return f'<Tag (name={self.name}, slug={self.slug})>'