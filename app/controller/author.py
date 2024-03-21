from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
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
    author = Author(**payload)

    db.add(author)
    await db.commit()

    return author


async def update_author(id: UUID, payload: dict, db: AsyncSession) -> Author:
    author = await get_author_by_id(id, db)

    [setattr(author, key, value) for key, value in payload.items()]

    await db.commit()
    return author


async def delete_author(id: UUID, db: AsyncSession) -> None:
    author = await get_author_by_id(id, db)
    await db.delete(author)
    await db.commit()

