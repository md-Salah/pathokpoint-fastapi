from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, or_
from uuid import UUID
from typing import Sequence

from app.models.book import Book
import app.pydantic_schema.book as schema
# import app.controller.csv as csv_service
from app.controller.utility import slugify


async def get_book_by_id(id: UUID, db: AsyncSession) -> schema.ReadBook:
    result = await db.execute(select(Book).where(Book.id == id))
    book = result.scalar()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Book with id {id} not found')
    return book


async def get_book_by_slug(slug: str, db: AsyncSession) -> schema.ReadBook:
    result = await db.execute(select(Book).where(Book.slug == slug))
    book = result.scalar()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Book with slug {slug} not found')
    return book


async def get_all_books(page: int, per_page: int, db: AsyncSession) -> Sequence[schema.ReadBook]:
    offset = (page - 1) * per_page
    
    result = await db.execute(select(Book).offset(offset).limit(per_page))
    books = result.scalars().all()
    return books

async def search_books(q: str, db: AsyncSession) -> Sequence[schema.ReadBook]:
    result = await db.execute(select(Book).where(
        or_(
            Book.name.ilike(f'%{q}%'),
            Book.banglish_name.ilike(f'%{q}%'),
        )
    ))
    books = result.scalars().all()
    return books

async def create_book(payload: schema.CreateBook, db: AsyncSession) -> schema.ReadBook:
    # if sku it should be unique
    if payload.sku and await db.scalar(select(Book).where(Book.sku == payload.sku)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Book with sku {payload.sku} already exists')

    payload.slug = await generate_unique_slug(payload, db)

    new_book = Book(**schema.CreateBook.model_dump(payload))
    db.add(new_book)
    await db.commit()

    return new_book


async def update_book(id: UUID, payload: schema.UpdateBook, db: AsyncSession) -> schema.ReadBook:
    book = await get_book_by_id(id, db)

    data = schema.UpdateBook.model_dump(payload, exclude_unset=True)
    for key, value in data.items():
        setattr(book, key, value)

    await db.commit()
    return book

async def delete_book(id: UUID, db: AsyncSession):
    book = await get_book_by_id(id, db)
    
    if book:       
        await db.execute(delete(Book).where(Book.id == id))
        await db.commit()
    


async def count_book(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Book))
    return result.scalar_one()


async def bulk_create_n_update_books(payload: list[schema.CreateBook], db: AsyncSession) -> list[Book]:
    new_books = []
    existing_books = []

    for book in payload:
        # Update book if sku exists
        if book.sku:
            result = await db.execute(select(Book).where(Book.sku == book.sku))
            existing_book = result.scalar()
            if existing_book:
                [existing_book.__setattr__(key, value) for key, value in schema.CreateBook.model_dump(
                    book, exclude_unset=True).items()]
                existing_books.append(existing_book)
                continue

        book.slug = await generate_unique_slug(book, db)
        new_books.append(Book(**schema.CreateBook.model_dump(book)))

    db.add_all(new_books)
    await db.commit()

    return new_books + existing_books


# def import_book_from_csv(file: UploadFile, db: AsyncSession) -> str:
#     books = csv_service.clean_csv(file.file)
#     payload = [schema.CreateBook(**book) for book in books]
#     new_books = bulk_create_n_update_books(payload, db)

#     return csv_service.book_to_csv_stream([book_orm_to_dict(book) for book in new_books])

# def export_book_to_csv(db: AsyncSession) -> str:
#     books = db.query(Book).all()
#     return csv_service.book_to_csv_stream([book_orm_to_dict(book) for book in books])


# Additional functions
async def generate_unique_slug(payload, db: AsyncSession) -> str:
    slug = payload.slug.replace(
        ' ', '-').lower() if payload.slug else slugify(payload.banglish_name or payload.name)
    result = await db.execute(select(Book).filter(Book.slug.like(f'{slug}%')))
    existing_book = result.scalars().all()
    return f"{slug}-{len(existing_book)}" if existing_book else slug

def book_orm_to_dict(book: Book):
    book_dict = book.__dict__
    book_dict.pop('_sa_instance_state')
    return book_dict
