from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import joinedload
from typing import Sequence
from uuid import UUID
import logging

from app.filter_schema.category import CategoryFilter
from app.models import Category
from app.controller.exception import NotFoundException, ConflictException
from app.controller.image import attach_image, detach_images

logger = logging.getLogger(__name__)

query = select(Category).options(joinedload(Category.parent),
                                 joinedload(Category.children),  # type: ignore
                                 joinedload(Category.image),
                                 joinedload(Category.banner))


async def get_category_by_id(id: UUID, db: AsyncSession) -> Category:
    category = await db.scalar(query.filter(Category.id == id))
    if not category:
        raise NotFoundException('Category not found', str(id))
    return category


async def get_category_by_slug(slug: str, db: AsyncSession) -> Category:
    category = await db.scalar(query.filter(Category.slug == slug))
    if not category:
        raise NotFoundException('Category not found')
    return category


async def get_all_categories(filter: CategoryFilter, page: int, per_page: int, db: AsyncSession) -> Sequence[Category]:
    offset = (page - 1) * per_page

    stmt = filter.filter(query)
    stmt = stmt.offset(offset).limit(per_page)
    result = await db.execute(stmt)
    return result.scalars().unique().all()


async def count_category(filter: CategoryFilter, db: AsyncSession) -> int:
    stmt = select(func.count(Category.id))
    stmt = filter.filter(stmt)
    result = await db.execute(stmt)
    return result.scalar_one()


async def create_category(payload: dict, db: AsyncSession) -> Category:
    _category = await db.scalar(select(Category).filter(or_(Category.name == payload['name'], Category.slug == payload['slug'])))
    if _category:
        if _category.name == payload['name']:
            raise ConflictException('Category with name {} already exists'.format(
                _category.name), str(_category.id))
        else:
            raise ConflictException('Category with slug {} already exists'.format(
                _category.slug), str(_category.id))

    if 'image_id' in payload:
        payload['image'] = await attach_image(payload['image_id'], None, db)
    if 'banner_id' in payload:
        payload['banner'] = await attach_image(payload['banner_id'], None, db)
    if payload.get('parent'):
        payload['parent'] = (await db.scalars(select(Category).filter(Category.id.in_(payload['parent'])))).all()

    category = Category(**payload)
    db.add(category)
    await db.commit()
    logger.info(f'Category created: {category}')
    return category


async def update_category(id: UUID, payload: dict, db: AsyncSession) -> Category:
    category = await get_category_by_id(id, db)
    if payload.get('name') and category.name != payload['name']:
        _category = await db.scalar(select(Category).filter(Category.name == payload['name']))
        if _category:
            raise ConflictException('Category with name {} already exists'.format(
                _category.name), str(_category.id))
    if payload.get('slug') and category.slug != payload['slug']:
        _category = await db.scalar(select(Category).filter(Category.slug == payload['slug']))
        if _category:
            raise ConflictException('Category with slug {} already exists'.format(
                _category.slug), str(_category.id))

    if 'image_id' in payload:
        payload['image'] = await attach_image(payload['image_id'], category.image_id, db)
    if 'banner_id' in payload:
        payload['banner'] = await attach_image(payload['banner_id'], category.banner_id, db)
    if 'parent' in payload:
        if payload['parent']:
            payload['parent'] = (await db.scalars(select(Category).filter(Category.id.in_(payload['parent'])))).all()
        else:
            payload['parent'] = []

    [setattr(category, key, value) for key, value in payload.items()]

    await db.commit()
    logger.info(f'Category updated: {category}')
    return category


async def delete_category(id: UUID, db: AsyncSession) -> None:
    category = await db.scalar(select(Category).filter(Category.id == id))
    if not category:
        raise NotFoundException('Category not found', str(id))

    await detach_images(db, category.image_id, category.banner_id)
    await db.delete(category)
    await db.commit()

    logger.info(f'Category deleted: {category}')
