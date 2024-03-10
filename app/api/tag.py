from fastapi import APIRouter, Depends, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.config.database import get_db
import app.controller.tag as tag_service
import app.pydantic_schema.tag as tag_schema

router = APIRouter()


# Permission: Public
@router.get('/tag/id/{id}', response_model=tag_schema.TagOut)
async def get_tag_by_id(id: UUID, db: AsyncSession = Depends(get_db)):
    tag = await tag_service.get_tag_by_id(id, db)
    return tag_schema.TagOut.model_validate(tag)


# Permission: Public
@router.get('/tags', response_model=list[tag_schema.TagOut])
async def get_all_tags(*, page: int = Query(1, ge=1),
                           per_page: int = Query(10, ge=1, le=100),
                           db: AsyncSession = Depends(get_db),  response: Response):
    tags = await tag_service.get_all_tags(page, per_page, db)
    total_tags = await tag_service.count_tag(db)

    response.headers['X-Total-Count'] = str(total_tags)
    response.headers['X-Total-Pages'] = str(-(-total_tags // per_page))
    response.headers['X-Current-Page'] = str(page)
    response.headers['X-Per-Page'] = str(per_page)

    return [tag_schema.TagOut.model_validate(tag) for tag in tags]


# Permission: Admin
@router.post('/tag', response_model=tag_schema.TagOut, status_code=status.HTTP_201_CREATED)
async def create_tag(payload: tag_schema.CreateTag, db: AsyncSession = Depends(get_db)):
    tag = await tag_service.create_tag(payload.model_dump(), db)
    return tag_schema.TagOut.model_validate(tag)


# Permission: Admin
@router.patch('/tag/{id}', response_model=tag_schema.TagOut)
async def update_tag(id: UUID, payload: tag_schema.UpdateTag, db: AsyncSession = Depends(get_db)):
    tag = await tag_service.update_tag(id, payload.model_dump(exclude_unset=True), db)
    return tag_schema.TagOut.model_validate(tag)


# Permission: Admin
@router.delete('/tag/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(id: UUID, db: AsyncSession = Depends(get_db)):
    await tag_service.delete_tag(id, db)
