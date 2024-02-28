from fastapi import APIRouter, status, Depends, Query, Response, UploadFile, File, HTTPException, Path
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Annotated

import app.pydantic_schema.book as schema
from app.config.database import get_db
import app.controller.book as book_service

router = APIRouter()

# GET BOOK BY ID : CUSTOMER
@router.get('/book/id/{id}', response_model=schema.ReadBook)  
async def get_book_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
    return await book_service.get_book_by_id(id, db)

# GET BOOK BY SLUG : CUSTOMER
@router.get('/book/slug/{slug}', response_model=schema.ReadBook) 
async def get_book_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    return await book_service.get_book_by_slug(slug, db)

# GET ALL BOOKS : CUSTOMER
@router.get('/books', response_model=list[schema.ReadBook])  
async def get_all_books(*, page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db),  response: Response):
    books = await book_service.get_all_books(page, per_page, db)
    total_books = await book_service.count_book(db)

    response.headers['X-Total-Count'] = str(total_books)
    response.headers['X-Total-Pages'] = str(-(-total_books // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return books

@router.get('/book/search/{q}', response_model=list[schema.ReadBook])
async def search_books(q: str = Path(..., min_length=3), db: AsyncSession = Depends(get_db)):
    return await book_service.search_books(q, db)

# CREATE BOOK : ADMIN
@router.post('/book', response_model=schema.ReadBook, status_code=status.HTTP_201_CREATED)
async def create_book(payload: schema.CreateBook, db: AsyncSession = Depends(get_db)):
    return await book_service.create_book(payload, db)

# UPDATE BOOK : ADMIN
@router.patch('/book/{id}', response_model=schema.ReadBook) 
async def update_book(id: UUID, payload: schema.UpdateBook, db: AsyncSession = Depends(get_db)):
    return await book_service.update_book(id, payload, db)

# DELETE BOOK : ADMIN
@router.delete('/book/{id}', status_code=status.HTTP_204_NO_CONTENT) 
async def delete_book(id: UUID, db: AsyncSession = Depends(get_db)):
    await book_service.delete_book(id, db)

@router.get('/book/test')
async def test(db: AsyncSession = Depends(get_db)):
    return await book_service.test(db)

# # IMPORT CSV : ADMIN
# @router.post('/book/import-from-csv', response_class=StreamingResponse ,status_code=status.HTTP_201_CREATED)
# def import_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
#     if file.filename and file.filename.endswith('.csv'):
#         csv_stream = book_service.import_book_from_csv(file, db)
#         response = StreamingResponse(iter([csv_stream]), media_type="text/csv")
#         response.headers["Content-Disposition"] = "attachment; filename={}".format(file.filename)
        
#         return response
#     else:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid file format. Please upload a CSV file')
    
    
# # EXPORT TO CSV : ADMIN
# @router.get('/book/export-to-csv', response_class=StreamingResponse)
# def export_to_csv(db: AsyncSession = Depends(get_db)):
#     csv_stream = book_service.export_book_to_csv(db)
#     response = StreamingResponse(iter([csv_stream]), media_type="text/csv")
#     response.headers["Content-Disposition"] = "attachment; filename=books.csv"
    
#     return response

