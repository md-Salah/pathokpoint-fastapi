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
from app.filter_schema.publisher import PublisherFilter
from app.models import Author, Book, Category, Publisher

logger = logging.getLogger(__name__)

query_selectinload = select(Publisher).options(selectinload(
    Publisher.image), selectinload(Publisher.banner))

query_joinedload = select(Publisher).options(joinedload(
    Publisher.image), joinedload(Publisher.banner))


async def get_publisher_by_id(id: UUID, db: AsyncSession) -> Publisher:
    publisher = await db.scalar(query_selectinload.filter(Publisher.id == id))
    if not publisher:
        raise NotFoundException('Publisher not found', str(id))
    return publisher


async def get_publisher_by_slug(slug: str, db: AsyncSession) -> Publisher:
    publisher = await db.scalar(query_selectinload.filter(Publisher.slug == slug))
    if not publisher:
        raise NotFoundException('Publisher not found')
    return publisher


def apply_filter(fltr: PublisherFilter, query: Union[Query, Select]) -> Union[Query, Select]:
    filter = fltr.model_copy()
    author__name__in = filter.pop('author__name__in')
    category__name__in = filter.pop('category__name__in')

    if author__name__in or category__name__in:
        query = query.join(Publisher.books)

    if author__name__in:
        query = query.filter(
            Book.authors.any(Author.name.in_(author__name__in))
        )
    if category__name__in:
        query = query.filter(
            Book.categories.any(Category.name.in_(category__name__in))
        )
    if q := filter.pop('q'):
        query = query.filter(or_(
            Publisher.name.ilike(f'%{q}%'),
            Publisher.slug.ilike(f'%{q.replace(' ', '-')}%'),
            func.similarity(Publisher.name, q) > 0.5,
            func.similarity(Publisher.slug, q) > 0.5
        ))

    query = filter.filter(query)
    query = query.distinct()
    return query


async def get_all_publishers(filter: PublisherFilter, page: int, per_page: int, db: AsyncSession) -> Sequence[Publisher]:
    offset = (page - 1) * per_page

    query = apply_filter(filter, query_selectinload)

    try:
        result = await db.execute(query.offset(offset).limit(per_page))
    except Exception:
        logger.error(traceback.format_exc())
        raise UnhandledException()

    return result.scalars().unique().all()


async def count_publisher(filter: PublisherFilter, db: AsyncSession) -> int:
    query = apply_filter(filter, select(Publisher))
    count_query = select(func.count()).select_from(query.subquery())

    try:
        result = await db.execute(count_query)
    except Exception:
        logger.error(traceback.format_exc())
        raise UnhandledException()

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
        payload['image'] = await validate_img(payload['image_id'], db)
    if 'banner_id' in payload:
        payload['banner'] = await validate_img(payload['banner_id'], db)

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
        payload['image'] = await validate_img(payload['image_id'], db)
    if 'banner_id' in payload:
        payload['banner'] = await validate_img(payload['banner_id'], db)

    [setattr(publisher, key, value) for key, value in payload.items()]
    await db.commit()

    logger.info(f'Publisher updated: {publisher}')
    return publisher


async def delete_publisher(id: UUID, db: AsyncSession) -> None:
    publisher = await get_publisher_by_id(id, db)
    await db.delete(publisher)
    await db.commit()

    logger.info(f'Publisher deleted: {publisher}')
