from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Sequence
from uuid import UUID

from app.models import Publisher
import app.pydantic_schema.publisher as publisher_schema
from app.controller.utility import slugify

async def get_publisher_by_id(id: UUID, db: AsyncSession) -> publisher_schema.PublisherOut:
    result = await db.execute(select(Publisher).filter(Publisher.id == id))
    publisher = result.scalar()
    if not publisher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Publisher with id {id} not found')
    return publisher

async def get_publisher_by_slug(slug: str, db: AsyncSession) -> publisher_schema.PublisherOut:
    result = await db.execute(select(Publisher).filter(Publisher.slug == slug))
    return result.scalars().first()

async def get_all_publishers(page: int, per_page:int, db: AsyncSession) -> Sequence[publisher_schema.PublisherOut]:
    offset = (page - 1) * per_page

    result = await db.execute(select(Publisher).offset(offset).limit(per_page))
    return result.scalars().all()

async def create_publisher(payload: publisher_schema.CreatePublisher, db: AsyncSession) -> publisher_schema.PublisherOut:
    publisher = Publisher(**payload.model_dump(exclude_unset=True))
    publisher.slug = await generate_unique_slug(payload.slug, payload.name, db)

    db.add(publisher)
    await db.commit()

    print(publisher.__dict__)

    return publisher_schema.PublisherOut.model_validate(publisher)

async def update_publisher(id: UUID, payload: publisher_schema.UpdatePublisher, db: AsyncSession) -> publisher_schema.PublisherOut:
    publisher = await get_publisher_by_id(id, db)

    data = publisher_schema.UpdatePublisher.model_dump(payload, exclude_unset=True)
    [setattr(publisher, key, value) for key, value in data.items()]

    await db.commit()
    return publisher_schema.PublisherOut.model_validate(publisher)

async def delete_publisher(id: UUID, db: AsyncSession) -> None:
    publisher = await get_publisher_by_id(id, db)
    await db.delete(publisher)
    await db.commit()
    
async def count_publisher(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Publisher))
    return result.scalar_one()

# Additional Function
async def generate_unique_slug(slug: str | None, name: str, db: AsyncSession) -> str:
    slug = slug.replace(
        ' ', '-').lower() if slug else slugify(name)
    result = await db.execute(select(Publisher).filter(Publisher.slug.like(f'{slug}%')))
    existing_book = result.scalars().all()
    return f"{slug}-{len(existing_book)}" if existing_book else slug
