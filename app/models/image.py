import asyncio
import logging
import uuid

from sqlalchemy import String, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.attributes import set_committed_value

import app.library.s3 as s3
from app.constant.image import ImageFolder
from app.models.mixins import TimestampMixin

logger = logging.getLogger(__name__)


class Image(TimestampMixin):
    __tablename__ = 'images'

    id: Mapped[uuid.UUID] = mapped_column(UUID(
        as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    src: Mapped[str] = mapped_column(String, default='')    
    folder: Mapped[ImageFolder] = mapped_column(
        String, default=ImageFolder.dummy)

    def __repr__(self):
        return f'<Image (filename={self.name})>'


@event.listens_for(Image, 'after_delete')
def after_delete(mapper, connection, target: Image):
    loop = asyncio.get_event_loop()
    loop.create_task(after_delete_async(target))


async def after_delete_async(target: Image):
    try:
        is_success = await s3.delete_file(target.name, target.folder)
        logger.debug('Delete image event for "{}" is_success: {}'.format(
            target.name, is_success))
    except Exception:
        pass


@event.listens_for(Image, 'load')
def generate_url(target: Image, context):
    set_committed_value(target, 'src', s3.public_url(
        target.name, target.folder))
