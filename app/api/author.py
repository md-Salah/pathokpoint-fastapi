from fastapi import APIRouter, Depends, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi_filter import FilterDepends

from app.config.database import get_db
import app.controller.author as author_service
import app.pydantic_schema.author as author_schema
from app.filter_schema.author import AuthorFilter

router = APIRouter(prefix='/author')


@router.get('/id/{id}', response_model=author_schema.AuthorOut)
async def get_author_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
    return await author_service.get_author_by_id(id, db)

@router.get('/slug/{slug}', response_model=author_schema.AuthorOut)
async def get_author_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    return await author_service.get_author_by_slug(slug, db)

@router.get('/all', response_model=list[author_schema.AuthorOut])
async def get_all_authors(*,
                          author_filter: AuthorFilter = FilterDepends(AuthorFilter),
                          page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100),
                          db: AsyncSession = Depends(get_db),
                          response: Response):
    authors = await author_service.get_all_authors(page, per_page, db, author_filter)

    total_result = await author_service.count_author(db, author_filter)
    response.headers['X-Total-Count'] = str(total_result)
    response.headers['X-Total-Pages'] = str(-(-total_result // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return authors


@router.post('', response_model=author_schema.AuthorOut, status_code=status.HTTP_201_CREATED)
async def create_author(payload: author_schema.CreateAuthor, db: AsyncSession = Depends(get_db)):
    return await author_service.create_author(payload.model_dump(), db)


@router.patch('/{id}', response_model=author_schema.AuthorOut)
async def update_author(id: UUID, payload: author_schema.UpdateAuthor, db: AsyncSession = Depends(get_db)):
    return await author_service.update_author(id, payload.model_dump(exclude_unset=True), db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(id: UUID, db: AsyncSession = Depends(get_db)):
    return await author_service.delete_author(id, db)
