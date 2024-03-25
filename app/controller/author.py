from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, delete, update
from typing import Sequence
from uuid import UUID

from app.models import Author
from app.filter_schema.author import AuthorFilter


async def get_author_by_id(id: UUID, db: AsyncSession) -> Author:
    result = await db.execute(select(Author).filter(Author.id == id))
    author = result.scalar()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Author with id {id} not found')
    return author


async def get_author_by_slug(slug: str, db: AsyncSession) -> Author:
    author = await db.scalar(select(Author).filter(Author.slug == slug))
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Author with slug {slug} not found')
    return author


async def get_all_authors(page: int, per_page: int, db: AsyncSession, author_filter: AuthorFilter) -> Sequence[Author]:
    offset = (page - 1) * per_page

    query = select(Author)
    query = author_filter.filter(query)
    query = query.offset(offset).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


async def count_author(db: AsyncSession, author_filter: AuthorFilter) -> int:
    query = select(func.count(Author.id))
    query = author_filter.filter(query)
    result = await db.execute(query)
    return result.scalar_one()


async def create_author(payload: dict, db: AsyncSession) -> Author:
    _author = await db.scalar(select(Author).filter(or_(Author.name == payload['name'], Author.slug == payload['slug'])))
    if _author:
        if _author.name == payload['name']:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Author with name {} already exists'.format(payload["name"]),
                                    'resource_id': f'{_author.id}'
                                })
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Author with slug {} already exists'.format(payload["slug"]),
                                    'resource_id': f'{_author.id}'
                                })

    author = Author(**payload)
    db.add(author)
    await db.commit()
    return author


async def update_author(id: UUID, payload: dict, db: AsyncSession) -> Author:
    author = await get_author_by_id(id, db)
    if payload.get('name') and author.name != payload['name']:
        _author = await db.scalar(select(Author).filter(Author.name == payload['name']))
        if _author:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Author with name {} already exists'.format(payload["name"]),
                                    'resource_id': f'{_author.id}'
                                })
    if payload.get('slug') and author.slug != payload['slug']:
        _author = await db.scalar(select(Author).filter(Author.slug == payload['slug']))
        if _author:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={
                                    'msg': 'Author with slug {} already exists'.format(payload["slug"]),
                                    'resource_id': f'{_author.id}'
                                })

    [setattr(author, key, value) for key, value in payload.items()]
    await db.commit()
    return author


async def delete_author(id: UUID, db: AsyncSession) -> None:
    await db.execute(delete(Author).where(Author.id == id))
    await db.commit()
