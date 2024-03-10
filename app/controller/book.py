from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import joinedload

from slugify import slugify

from app.models import Book, Author, Category, Image, Publisher, Tag

query = select(Book).options(
    joinedload(Book.publisher),
    joinedload(Book.authors),
    joinedload(Book.translators),
    joinedload(Book.categories),
    joinedload(Book.images),
    joinedload(Book.tags)
)


async def get_book_by_id(id: UUID, db: AsyncSession) -> Book:
    book = await db.scalar(query.where(Book.id == id))
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Book with id {id} not found')
    return book


async def get_all_books(page: int, per_page: int, db: AsyncSession) -> Sequence[Book]:
    offset = (page - 1) * per_page

    result = await db.execute(query.offset(offset).limit(per_page))
    books = result.unique().scalars().all()
    return books


async def search_books(q: str, db: AsyncSession) -> Sequence[Book]:
    result = await db.execute(query.where(
        or_(
            Book.name.ilike(f'%{q}%'),
            Book.slug.ilike(f'%{q}%'),
        )
    ))
    books = result.unique().scalars().all()
    return books


async def create_book(payload: dict, db: AsyncSession) -> Book:
    if await db.scalar(select(Book).where(Book.sku == payload['sku'])):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Book with sku ({}) already exists'.format(payload['sku']))

    payload['slug'] = slugify(payload['slug'])
    payload = await build_relationships(payload, db)

    book = Book(**payload)
    db.add(book)
    await db.commit()

    return book


async def update_book(id: UUID, payload: dict, db: AsyncSession) -> Book:
    book = await db.scalar(query.where(Book.id == id))
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Book with id ({id}) not found')

    if payload.get('slug'):
        payload['slug'] = slugify(payload['slug'])
    payload = await build_relationships(payload, db)

    [setattr(book, key, value) for key, value in payload.items()]

    await db.commit()
    return book


async def delete_book(id: UUID, db: AsyncSession) -> None:
    book = await db.get(Book, id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Book with id ({id}) not found')
    await db.delete(book)
    await db.commit()


async def count_book(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Book))
    return result.scalar_one()


async def build_relationships(payload: dict, db: AsyncSession) -> dict:
    if payload.get('publisher'):
        payload['publisher'] = await db.get(Publisher, payload['publisher'])
    if payload.get('authors'):
        payload['authors'] = [await db.get(Author, author_id) for author_id in payload['authors']]
    if payload.get('translators'):
        payload['translators'] = [await db.get(Author, translator_id) for translator_id in payload['translators']]
    if payload.get('categories'):
        payload['categories'] = [await db.get(Category, category_id) for category_id in payload['categories']]
    if payload.get('images'):
        payload['images'] = [await db.get(Image, image_id) for image_id in payload['images']]
    if payload.get('tags'):
        payload['tags'] = [await db.get(Tag, tag_id) for tag_id in payload['tags']]

    return payload
