from fastapi import APIRouter, status, Query, Response
from uuid import UUID
from fastapi_filter import FilterDepends

from app.filter_schema.publisher import PublisherFilter
from app.config.database import Session
import app.controller.publisher as publisher_service
import app.pydantic_schema.publisher as publisher_schema
from app.controller.auth import AdminAccessToken

router = APIRouter(prefix='/publisher')


@router.get('/id/{id}', response_model=publisher_schema.PublisherOut)
async def get_publisher_by_id(id: UUID, db: Session):
    return await publisher_service.get_publisher_by_id(id, db)


@router.get('/slug/{slug}', response_model=publisher_schema.PublisherOut)
async def get_publisher_by_slug(slug: str, db: Session):
    return await publisher_service.get_publisher_by_slug(slug, db)


@router.get('/all', response_model=list[publisher_schema.PublisherOut])
async def get_all_publishers(*,
                             filter: PublisherFilter = FilterDepends(
                                 PublisherFilter),
                             page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), db: Session,  response: Response):
    publishers = await publisher_service.get_all_publishers(filter, page, per_page, db)
    total_publishers = await publisher_service.count_publisher(filter, db)

    response.headers['X-Total-Count'] = str(total_publishers)
    response.headers['X-Total-Pages'] = str(-(-total_publishers // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return publishers


@router.post('', response_model=publisher_schema.PublisherOut, status_code=status.HTTP_201_CREATED)
async def create_publisher(payload: publisher_schema.CreatePublisher, _: AdminAccessToken, db: Session):
    return await publisher_service.create_publisher(payload.model_dump(), db)


@router.patch('/{id}', response_model=publisher_schema.PublisherOut)
async def update_publisher(id: UUID, payload: publisher_schema.UpdatePublisher, _: AdminAccessToken, db: Session):
    return await publisher_service.update_publisher(id, payload.model_dump(exclude_unset=True), db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_publisher(id: UUID, _: AdminAccessToken, db: Session):
    return await publisher_service.delete_publisher(id, db)
