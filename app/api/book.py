from fastapi import APIRouter, status, Query, Response, File, UploadFile
from uuid import UUID
from fastapi_filter import FilterDepends

from app.filter_schema.book import BookFilter, BookFilterMinimal
import app.pydantic_schema.book as schema
from app.config.database import Session
import app.controller.book as book_service
import app.controller.csv as csv_service
from app.controller.auth import AdminAccessToken

router = APIRouter(prefix='/book')


@router.get('/id/{id}', response_model=schema.BookOut)
async def get_book_by_id(id: UUID, db: Session):
    return await book_service.get_book_by_id(id, db)


@router.get('/all', response_model=list[schema.BookOut])
async def get_all_books(*,
                        page: int = Query(1, ge=1),
                        per_page: int = Query(10, ge=1, le=100),
                        filter: BookFilter = FilterDepends(BookFilter),
                        db: Session,
                        response: Response):
    books = await book_service.get_all_books(filter, page, per_page, db)
    total_books = await book_service.count_books(filter, db)

    response.headers['X-Total-Count'] = str(total_books)
    response.headers['X-Total-Pages'] = str(-(-total_books // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return books


@router.get('/all-minimal', response_model=list[schema.BookOutMinimal])
async def get_all_books_minimal(*,
                                page: int = Query(1, ge=1),
                                per_page: int = Query(10, ge=1, le=100),
                                filter: BookFilterMinimal = FilterDepends(
                                    BookFilterMinimal),
                                db: Session,
                                response: Response):
    books = await book_service.get_all_books_minimal(filter, page, per_page, db)
    total_books = await book_service.count_books_minimal(filter, db)

    response.headers['X-Total-Count'] = str(total_books)
    response.headers['X-Total-Pages'] = str(-(-total_books // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return books


@router.post('', response_model=schema.BookOutAdmin, status_code=status.HTTP_201_CREATED)
async def create_book(payload: schema.CreateBook, _: AdminAccessToken, db: Session):
    return await book_service.create_book(payload.model_dump(), db)


@router.post('/bulk', response_model=list[schema.BookOutAdmin], status_code=status.HTTP_201_CREATED)
async def create_book_bulk(payload: list[schema.CreateBook], _: AdminAccessToken, db: Session):
    return await book_service.create_book_bulk([p.model_dump() for p in payload], db)


@router.patch('/{id}', response_model=schema.BookOutAdmin)
async def update_book(id: UUID, payload: schema.UpdateBook, _: AdminAccessToken, db: Session):
    return await book_service.update_book(id, payload.model_dump(exclude_unset=True), db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(id: UUID, _: AdminAccessToken, db: Session):
    await book_service.delete_book(id, db)


@router.get('/export/csv')
async def export_books_to_csv(*,
                              page: int = Query(1, ge=1),
                              per_page: int = Query(1000, ge=1, le=1000),
                              columns: str | None = Query(
                                  None, description='Comma separated list of columns to include in the CSV'),
                              filter: BookFilter = FilterDepends(BookFilter),
                              _: AdminAccessToken,
                              db: Session):
    response = await csv_service.export_books_to_csv(filter, page, per_page, db, columns)
    total_books = await book_service.count_books(filter, db)

    response.headers['X-Total-Count'] = str(total_books)
    response.headers['X-Total-Pages'] = str(-(-total_books // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return response


@router.post('/import/csv')
async def import_books_from_csv(*, file: UploadFile = File(...), _: AdminAccessToken, db: Session):
    return await csv_service.import_books_from_csv(file, db)
