from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from datetime import datetime

from app.models.mixins import TimestampMixin


class Setting(TimestampMixin):
    __tablename__ = 'settings'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String, index=True, unique=True)
    value: Mapped[str]
    description: Mapped[str | None]
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True))

    def __repr__(self):
        return f'<Setting (name={self.key}, slug={self.value})>'
