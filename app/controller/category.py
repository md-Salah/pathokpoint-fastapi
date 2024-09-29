import logging
import traceback
from typing import Sequence, Union
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query, joinedload, selectinload
from sqlalchemy.sql.selectable import Select

from app.controller.exception import (
    ConflictException,
    NotFoundException,
    UnhandledException,
)
from app.controller.image import validate_img
from app.filter_schema.category import CategoryFilter
from app.models import Author, Book, Category, Publisher

logger = logging.getLogger(__name__)

query_selectinload = select(Category).options(
    selectinload(Category.parent),
    selectinload(Category.image),
    selectinload(Category.banner)
)

query_joinedload = select(Category).options(
    joinedload(Category.parent),
    joinedload(Category.image),
    joinedload(Category.banner)
)


async def get_category_by_id(id: UUID, db: AsyncSession) -> Category:
    category = await db.scalar(query_selectinload.filter(Category.id == id))
    if not category:
        raise NotFoundException('Category not found', str(id))
    return category


async def get_category_by_slug(slug: str, db: AsyncSession) -> Category:
    category = await db.scalar(query_selectinload.filter(Category.slug == slug))
    if not category:
        raise NotFoundException('Category not found')
    return category


def apply_filter(fltr: CategoryFilter, query: Union[Query, Select]) -> Union[Query, Select]:
    filter = fltr.model_copy()
    author__name__in = filter.pop('author__name__in')
    publisher__name__in = filter.pop('publisher__name__in')

    if author__name__in or publisher__name__in:
        query = query.join(Category.books)

    if author__name__in:
        query = query.filter(
            Book.authors.any(Author.name.in_(author__name__in))
        )
    if publisher__name__in:
        query = query.filter(
            Book.publisher.has(Publisher.name.in_(publisher__name__in))
        )
    if q := filter.pop('q'):
        query = query.filter(or_(
            Category.name.ilike(f'%{q}%'),
            Category.slug.ilike(f'%{q.replace(' ', '-')}%'),
            func.similarity(Category.name, q) > 0.5,
            func.similarity(Category.slug, q) > 0.5
        ))

    query = filter.filter(query)
    query = query.distinct()
    return query


async def get_all_categories(filter: CategoryFilter, page: int, per_page: int, db: AsyncSession) -> Sequence[Category]:
    offset = (page - 1) * per_page

    query = apply_filter(filter, query_selectinload)

    try:
        result = await db.execute(query.offset(offset).limit(per_page))
    except Exception:
        logger.error(traceback.format_exc())
        raise UnhandledException()

    return result.scalars().unique().all()


async def count_category(filter: CategoryFilter, db: AsyncSession) -> int:
    query = apply_filter(filter, select(Category))
    count_query = select(func.count()).select_from(query.subquery())

    try:
        result = await db.execute(count_query)
    except Exception:
        logger.error(traceback.format_exc())
        raise UnhandledException()

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
        payload['image'] = await validate_img(payload['image_id'], db)
    if 'banner_id' in payload:
        payload['banner'] = await validate_img(payload['banner_id'], db)
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
        payload['image'] = await validate_img(payload['image_id'], db)
    if 'banner_id' in payload:
        payload['banner'] = await validate_img(payload['banner_id'], db)

    if 'parent' in payload:
        payload['parent'] = (await db.scalars(select(Category).filter(
            Category.id.in_(payload['parent'])
        ))).all() if payload['parent'] else []

    [setattr(category, key, value) for key, value in payload.items()]

    await db.commit()
    logger.info(f'Category updated: {category}')
    return category


async def delete_category(id: UUID, db: AsyncSession) -> None:
    category = await db.scalar(select(Category).filter(Category.id == id))
    if not category:
        raise NotFoundException('Category not found', str(id))

    await db.delete(category)
    await db.commit()

    logger.info(f'Category deleted: {category}')
