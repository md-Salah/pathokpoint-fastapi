from fastapi import APIRouter, Depends, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi_filter import FilterDepends

from app.filter_schema.category import CategoryFilter
from app.config.database import get_db
import app.controller.category as category_service
import app.pydantic_schema.category as category_schema

router = APIRouter(prefix='/category')


@router.get('/id/{id}', response_model=category_schema.CategoryOut)
async def get_category_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
    return await category_service.get_category_by_id(id, db)


@router.get('/slug/{slug}', response_model=category_schema.CategoryOut)
async def get_category_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    return await category_service.get_category_by_slug(slug, db)


@router.get('/all', response_model=list[category_schema.CategoryOut])
async def get_all_categories(*,
                             category_filter : CategoryFilter = FilterDepends(CategoryFilter),
                             page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db),  response: Response):
    categories = await category_service.get_all_categories(page, per_page, db, category_filter)
    total_categories = await category_service.count_category(db, category_filter)

    response.headers['X-Total-Count'] = str(total_categories)
    response.headers['X-Total-Pages'] = str(-(-total_categories // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return categories


@router.post('', response_model=category_schema.CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(payload: category_schema.CreateCategory, db: AsyncSession = Depends(get_db)):
    return await category_service.create_category(payload.model_dump(), db)


@router.patch('/{id}', response_model=category_schema.CategoryOut)
async def update_category(id: UUID, payload: category_schema.UpdateCategory, db: AsyncSession = Depends(get_db)):
    return await category_service.update_category(id, payload.model_dump(exclude_unset=True), db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(id: UUID, db: AsyncSession = Depends(get_db)):
    return await category_service.delete_category(id, db)
