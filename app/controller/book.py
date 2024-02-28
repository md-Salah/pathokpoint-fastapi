from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, or_
from uuid import UUID
from typing import Sequence
from sqlalchemy.orm import selectinload, joinedload

from app.models import Book
import app.pydantic_schema.book as book_schema
# import app.controller.csv as csv_service
from app.controller.utility import slugify

async def test(db: AsyncSession):
    # book = Book(**{
    #     'name': 'আগুনডানা মেয়ে',
    #     'slug': 'agun-dana-meye',
    #     'regular_price': 800,
    #     'sale_price': 584,
    # })
    # author = Author(**{
    #     'name': 'সাদাত হোসাইন',
    #     'banglish_name': 'Sadat Hossain',
    #     'slug': 'sadat-hossain',
    # })
    
    # db.add(book)
    # db.add(author)
    # book.authors.add(author)    
    # await db.commit()
    # id = '65ccf19c-679b-4155-8402-9577c6f1f2bb'
    
    book_with_authors = await (
        db.execute(select(Book).options(joinedload(Book.authors)).where(Book.id == id))
    )
    
    return book_with_authors.unique().scalars().all()

async def get_book_by_id(id: UUID, db: AsyncSession) -> book_schema.ReadBook:
    result = await db.execute(select(Book).where(Book.id == id))
    book = result.scalar()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Book with id {id} not found')
    return book


async def get_book_by_slug(slug: str, db: AsyncSession) -> book_schema.ReadBook:
    result = await db.execute(select(Book).where(Book.slug == slug))
    book = result.scalar()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Book with slug {slug} not found')
    return book


async def get_all_books(page: int, per_page: int, db: AsyncSession) -> Sequence[book_schema.ReadBook]:
    offset = (page - 1) * per_page
    
    result = await db.execute(select(Book).offset(offset).limit(per_page))
    books = result.scalars().all()
    return books

async def search_books(q: str, db: AsyncSession) -> Sequence[book_schema.ReadBook]:
    result = await db.execute(select(Book).where(
        or_(
            Book.name.ilike(f'%{q}%'),
            Book.slug.ilike(f'%{q}%'),
        )
    ))
    books = result.scalars().all()
    return books

async def create_book(payload: book_schema.CreateBook, db: AsyncSession) -> book_schema.ReadBook:
    # if sku it should be unique
    if payload.sku and await db.scalar(select(Book).where(Book.sku == payload.sku)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Book with sku {payload.sku} already exists')

    payload.slug = await generate_unique_slug(payload, db)

    book = Book(**payload.model_dump())
    db.add(book)
    await db.commit()

    return book_schema.ReadBook.model_validate(book)


async def update_book(id: UUID, payload: book_schema.UpdateBook, db: AsyncSession) -> book_schema.ReadBook:
    book = await get_book_by_id(id, db)

    data = book_schema.UpdateBook.model_dump(payload, exclude_unset=True)
    for key, value in data.items():
        setattr(book, key, value)

    await db.commit()
    return book

async def delete_book(id: UUID, db: AsyncSession):
    book = await get_book_by_id(id, db)
    await db.delete(book)   
    await db.commit()
    
async def count_book(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Book))
    return result.scalar_one()

# Bulk operations
async def bulk_create_n_update_books(payload: list[book_schema.CreateBook], db: AsyncSession) -> list[Book]:
    new_books = []
    existing_books = []

    for book in payload:
        # Update book if sku exists
        if book.sku:
            result = await db.execute(select(Book).where(Book.sku == book.sku))
            existing_book = result.scalar()
            if existing_book:
                [existing_book.__setattr__(key, value) for key, value in book_schema.CreateBook.model_dump(
                    book, exclude_unset=True).items()]
                existing_books.append(existing_book)
                continue

        book.slug = await generate_unique_slug(book, db)
        new_books.append(Book(**book_schema.CreateBook.model_dump(book)))

    db.add_all(new_books)
    await db.commit()

    return new_books + existing_books


# def import_book_from_csv(file: UploadFile, db: AsyncSession) -> str:
#     books = csv_service.clean_csv(file.file)
#     payload = [book_schema.CreateBook(**book) for book in books]
#     new_books = bulk_create_n_update_books(payload, db)

#     return csv_service.book_to_csv_stream([book_orm_to_dict(book) for book in new_books])

# def export_book_to_csv(db: AsyncSession) -> str:
#     books = db.query(Book).all()
#     return csv_service.book_to_csv_stream([book_orm_to_dict(book) for book in books])


async def set_price_in_bulk():
    pass

# Additional functions
async def generate_unique_slug(payload, db: AsyncSession) -> str:
    slug = payload.slug.replace(
        ' ', '-').lower() if payload.slug else slugify(payload.name)
    result = await db.execute(select(Book).filter(Book.slug.like(f'{slug}%')))
    existing_book = result.scalars().all()
    return f"{slug}-{len(existing_book)}" if existing_book else slug

def book_orm_to_dict(book: Book):
    book_dict = book.__dict__
    book_dict.pop('_sa_instance_state')
    return book_dict
