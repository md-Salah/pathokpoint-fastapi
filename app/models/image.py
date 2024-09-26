from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum, event
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.attributes import set_committed_value
import uuid
import logging
import asyncio

from app.models.mixins import TimestampMixin
from app.constant.image import ImageFolder
import app.library.s3 as s3

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
        return f'<Image (name={self.name}, folder={self.folder.value})>'


@event.listens_for(Image, 'after_delete')
def after_delete(mapper, connection, target: Image):
    loop = asyncio.get_event_loop()
    loop.create_task(after_delete_async(target))


async def after_delete_async(target: Image):
    try:
        is_success = await s3.delete_file(target.name, target.folder.value)
        logger.debug('Delete image even for "{}" is_success: {}'.format(
            target.name, is_success))
    except Exception:
        pass


@event.listens_for(Image, 'load')
def generate_url(target: Image, context):
    loop = asyncio.get_event_loop()
    loop.create_task(generate_url_async(target))


async def generate_url_async(img: Image):
    set_committed_value(img, 'src', await s3.signed_url(img.name, img.folder.value))
