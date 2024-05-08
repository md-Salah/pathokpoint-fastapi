from starlette.concurrency import run_in_threadpool
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, Table
from typing import Sequence
from uuid import UUID, uuid4
import os
import logging
from typing import Any

from app.models.image import Image
from app.controller.exception import NotFoundException

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
    src = await run_in_threadpool(upload_file_to_cloudinary, file, filename, str(id))
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
    success = await run_in_threadpool(delete_file_from_cloudinary, str(image.id))
    if success:
        await db.delete(image)
        await db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Image delete failed')


async def delete_image_bulk(ids: Sequence[UUID], db: AsyncSession) -> None:
    await db.execute(delete(Image).where(Image.id.in_(ids)))

    for image_id in ids:
        success = await run_in_threadpool(delete_file_from_cloudinary, str(image_id))
        if not success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='Image delete failed')

    await db.commit()


async def count_image(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Image))
    return result.scalar_one()



# Additional functions for attaching and detaching images from other models
async def attach_image(id: UUID | None, previous_id: UUID | None, db: AsyncSession) -> Image | None:
    if previous_id and previous_id != id:
        await delete_image(previous_id, db)
    return await db.get(Image, id) if id else None


async def handle_multiple_image_attachment(ids: list[UUID], previous_ids: list[UUID], db: AsyncSession, link_table: Table | None = None) -> list[Image]:
    images = []
    if ids:
        stmt = select(Image).filter(Image.id.in_(ids))        
        images = list((await db.scalars(stmt)).all())
        
        not_found = [id for id in ids if id not in [image.id for image in images]]
        if not_found:
            raise NotFoundException('Image not found', ','.join(str(id) for id in not_found))
        
    to_remove = [id for id in previous_ids if id not in ids]
    if to_remove:
        if isinstance(link_table, Table):
            await db.execute(link_table.delete().where(link_table.c.image_id.in_(previous_ids)))
        
        await db.execute(delete(Image).where(Image.id.in_(to_remove)))
        for image_id in to_remove:
            success = await run_in_threadpool(delete_file_from_cloudinary, str(image_id))
            if not success:
                logger.error(f'Failed to delete image {image_id}')

    # logger.debug(f'Images found: {images}')
    return images


async def detach_images(db: AsyncSession, *ids: UUID | None) -> None:
    image_ids = [id for id in ids if id]
    if image_ids:
        await delete_image_bulk(image_ids, db)
