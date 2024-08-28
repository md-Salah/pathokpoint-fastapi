from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum, event
from sqlalchemy.orm import Mapped, mapped_column
import uuid
import logging

from app.models.mixins import TimestampMixin
from app.constant.image import ImageFolder
from app.library.cloudinary import delete_file_from_cloudinary_sync

logger = logging.getLogger(__name__)


class Image(TimestampMixin):
    __tablename__ = 'images'

    id: Mapped[uuid.UUID] = mapped_column(UUID(
        as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    name: Mapped[str]
    src: Mapped[str]
    public_id: Mapped[str]
    folder: Mapped[ImageFolder] = mapped_column(
        Enum(ImageFolder), default=ImageFolder.dummy)

    def __repr__(self):
        return f'<Image (name={self.name}, src={self.src})>'


@event.listens_for(Image, 'after_delete')
def after_delete(mapper, connection, target: Image):
    if target.public_id:
        is_success = delete_file_from_cloudinary_sync(target.public_id)
        logger.debug(f'Image deletion event success: {is_success}')

