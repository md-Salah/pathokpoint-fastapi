from fastapi import APIRouter, Depends, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.config.database import get_db
import app.controller.publisher as publisher_service
import app.pydantic_schema.publisher as publisher_schema

router = APIRouter()

# Public: Get Publisher By ID
@router.get('/publisher/id/{id}', response_model=publisher_schema.PublisherOut)
async def get_publisher_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
    return await publisher_service.get_publisher_by_id(id, db)

# Public: Get Publisher By Slug
@router.get('/publisher/slug/{slug}', response_model=publisher_schema.PublisherOut)
async def get_publisher_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    return await publisher_service.get_publisher_by_slug(slug, db)

# Public: Get All Publishers
@router.get('/publishers', response_model=list[publisher_schema.PublisherOut])  
async def get_all_publishers(*, page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), db: AsyncSession = Depends(get_db),  response: Response):
    publishers = await publisher_service.get_all_publishers(page, per_page, db)
    total_publishers = await publisher_service.count_publisher(db)

    response.headers['X-Total-Count'] = str(total_publishers)
    response.headers['X-Total-Pages'] = str(-(-total_publishers // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return publishers

# ADMIN: Create Publisher
@router.post('/publisher', response_model=publisher_schema.PublisherOut, status_code=status.HTTP_201_CREATED)
async def create_publisher(payload: publisher_schema.CreatePublisher, db: AsyncSession = Depends(get_db)):
    return await publisher_service.create_publisher(payload, db)

# ADMIN: Update Publisher
@router.patch('/publisher/{id}', response_model=publisher_schema.PublisherOut)
async def update_publisher(id: UUID, payload: publisher_schema.UpdatePublisher, db: AsyncSession = Depends(get_db)):
    return await publisher_service.update_publisher(id, payload, db)

# ADMIN: Delete Publisher
@router.delete('/publisher/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_publisher(id: UUID, db: AsyncSession = Depends(get_db)):
    return await publisher_service.delete_publisher(id, db)