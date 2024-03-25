from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, delete
from typing import Sequence
from uuid import UUID

from app.models.tag import Tag
from app.filter_schema.tag import TagFilter


async def get_tag_by_id(id: UUID, db: AsyncSession) -> Tag:
    tag = await db.get(Tag, id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Tag with id ({id}) not found')
    return tag


async def get_all_tags(page: int, per_page: int, db: AsyncSession, tag_filter: TagFilter) -> Sequence[Tag]:
    offset = (page - 1) * per_page
    query = select(Tag)
    query = tag_filter.filter(query)
    query = query.offset(offset).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


async def count_tag(db: AsyncSession, tag_filter: TagFilter) -> int:
    query = select(func.count(Tag.id))
    query = tag_filter.filter(query)
    result = await db.execute(query)
    return result.scalar_one()


async def create_tag(payload: dict, db: AsyncSession) -> Tag:
    _tag = await db.scalar(select(Tag).where(or_(Tag.name == payload['name'], Tag.slug == payload['slug'])))
    if _tag:
        if _tag.name == payload['name']:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Tag with name ({}) already exists'.format(payload["name"]),
                                    'resource_id': f'{_tag.id}'
                                })
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Tag with slug ({}) already exists'.format(payload["slug"]),
                                    'resource_id': f'{_tag.id}'
                                })

    tag = Tag(**payload)
    db.add(tag)
    await db.commit()
    return tag


async def update_tag(id: UUID, payload: dict, db: AsyncSession) -> Tag:
    tag = await get_tag_by_id(id, db)
    if payload.get('name') and tag.name != payload['name']:
        _tag = await db.scalar(select(Tag).where(Tag.name == payload['name']))
        if _tag:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Tag with name ({}) already exists'.format(payload["name"]),
                                    'resource_id': f'{_tag.id}'
                                })
    if payload.get('slug') and tag.slug != payload['slug']:
        _tag = await db.scalar(select(Tag).where(Tag.slug == payload['slug']))
        if _tag:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Tag with slug ({}) already exists'.format(payload["slug"]),
                                    'resource_id': f'{_tag.id}'
                                })

    [setattr(tag, key, value)
     for key, value in payload.items()]
    await db.commit()
    return tag


async def delete_tag(id: UUID, db: AsyncSession) -> None:
    query = delete(Tag).where(Tag.id == id)
    await db.execute(query)
    await db.commit()
