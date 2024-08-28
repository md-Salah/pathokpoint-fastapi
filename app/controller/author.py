from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Sequence
from uuid import UUID
import logging

from app.models import Author, User
from app.filter_schema.author import AuthorFilter
from app.controller.exception import NotFoundException, ConflictException
from app.controller.image import validate_img

logger = logging.getLogger(__name__)

query = select(Author).options(selectinload(
    Author.image), selectinload(Author.banner))


async def get_author_by_id(id: UUID, db: AsyncSession) -> Author:
    author = await db.scalar(query.filter(Author.id == id))
    if not author:
        raise NotFoundException('Author not found', str(id))
    return author


async def get_author_by_slug(slug: str, db: AsyncSession) -> Author:
    author = await db.scalar(query.filter(Author.slug == slug))
    if not author:
        raise NotFoundException('Author not found')
    return author


async def get_all_authors(filter: AuthorFilter, page: int, per_page: int, db: AsyncSession) -> Sequence[Author]:
    offset = (page - 1) * per_page

    stmt = filter.filter(query)
    stmt = stmt.offset(offset).limit(per_page)
    result = await db.execute(stmt)
    return result.scalars().unique().all()


async def count_author(filter: AuthorFilter, db: AsyncSession) -> int:
    stmt = select(func.count(Author.id))
    stmt = filter.filter(stmt)
    result = await db.execute(stmt)
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
