from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import Sequence
from uuid import UUID, uuid4
import os
import logging

from app.models.image import Image

from app.library import upload_file_to_cloudinary, delete_file_from_cloudinary

logger = logging.getLogger(__name__)

async def get_image_by_id(id: UUID, db: AsyncSession) -> Image:
    image = await db.get(Image, id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Image with id ({id}) not found')
    return image


async def get_all_images(page: int, per_page: int, db: AsyncSession) -> Sequence[Image]:
    offset = (page - 1) * per_page
    result = await db.execute(select(Image).offset(offset).limit(per_page))
    return result.scalars().all()


async def create_image(file: str, filename: str, alt: str, db: AsyncSession) -> Image:
    id = uuid4()
    src = upload_file_to_cloudinary(file, filename, str(id))
    os.remove(file)

    if not src:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Image upload failed')

    image = Image(id=id, name=filename, src=src, alt=alt)
    db.add(image)
    await db.commit()
    return image


async def delete_image(id: UUID, db: AsyncSession) -> None:
    image = await get_image_by_id(id, db)
    success = delete_file_from_cloudinary(str(image.id))
    if success:
        await db.delete(image)
        await db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Image delete failed')

async def delete_image_bulk(ids: Sequence[UUID], db: AsyncSession) -> None:
    for image_id in ids:
        success = delete_file_from_cloudinary(str(image_id))
        if not success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='Image delete failed')
    
    await db.execute(delete(Image).where(Image.id.in_(ids)))
    await db.commit()

async def count_image(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Image))
    return result.scalar_one()
