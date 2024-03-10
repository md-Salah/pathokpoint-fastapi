from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Sequence
from uuid import UUID

from app.models.tag import Tag


async def get_tag_by_id(id: UUID, db: AsyncSession) -> Tag:
    tag = await db.get(Tag, id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Tag with id ({id}) not found')
    return tag


async def get_all_tags(page: int, per_page: int, db: AsyncSession) -> Sequence[Tag]:
    offset = (page - 1) * per_page
    result = await db.execute(select(Tag).offset(offset).limit(per_page))
    return result.scalars().all()


async def create_tag(payload: dict, db: AsyncSession) -> Tag:
    tag = Tag(**payload)
    db.add(tag)
    await db.commit()
    return tag


async def update_tag(id: UUID, payload: dict, db: AsyncSession) -> Tag:
    tag = await get_tag_by_id(id, db)
    [setattr(tag, key, value)
     for key, value in payload.items()]
    await db.commit()
    return tag


async def delete_tag(id: UUID, db: AsyncSession) -> None:
    tag = await get_tag_by_id(id, db)
    await db.delete(tag)
    await db.commit()


async def count_tag(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Tag))
    return result.scalar_one()
