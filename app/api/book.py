from fastapi import APIRouter, status, Depends, Query, Response, Path
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi_filter import FilterDepends

from app.filter_schema.book import BookFilter
import app.pydantic_schema.book as schema
from app.config.database import get_db
import app.controller.book as book_service

router = APIRouter(prefix='/book')


@router.get('/id/{id}', response_model=schema.BookOut)
async def get_book_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
    return await book_service.get_book_by_id(id, db)


@router.get('/all', response_model=list[schema.BookOut])
async def get_all_books(*, 
                        page: int = Query(1, ge=1), 
                        per_page: int = Query(10, ge=1, le=100), 
                        book_filter: BookFilter = FilterDepends(BookFilter),
                        authors: str | None = Query(None, description='Comma separated author slugs', pattern=r'^[\w-]+(,[\w-]+)*$'),
                        categories: str | None = Query(None, description='Comma separated category slugs', pattern=r'^[\w-]+(,[\w-]+)*$'),
                        publishers: str | None = Query(None, description='Comma separated publisher slugs', pattern=r'^[\w-]+(,[\w-]+)*$'),
                        translators: str | None = Query(None, description='Comma separated translator slugs', pattern=r'^[\w-]+(,[\w-]+)*$'),
                        tags: str | None = Query(None, description='Comma separated tag slugs', pattern=r'^[\w-]+(,[\w-]+)*$'),
                        db: AsyncSession = Depends(get_db),  
                        response: Response):
    books = await book_service.get_all_books(page, per_page, db, book_filter, authors, categories, publishers, translators, tags)
    total_books = await book_service.count_books(db, book_filter, authors, categories, publishers, translators, tags)

    response.headers['X-Total-Count'] = str(total_books)
    response.headers['X-Total-Pages'] = str(-(-total_books // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return books


@router.post('', response_model=schema.BookOutAdmin, status_code=status.HTTP_201_CREATED)
async def create_book(payload: schema.CreateBook, db: AsyncSession = Depends(get_db)):
    return await book_service.create_book(payload.model_dump(), db)


@router.patch('/{id}', response_model=schema.BookOutAdmin)
async def update_book(id: UUID, payload: schema.UpdateBook, db: AsyncSession = Depends(get_db)):
    return await book_service.update_book(id, payload.model_dump(exclude_unset=True), db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(id: UUID, db: AsyncSession = Depends(get_db)):
    await book_service.delete_book(id, db)
