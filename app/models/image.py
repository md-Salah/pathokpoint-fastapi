from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid

from app.models.mixins import TimestampMixin


class Image(TimestampMixin):
    __tablename__ = 'images'

    id: Mapped[uuid.UUID] = mapped_column(UUID(
        as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    name: Mapped[str]
    src: Mapped[str]
    alt: Mapped[str]

    def __repr__(self):
        return f'<Image (name={self.name})>'
