from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column
import uuid

from app.models.mixins import TimestampMixin
from app.constant.image_folder import ImageFolder

class Image(TimestampMixin):
    __tablename__ = 'images'

    id: Mapped[uuid.UUID] = mapped_column(UUID(
        as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    name: Mapped[str]
    src: Mapped[str]
    alt: Mapped[str]
    public_id: Mapped[str]
    folder: Mapped[ImageFolder] = mapped_column(Enum(ImageFolder), default=ImageFolder.dummy)

    def __repr__(self):
        return f'<Image (name={self.name}, src={self.src})>'
