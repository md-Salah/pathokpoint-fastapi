from fastapi import APIRouter, status, Query, Response
from uuid import UUID
from fastapi_filter import FilterDepends

from app.filter_schema.category import CategoryFilter
from app.config.database import Session
import app.controller.category as category_service
import app.pydantic_schema.category as category_schema
from app.controller.auth import AdminAccessToken

router = APIRouter(prefix='/category')


@router.get('/id/{id}', response_model=category_schema.CategoryOut)
async def get_category_by_id(id: UUID, db: Session):
    return await category_service.get_category_by_id(id, db)


@router.get('/slug/{slug}', response_model=category_schema.CategoryOut)
async def get_category_by_slug(slug: str, db: Session):
    return await category_service.get_category_by_slug(slug, db)


@router.get('/all', response_model=list[category_schema.CategoryOut])
async def get_all_categories(*,
                             filter: CategoryFilter = FilterDepends(
                                 CategoryFilter),
                             page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), db: Session,  response: Response):
    categories = await category_service.get_all_categories(filter, page, per_page, db)
    total_categories = await category_service.count_category(filter, db)

    response.headers['X-Total-Count'] = str(total_categories)
    response.headers['X-Total-Pages'] = str(-(-total_categories // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return categories


@router.post('', response_model=category_schema.CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(payload: category_schema.CreateCategory, _: AdminAccessToken, db: Session):
    return await category_service.create_category(payload.model_dump(), db)


@router.patch('/{id}', response_model=category_schema.CategoryOut)
async def update_category(id: UUID, payload: category_schema.UpdateCategory, _: AdminAccessToken, db: Session):
    return await category_service.update_category(id, payload.model_dump(exclude_unset=True), db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(id: UUID, _: AdminAccessToken, db: Session):
    return await category_service.delete_category(id, db)
