from fastapi import APIRouter, status, Depends, Query, Response, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID

import app.pydantic_schema.book as schema
from app.config.database import get_db
import app.controller.book as service

router = APIRouter()

# GET BOOK BY ID : CUSTOMER
@router.get('/book/id/{id}', response_model=schema.ReadBook)  
def get_book_by_id(id: UUID, db: Session = Depends(get_db)):
    return service.get_book_by_id(id, db)

# GET BOOK BY SLUG : CUSTOMER
@router.get('/book/slug/{slug}', response_model=schema.ReadBook) 
def get_book_by_slug(slug: str, db: Session = Depends(get_db)):
    return service.get_book_by_slug(slug, db)

# GET ALL BOOKS : CUSTOMER
@router.get('/books', response_model=list[schema.ReadBook])  
def get_all_books(*, page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), db: Session = Depends(get_db),  response: Response):
    books = service.get_all_books(page, per_page, db)
    total_books = service.count_book(db)

    response.headers['X-Total-Count'] = str(total_books)
    response.headers['X-Total-Pages'] = str(-(-total_books // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return books

# CREATE BOOK : ADMIN
@router.post('/book', response_model=schema.ReadBook, status_code=status.HTTP_201_CREATED)
def create_book(payload: schema.CreateBook, db: Session = Depends(get_db)):
    return service.create_book(payload, db)

# UPDATE BOOK : ADMIN
@router.patch('/book/{id}', response_model=schema.ReadBook) 
def update_book(id: UUID, payload: schema.UpdateBook, db: Session = Depends(get_db)):
    return service.update_book(id, payload, db)

# DELETE BOOK : ADMIN
@router.delete('/book/{id}', response_model=schema.ReadBook) 
def delete_book(id: UUID, db: Session = Depends(get_db)):
    return service.delete_book(id, db)

# IMPORT CSV : ADMIN
@router.post('/book/import-from-csv', response_class=StreamingResponse ,status_code=status.HTTP_201_CREATED)
def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.filename and file.filename.endswith('.csv'):
        csv_stream = service.import_book_from_csv(file, db)
        response = StreamingResponse(iter([csv_stream]), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename={}".format(file.filename)
        
        return response
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid file format. Please upload a CSV file')
    
    
# EXPORT TO CSV : ADMIN
@router.get('/book/export-to-csv', response_class=StreamingResponse)
def export_to_csv(db: Session = Depends(get_db)):
    csv_stream = service.export_book_to_csv(db)
    response = StreamingResponse(iter([csv_stream]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=books.csv"
    
    return response

