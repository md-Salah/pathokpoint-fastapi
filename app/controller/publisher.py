from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, delete, update
from typing import Sequence
from uuid import UUID

from app.models import Publisher, Image
from app.filter_schema.publisher import PublisherFilter


async def get_publisher_by_id(id: UUID, db: AsyncSession) -> Publisher:
    publisher = await db.scalar(select(Publisher).filter(Publisher.id == id))
    if not publisher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Publisher with id {id} not found')
    return publisher


async def get_publisher_by_slug(slug: str, db: AsyncSession) -> Publisher:
    publisher = await db.scalar(select(Publisher).filter(Publisher.slug == slug))
    if not publisher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Publisher with slug {slug} not found')
    return publisher


async def get_all_publishers(page: int, per_page: int, db: AsyncSession, publisher_filter: PublisherFilter) -> Sequence[Publisher]:
    offset = (page - 1) * per_page

    query = select(Publisher)
    query = publisher_filter.filter(query)
    query = query.offset(offset).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


async def count_publisher(db: AsyncSession, publisher_filter: PublisherFilter) -> int:
    query = select(func.count(Publisher.id))
    query = publisher_filter.filter(query)
    result = await db.execute(query)
    return result.scalar_one()


async def create_publisher(payload: dict, db: AsyncSession) -> Publisher:
    _publisher = await db.scalar(select(Publisher).filter(or_(Publisher.name == payload['name'], Publisher.slug == payload['slug'])))
    if _publisher:
        if _publisher.name == payload['name']:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Publisher with name {} already exists'.format(payload["name"]),
                                    'resource_id': f'{_publisher.id}'
                                })
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Publisher with slug {} already exists'.format(payload["slug"]),
                                    'resource_id': f'{_publisher.id}'
                                })

    if payload.get('image'):
        payload['image'] = await db.get(Image, payload['image'])
    if payload.get('banner'):
        payload['banner'] = await db.get(Image, payload['banner'])

    publisher = Publisher(**payload)
    db.add(publisher)
    await db.commit()
    return publisher


async def update_publisher(id: UUID, payload: dict, db: AsyncSession) -> Publisher:
    publisher = await get_publisher_by_id(id, db)
    if payload.get('name') and publisher.name != payload['name']:
        _publisher = await db.scalar(select(Publisher).filter(Publisher.name == payload['name']))
        if _publisher:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Publisher with name {} already exists'.format(payload["name"]),
                                    'resource_id': f'{_publisher.id}'
                                })
    if payload.get('slug') and publisher.slug != payload['slug']:
        _publisher = await db.scalar(select(Publisher).filter(Publisher.slug == payload['slug']))
        if _publisher:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Publisher with slug {} already exists'.format(payload["slug"]),
                                    'resource_id': f'{_publisher.id}'
                                })

    if payload.get('image'):
        payload['image'] = await db.get(Image, payload['image'])
    if payload.get('banner'):
        payload['banner'] = await db.get(Image, payload['banner'])

    [setattr(publisher, key, value) for key, value in payload.items()]
    await db.commit()
    return publisher


async def delete_publisher(id: UUID, db: AsyncSession) -> None:
    await db.execute(delete(Publisher).where(Publisher.id == id))
    await db.commit()
