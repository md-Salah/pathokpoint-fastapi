from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Sequence

from app.models.book import Book
import app.pydantic_schema.book as schema
import app.controller.csv as csv_service
from app.controller.utility import slugify


def get_book_by_id(id: UUID, db: Session) -> schema.ReadBook:
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Book with id {id} not found')
    return book


def get_book_by_slug(slug: str, db: Session) -> schema.ReadBook:
    book = db.query(Book).filter(Book.slug == slug).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Book with slug {slug} not found')
    return book


def get_all_books(page: int, per_page: int, db: Session) -> Sequence[schema.ReadBook]:
    offset = (page - 1) * per_page
    books = db.query(Book).offset(offset).limit(per_page).all()
    return books


def create_book(payload: schema.CreateBook, db: Session) -> schema.ReadBook:
    # sku should be unique if not None
    if payload.sku and db.query(Book).filter(Book.sku == payload.sku).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Book with sku {payload.sku} already exists')

    payload.slug = generate_unique_slug(payload, db)

    new_book = Book(**schema.CreateBook.model_dump(payload))
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


def update_book(id: UUID, payload: schema.UpdateBook, db: Session) -> schema.ReadBook:
    book = get_book_by_id(id, db)

    data = schema.UpdateBook.model_dump(payload, exclude_unset=True)
    for key, value in data.items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)
    return book


def delete_book(id: UUID, db: Session) -> schema.ReadBook:
    book = get_book_by_id(id, db)
    db.delete(book)
    db.commit()
    return book


def count_book(db: Session) -> int:
    return db.query(Book).count()


def bulk_create_n_update_books(payload: list[schema.CreateBook], db: Session) -> list[Book]:
    new_books = []
    existing_books = []

    for book in payload:
        # Update book if sku exists
        if book.sku:
            existing_book = db.query(Book).filter(Book.sku == book.sku).first()
            if existing_book:
                [existing_book.__setattr__(key, value) for key, value in schema.CreateBook.model_dump(
                    book, exclude_unset=True).items()]
                existing_books.append(existing_book)
                continue

        book.slug = generate_unique_slug(book, db)
        new_books.append(Book(**schema.CreateBook.model_dump(book)))

    db.add_all(new_books)
    db.commit()
    for book in new_books + existing_books:
        db.refresh(book)

    return new_books + existing_books


def import_book_by_csv(file: UploadFile, db: Session) -> str:
    books = csv_service.clean_csv(file.file)
    payload = [schema.CreateBook(**book) for book in books]
    new_books = bulk_create_n_update_books(payload, db)

    return csv_service.book_to_csv_stream([book_orm_to_dict(book) for book in new_books])

def export_book_to_csv(db: Session) -> str:
    books = db.query(Book).all()
    return csv_service.book_to_csv_stream([book_orm_to_dict(book) for book in books])

# Additional functions
def generate_unique_slug(payload, db: Session) -> str:
    slug = payload.slug.replace(
        ' ', '-').lower() if payload.slug else slugify(payload.banglish_name or payload.name)
    existing_book = db.query(Book).filter(Book.slug.like(f'{slug}%')).all()
    return f"{slug}-{len(existing_book)}" if existing_book else slug

def book_orm_to_dict(book: Book):
    book_dict = book.__dict__
    book_dict.pop('_sa_instance_state')
    return book_dict
