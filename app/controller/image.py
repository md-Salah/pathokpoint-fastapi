from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, Table
from typing import Sequence
from uuid import UUID
import os
import logging
import tempfile
import aiofiles

from app.models.image import Image
from app.controller.exception import NotFoundException, ServerErrorException, BadRequestException
from app.library.cloudinary import upload_file_to_cloudinary, delete_file_from_cloudinary, update_file
from app.constant.image_folder import ImageFolder
from app.library.img_resize import img_resize

logger = logging.getLogger(__name__)


async def get_image_by_id(id: UUID, db: AsyncSession) -> Image:
    image = await db.get(Image, id)
    if not image:
        raise NotFoundException('Image not found', str(id))
    return image


async def get_all_images(page: int, per_page: int, db: AsyncSession) -> Sequence[Image]:
    offset = (page - 1) * per_page
    result = await db.execute(select(Image).offset(offset).limit(per_page))
    return result.scalars().all()


async def count_image(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Image))
    return result.scalar_one()


async def validate_n_resize_image(file: UploadFile) -> str:
    CHUNK_SIZE = 1 * 1024 * 1024

    if file.size is None:
        raise BadRequestException('File size is unknown')
    elif file.size > 2 * CHUNK_SIZE:
        raise BadRequestException('File size should not exceed 2MB')

    try:
        tmp_dir = 'dummy/tmp'
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as temp_file:
            tmp_file = temp_file.name
            async with aiofiles.open(tmp_file, 'wb') as f:
                while chunk := await file.read(CHUNK_SIZE):
                    await f.write(chunk)

            await img_resize(tmp_file, (260, 372), 20)
            return tmp_file
    except Exception as err:
        logger.error(f'Error while uploading image: {err}')
        raise ServerErrorException('Error while uploading image')


async def create_image(file: UploadFile, filename: str | None, alt: str, folder: ImageFolder, db: AsyncSession) -> Image:
    tmp_file = await validate_n_resize_image(file)
    filename = filename or file.filename or ""

    response = await upload_file_to_cloudinary(tmp_file, filename, folder.value)
    os.remove(tmp_file)
    if not response:
        raise ServerErrorException('Image upload failed')

    image = Image(name=filename,
                  src=response['secure_url'], alt=alt, public_id=response['public_id'], folder=folder)
    db.add(image)
    await db.commit()
    return image


async def update_image(id: UUID, file: UploadFile, filename: str | None, alt: str, db: AsyncSession) -> Image:
    image = await db.get(Image, id)
    if not image:
        raise NotFoundException('Image not found', str(id))

    tmp_file = await validate_n_resize_image(file)
    filename = filename or file.filename or ""

    response = await update_file(tmp_file, public_id=image.public_id, filename=filename)
    os.remove(tmp_file)
    if not response:
        raise ServerErrorException('Image upload failed')

    image.public_id = response['public_id']
    image.src = response['secure_url']
    image.name = filename
    image.alt = alt
    await db.commit()
    return image


async def delete_image(id: UUID, db: AsyncSession) -> None:
    image = await get_image_by_id(id, db)
    success = await delete_file_from_cloudinary(image.public_id)
    if not success:
        raise ServerErrorException('Image delete failed')
    await db.delete(image)
    await db.commit()


async def delete_image_bulk(ids: Sequence[UUID], db: AsyncSession) -> None:
    images = (await db.scalars(select(Image).filter(Image.id.in_(ids)))).all()

    for image in images:
        success = await delete_file_from_cloudinary(image.public_id)
        if not success:
            raise ServerErrorException('Image delete failed')

    await db.execute(delete(Image).where(Image.id.in_(ids)))
    await db.commit()


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

        not_found = [id for id in ids if id not in [
            image.id for image in images]]
        if not_found:
            raise NotFoundException(
                'Image not found', ','.join(str(id) for id in not_found))

    to_remove = [id for id in previous_ids if id not in ids]
    if to_remove:
        if isinstance(link_table, Table):
            await db.execute(link_table.delete().where(link_table.c.image_id.in_(previous_ids)))

        await delete_image_bulk(to_remove, db)

    return images


async def detach_images(db: AsyncSession, *ids: UUID | None) -> None:
    image_ids = [id for id in ids if id]
    if image_ids:
        await delete_image_bulk(image_ids, db)
