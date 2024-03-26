from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, delete, update
from typing import Sequence
from uuid import UUID

from app.filter_schema.category import CategoryFilter
from app.models import Category, Image


async def get_category_by_id(id: UUID, db: AsyncSession) -> Category:
    category = await db.scalar(select(Category).filter(Category.id == id))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Category with id {id} not found')
    return category


async def get_category_by_slug(slug: str, db: AsyncSession) -> Category:
    category = await db.scalar(select(Category).filter(Category.slug == slug))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Category with slug {slug} not found')
    return category


async def get_all_categories(page: int, per_page: int, db: AsyncSession, category_filter: CategoryFilter) -> Sequence[Category]:
    offset = (page - 1) * per_page

    query = select(Category)
    query = category_filter.filter(query)
    query = query.offset(offset).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


async def count_category(db: AsyncSession, category_filter: CategoryFilter) -> int:
    query = select(func.count(Category.id))
    query = category_filter.filter(query)
    result = await db.execute(query)
    return result.scalar_one()


async def create_category(payload: dict, db: AsyncSession) -> Category:
    _category = await db.scalar(select(Category).filter(or_(Category.name == payload['name'], Category.slug == payload['slug'])))
    if _category:
        if _category.name == payload['name']:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Category with name {} already exists'.format(payload["name"]),
                                    'resource_id': f'{_category.id}'
                                })
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Category with slug {} already exists'.format(payload["slug"]),
                                    'resource_id': f'{_category.id}'
                                })

    if payload.get('image'):
        payload['image'] = await db.get(Image, payload['image'])
    if payload.get('banner'):
        payload['banner'] = await db.get(Image, payload['banner'])

    category = Category(**payload)
    db.add(category)
    await db.commit()
    return category


async def update_category(id: UUID, payload: dict, db: AsyncSession) -> Category:
    category = await get_category_by_id(id, db)
    if payload.get('name') and category.name != payload['name']:
        _category = await db.scalar(select(Category).filter(Category.name == payload['name']))
        if _category:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Category with name {} already exists'.format(payload["name"]),
                                    'resource_id': f'{_category.id}'
                                })
    if payload.get('slug') and category.slug != payload['slug']:
        _category = await db.scalar(select(Category).filter(Category.slug == payload['slug']))
        if _category:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Category with slug {} already exists'.format(payload["slug"]),
                                    'resource_id': f'{_category.id}'
                                })

    if payload.get('image'):
        payload['image'] = await db.get(Image, payload['image'])
    if payload.get('banner'):
        payload['banner'] = await db.get(Image, payload['banner'])

    [setattr(category, key, value) for key, value in payload.items()]

    await db.commit()
    return category


async def delete_category(id: UUID, db: AsyncSession) -> None:
    await db.execute(delete(Category).where(Category.id == id))
    await db.commit()
