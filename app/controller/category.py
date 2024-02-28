from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Sequence
from uuid import UUID

from app.models import Category
import app.pydantic_schema.category as category_schema
from app.controller.utility import slugify

async def get_category_by_id(id: UUID, db: AsyncSession) -> category_schema.CategoryOut:
    result = await db.execute(select(Category).filter(Category.id == id))
    category = result.scalar()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Category with id {id} not found')
    return category

async def get_category_by_slug(slug: str, db: AsyncSession) -> category_schema.CategoryOut:
    result = await db.execute(select(Category).filter(Category.slug == slug))
    return result.scalars().first()

async def get_all_categorys(page: int, per_page:int, db: AsyncSession) -> Sequence[category_schema.CategoryOut]:
    offset = (page - 1) * per_page

    result = await db.execute(select(Category).offset(offset).limit(per_page))
    return result.scalars().all()

async def create_category(payload: category_schema.CreateCategory, db: AsyncSession) -> category_schema.CategoryOut:
    category = Category(**payload.model_dump(exclude_unset=True))
    category.slug = await generate_unique_slug(payload.slug, payload.name, db)

    db.add(category)
    await db.commit()

    print(category.__dict__)

    return category_schema.CategoryOut.model_validate(category)

async def update_category(id: UUID, payload: category_schema.UpdateCategory, db: AsyncSession) -> category_schema.CategoryOut:
    category = await get_category_by_id(id, db)

    data = category_schema.UpdateCategory.model_dump(payload, exclude_unset=True)
    [setattr(category, key, value) for key, value in data.items()]

    await db.commit()
    return category_schema.CategoryOut.model_validate(category)

async def delete_category(id: UUID, db: AsyncSession) -> None:
    category = await get_category_by_id(id, db)
    await db.delete(category)
    await db.commit()
    
async def count_category(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Category))
    return result.scalar_one()

# Additional Function
async def generate_unique_slug(slug: str | None, name: str, db: AsyncSession) -> str:
    slug = slug.replace(
        ' ', '-').lower() if slug else slugify(name)
    result = await db.execute(select(Category).filter(Category.slug.like(f'{slug}%')))
    existing_book = result.scalars().all()
    return f"{slug}-{len(existing_book)}" if existing_book else slug
