from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Sequence
from uuid import UUID
import logging

from app.models import Publisher
from app.filter_schema.publisher import PublisherFilter
from app.controller.image import attach_image, detach_images
from app.controller.exception import NotFoundException, ConflictException

logger = logging.getLogger(__name__)


async def get_publisher_by_id(id: UUID, db: AsyncSession) -> Publisher:
    publisher = await db.scalar(select(Publisher).filter(Publisher.id == id))
    if not publisher:
        raise NotFoundException('Publisher not found', str(id))
    return publisher


async def get_publisher_by_slug(slug: str, db: AsyncSession) -> Publisher:
    publisher = await db.scalar(select(Publisher).filter(Publisher.slug == slug))
    if not publisher:
        raise NotFoundException('Publisher not found')
    return publisher


async def get_all_publishers(filter: PublisherFilter, page: int, per_page: int, db: AsyncSession) -> Sequence[Publisher]:
    offset = (page - 1) * per_page

    query = select(Publisher)
    query = filter.filter(query)
    query = query.offset(offset).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


async def count_publisher(filter: PublisherFilter, db: AsyncSession) -> int:
    query = select(func.count(Publisher.id))
    query = filter.filter(query)
    result = await db.execute(query)
    return result.scalar_one()


async def create_publisher(payload: dict, db: AsyncSession) -> Publisher:
    _publisher = await db.scalar(select(Publisher).filter(or_(Publisher.name == payload['name'], Publisher.slug == payload['slug'])))
    if _publisher:
        if _publisher.name == payload['name']:
            raise ConflictException('Publisher with name {} already exists'.format(
                _publisher.name), str(_publisher.id))
        else:
            raise ConflictException('Publisher with slug {} already exists'.format(
                _publisher.slug), str(_publisher.id))

    if 'image_id' in payload:
        payload['image'] = await attach_image(payload['image_id'], None, db)
    if 'banner_id' in payload:
        payload['banner'] = await attach_image(payload['banner_id'], None, db)

    publisher = Publisher(**payload)
    db.add(publisher)
    await db.commit()

    logger.info(f'Publisher created: {publisher}')
    return publisher


async def update_publisher(id: UUID, payload: dict, db: AsyncSession) -> Publisher:
    publisher = await get_publisher_by_id(id, db)
    if payload.get('name') and publisher.name != payload['name']:
        _publisher = await db.scalar(select(Publisher).filter(Publisher.name == payload['name']))
        if _publisher:
            raise ConflictException('Publisher with name {} already exists'.format(
                _publisher.name), str(_publisher.id))
    if payload.get('slug') and publisher.slug != payload['slug']:
        _publisher = await db.scalar(select(Publisher).filter(Publisher.slug == payload['slug']))
        if _publisher:
            raise ConflictException('Publisher with slug {} already exists'.format(
                _publisher.slug), str(_publisher.id))

    if 'image_id' in payload:
        payload['image'] = await attach_image(payload['image_id'], publisher.image_id, db)
    if 'banner_id' in payload:
        payload['banner'] = await attach_image(payload['banner_id'], publisher.banner_id, db)

    [setattr(publisher, key, value) for key, value in payload.items()]
    await db.commit()

    logger.info(f'Publisher updated: {publisher}')
    return publisher


async def delete_publisher(id: UUID, db: AsyncSession) -> None:
    publisher = await get_publisher_by_id(id, db)
    await detach_images(db, publisher.image_id, publisher.banner_id)
    await db.delete(publisher)
    await db.commit()

    logger.info(f'Publisher deleted: {publisher}')
