from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Sequence
from uuid import UUID
import logging

from app.models.tag import Tag
from app.filter_schema.tag import TagFilter
from app.controller.exception import NotFoundException, ConflictException

logger = logging.getLogger(__name__)


async def get_tag_by_id(id: UUID, db: AsyncSession) -> Tag:
    tag = await db.get(Tag, id)
    if not tag:
        raise NotFoundException('Tag not found', str(id))
    return tag


async def get_all_tags(filter: TagFilter, page: int, per_page: int, db: AsyncSession) -> Sequence[Tag]:
    offset = (page - 1) * per_page
    query = select(Tag)
    query = filter.filter(query)
    query = query.offset(offset).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


async def count_tag(filter: TagFilter, db: AsyncSession) -> int:
    query = select(func.count(Tag.id))
    query = filter.filter(query)
    result = await db.execute(query)
    return result.scalar_one()


async def create_tag(payload: dict, db: AsyncSession) -> Tag:
    _tag = await db.scalar(select(Tag).where(or_(Tag.name == payload['name'], Tag.slug == payload['slug'])))
    if _tag:
        if _tag.name == payload['name']:
            raise ConflictException('Tag with name ({}) already exists'.format(
                _tag.name), str(_tag.id))
        else:
            raise ConflictException('Tag with slug ({}) already exists'.format(
                _tag.slug), str(_tag.id))

    logger.debug(f'Creating tag with payload: {payload}')
    tag = Tag(**payload)
    db.add(tag)
    await db.commit()
    logger.info(f'Tag created {tag}')
    return tag


async def update_tag(id: UUID, payload: dict, db: AsyncSession) -> Tag:
    tag = await get_tag_by_id(id, db)
    if payload.get('name') and tag.name != payload['name']:
        _tag = await db.scalar(select(Tag).where(Tag.name == payload['name']))
        if _tag:
            raise ConflictException('Tag with name ({}) already exists'.format(
                _tag.name), str(_tag.id))
    if payload.get('slug') and tag.slug != payload['slug']:
        _tag = await db.scalar(select(Tag).where(Tag.slug == payload['slug']))
        if _tag:
            raise ConflictException('Tag with slug ({}) already exists'.format(
                _tag.slug), str(_tag.id))

    logger.debug(f'Updating tag with payload: {payload}')
    [setattr(tag, key, value)
     for key, value in payload.items()]
    await db.commit()
    logger.info(f'Tag updated {tag}')
    return tag


async def delete_tag(id: UUID, db: AsyncSession) -> None:
    tag = await db.get(Tag, id)
    await db.delete(tag)
    await db.commit()

    logger.info(f'Tag deleted {tag}')
