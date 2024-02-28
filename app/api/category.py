from fastapi import APIRouter, Depends, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.config.database import get_db
import app.controller.category as category_service
import app.pydantic_schema.category as category_schema

router = APIRouter()

# Public: Get Category By ID
@router.get('/category/id/{id}', response_model=category_schema.CategoryOut)
async def get_category_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
    return await category_service.get_category_by_id(id, db)

# Public: Get Category By Slug
@router.get('/category/slug/{slug}', response_model=category_schema.CategoryOut)
async def get_category_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    return await category_service.get_category_by_slug(slug, db)

# Public: Get All Categorys
@router.get('/categorys', response_model=list[category_schema.CategoryOut])  
async def get_all_categorys(*, page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db),  response: Response):
    categorys = await category_service.get_all_categorys(page, per_page, db)
    total_categorys = await category_service.count_category(db)

    response.headers['X-Total-Count'] = str(total_categorys)
    response.headers['X-Total-Pages'] = str(-(-total_categorys // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return categorys

# ADMIN: Create Category
@router.post('/category', response_model=category_schema.CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(payload: category_schema.CreateCategory, db: AsyncSession = Depends(get_db)):
    return await category_service.create_category(payload, db)

# ADMIN: Update Category
@router.patch('/category/{id}', response_model=category_schema.CategoryOut)
async def update_category(id: UUID, payload: category_schema.UpdateCategory, db: AsyncSession = Depends(get_db)):
    return await category_service.update_category(id, payload, db)

# ADMIN: Delete Category
@router.delete('/category/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(id: UUID, db: AsyncSession = Depends(get_db)):
    return await category_service.delete_category(id, db)