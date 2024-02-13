from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.book import Book
import app.pydantic_schema.book as schema
from app.controller.utility import slugify

def get_book_by_id(id: UUID, db: Session):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Book with id {id} not found')
    return book

def get_book_by_slug(slug: str, db: Session):
    book = db.query(Book).filter(Book.slug == slug).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Book with slug {slug} not found')
    return book

def get_all_books(page: int, per_page: int, db: Session):
    offset = (page - 1) * per_page
    books = db.query(Book).offset(offset).limit(per_page).all()
    return books
    
def create_book(payload: schema.CreateBook, db: Session):
    # sku should be unique if not None
    if payload.sku and db.query(Book).filter(Book.sku == payload.sku).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Book with sku {payload.sku} already exists')

    # generate unique slug
    slug = payload.slug.replace(
        ' ', '-').lower() if payload.slug else slugify(payload.banglish_name or payload.name)
    existing_book = db.query(Book).filter(Book.slug.like(f'{slug}%')).all()
    payload.slug = f"{slug}-{len(existing_book)}" if existing_book else slug

    new_book = Book(**schema.CreateBook.model_dump(payload))
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book

def update_book(id: UUID, payload: schema.UpdateBook, db: Session):
    book = get_book_by_id(id, db)

    data = schema.UpdateBook.model_dump(payload, exclude_unset=True)
    for key, value in data.items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)
    return book

def delete_book(id: UUID, db: Session):
    book = get_book_by_id(id, db)
    db.delete(book)
    db.commit()
    return book

def count_book(db: Session):
    return db.query(Book).count()