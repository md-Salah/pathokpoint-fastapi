import logging
import traceback
from typing import Sequence, Union
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query, selectinload
from sqlalchemy.sql.selectable import Select

from app.controller.exception import (
    ConflictException,
    NotFoundException,
    UnhandledException,
)
from app.controller.image import validate_img
from app.filter_schema.author import AuthorFilter
from app.models import Author, Book, Category, Publisher, User, Tag

logger = logging.getLogger(__name__)

query_selectinload = select(Author).options(
    selectinload(Author.image),
    selectinload(Author.banner)
)


async def get_author_by_id(id: UUID, db: AsyncSession) -> Author:
    author = await db.scalar(query_selectinload.filter(Author.id == id))
    if not author:
        raise NotFoundException('Author not found', str(id))
    return author


async def get_author_by_slug(slug: str, db: AsyncSession) -> Author:
    author = await db.scalar(query_selectinload.filter(Author.slug == slug))
    if not author:
        raise NotFoundException('Author not found')
    return author


def apply_filter(fltr: AuthorFilter, query: Union[Query, Select]) -> Union[Query, Select]:
    filter = fltr.model_copy()
    category__slug__in = filter.pop('category__slug__in')
    publisher__slug__in = filter.pop('publisher__slug__in')
    tag__slug__in = filter.pop('tag__slug__in')

    if publisher__slug__in or category__slug__in or tag__slug__in:
        query = query.join(Author.books)

    if publisher__slug__in:
        query = query.filter(
            Book.publisher.has(Publisher.slug.in_(publisher__slug__in))
        )
    if category__slug__in:
        query = query.filter(
            Book.categories.any(Category.slug.in_(category__slug__in))
        )
    if tag__slug__in:
        query = query.filter(
            Book.tags.any(Tag.slug.in_(tag__slug__in))
        )
    if q := filter.pop('q'):
        query = query.filter(or_(
            Author.name.ilike(f'%{q}%'),
            Author.slug.ilike('%{}%'.format(q.replace(' ', '-'))),
            func.similarity(Author.name, q) > 0.5,
            func.similarity(Author.slug, q) > 0.5
        ))

    query = filter.filter(query)
    query = query.distinct()
    return query


async def get_all_authors(filter: AuthorFilter, page: int, per_page: int, db: AsyncSession) -> Sequence[Author]:
    offset = (page - 1) * per_page

    query = apply_filter(filter, query_selectinload)

    try:
        result = await db.execute(query.offset(offset).limit(per_page))
    except Exception:
        logger.error(traceback.format_exc())
        raise UnhandledException()

    return result.scalars().unique().all()


async def count_author(filter: AuthorFilter, db: AsyncSession) -> int:
    query = apply_filter(filter, select(Author))
    count_query = select(func.count()).select_from(query.subquery())

    try:
        result = await db.execute(count_query)
    except Exception:
        logger.error(traceback.format_exc())
        raise UnhandledException()

    return result.scalar_one()


async def create_author(payload: dict, db: AsyncSession) -> Author:
    _author = await db.scalar(select(Author).filter(or_(Author.name == payload['name'], Author.slug == payload['slug'])))
    if _author:
        if _author.name == payload['name']:
            raise ConflictException(
                'Author name already exists', str(_author.id))
        else:
            raise ConflictException(
                'Author slug already exists', str(_author.id))

    if 'image_id' in payload:
        payload['image'] = await validate_img(payload['image_id'], db)
    if 'banner_id' in payload:
        payload['banner'] = await validate_img(payload['banner_id'], db)

    author = Author(**payload)
    db.add(author)
    await db.commit()

    logger.info(f'Author created: {author}')
    return author


async def update_author(id: UUID, payload: dict, db: AsyncSession) -> Author:
    author = await get_author_by_id(id, db)
    if payload.get('name') and author.name != payload['name']:
        _author = await db.scalar(select(Author).filter(Author.name == payload['name']))
        if _author:
            raise ConflictException(
                'Author name already exists', str(_author.id))
    if payload.get('slug') and author.slug != payload['slug']:
        _author = await db.scalar(select(Author).filter(Author.slug == payload['slug']))
        if _author:
            raise ConflictException(
                'Author slug already exists', str(_author.id))

    if 'image_id' in payload:
        payload['image'] = await validate_img(payload['image_id'], db)
    if 'banner_id' in payload:
        payload['banner'] = await validate_img(payload['banner_id'], db)

    [setattr(author, key, value) for key, value in payload.items()]
    await db.commit()

    logger.info(f'Author updated: {author}')
    return author


async def follow_author(author_id: UUID, user_id: UUID, db: AsyncSession) -> Author:
    author = await get_author_by_id(author_id, db)
    user = await db.scalar(select(User).filter(User.id == user_id))
    if not user:
        raise NotFoundException('User not found', str(user_id))

    if user not in await author.awaitable_attrs.followers:
        author.followers.append(user)
        author.followers_count += 1
        await db.commit()
        logger.info(f'User {user} followed author {author}')
    else:
        raise ConflictException(
            'You are already following the author', str(author_id))

    return author


async def unfollow_author(author_id: UUID, user_id: UUID, db: AsyncSession) -> Author:
    author = await get_author_by_id(author_id, db)
    user = await db.scalar(select(User).filter(User.id == user_id))
    if not user:
        raise NotFoundException('User not found', str(user_id))

    if user not in await author.awaitable_attrs.followers:
        raise ConflictException(
            'You are not following the author', str(author_id))
    else:
        author.followers.remove(user)
        author.followers_count -= 1
        await db.commit()
        logger.info(f'User {user} unfollowed author {author}')

    return author


async def delete_author(id: UUID, db: AsyncSession) -> None:
    author = await get_author_by_id(id, db)
    await db.delete(author)
    await db.commit()

    logger.info(f'Author deleted: {author}')
