from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Sequence
from uuid import UUID

from app.models import Author
import app.pydantic_schema.author as author_schema
from app.controller.utility import slugify

async def get_author_by_id(id: UUID, db: AsyncSession) -> author_schema.AuthorOut:
    result = await db.execute(select(Author).filter(Author.id == id))
    author = result.scalar()
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Author with id {id} not found')
    return author

async def get_author_by_slug(slug: str, db: AsyncSession) -> author_schema.AuthorOut:
    result = await db.execute(select(Author).filter(Author.slug == slug))
    return result.scalars().first()

async def get_all_authors(page: int, per_page:int, db: AsyncSession) -> Sequence[author_schema.AuthorOut]:
    offset = (page - 1) * per_page

    result = await db.execute(select(Author).offset(offset).limit(per_page))
    return result.scalars().all()

async def create_author(payload: author_schema.CreateAuthor, db: AsyncSession) -> author_schema.AuthorOut:
    author = Author(**payload.model_dump(exclude_unset=True))
    author.slug = await generate_unique_slug(payload.slug, payload.name, db)

    db.add(author)
    await db.commit()

    print(author.__dict__)

    return author_schema.AuthorOut.model_validate(author)

async def update_author(id: UUID, payload: author_schema.UpdateAuthor, db: AsyncSession) -> author_schema.AuthorOut:
    author = await get_author_by_id(id, db)

    data = author_schema.UpdateAuthor.model_dump(payload, exclude_unset=True)
    [setattr(author, key, value) for key, value in data.items()]

    await db.commit()
    return author_schema.AuthorOut.model_validate(author)

async def delete_author(id: UUID, db: AsyncSession) -> None:
    author = await get_author_by_id(id, db)
    await db.delete(author)
    await db.commit()
    
async def count_author(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Author))
    return result.scalar_one()

# Additional Function
async def generate_unique_slug(slug: str | None, name: str, db: AsyncSession) -> str:
    slug = slug.replace(
        ' ', '-').lower() if slug else slugify(name)
    result = await db.execute(select(Author).filter(Author.slug.like(f'{slug}%')))
    existing_book = result.scalars().all()
    return f"{slug}-{len(existing_book)}" if existing_book else slug
