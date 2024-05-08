from fastapi import APIRouter, status, Query, Response
from uuid import UUID
from fastapi_filter import FilterDepends

from app.config.database import Session
import app.controller.tag as tag_service
import app.pydantic_schema.tag as tag_schema
from app.filter_schema.tag import TagFilter

router = APIRouter(prefix='/tag')


@router.get('/id/{id}', response_model=tag_schema.TagOut)
async def get_tag_by_id(id: UUID, db: Session):
    return await tag_service.get_tag_by_id(id, db)


@router.get('/all', response_model=list[tag_schema.TagOut])
async def get_all_tags(*,
                       filter: TagFilter = FilterDepends(TagFilter),
                       page: int = Query(1, ge=1),
                       per_page: int = Query(10, ge=1, le=100),
                       db: Session,  response: Response):
    tags = await tag_service.get_all_tags(filter, page, per_page, db)
    total_tags = await tag_service.count_tag(filter, db)

    response.headers['X-Total-Count'] = str(total_tags)
    response.headers['X-Total-Pages'] = str(-(-total_tags // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return tags


@router.post('', response_model=tag_schema.TagOut, status_code=status.HTTP_201_CREATED)
async def create_tag(payload: tag_schema.CreateTag, db: Session):
    return await tag_service.create_tag(payload.model_dump(), db)


@router.patch('/{id}', response_model=tag_schema.TagOut)
async def update_tag(id: UUID, payload: tag_schema.UpdateTag, db: Session):
    return await tag_service.update_tag(id, payload.model_dump(exclude_unset=True), db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(id: UUID, db: Session):
    await tag_service.delete_tag(id, db)
